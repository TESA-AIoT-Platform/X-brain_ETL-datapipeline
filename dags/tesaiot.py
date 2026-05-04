from airflow import DAG
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from airflow.providers.mongo.hooks.mongo import MongoHook
from airflow.providers.redis.hooks.redis import RedisHook
from airflow.providers.postgres.hooks.postgres import PostgresHook

import pendulum
from datetime import datetime, timedelta, date
import pandas as pd
import json
import requests
from bson import ObjectId

local_tz = pendulum.timezone("Asia/Bangkok")

# -----------------------------
# GLOBAL CONFIG (LOCAL)
# -----------------------------

MONGO_CONN_ID = "mongoAuth"
REDIS_CONN_ID = "redisCon"
POSTGRES_CONN_ID = "postgres_local"

MONGO_DB = "sl-core"
MONGO_COLLECTION = "data-log"

PARQUET_PATH = "/opt/airflow/dags/temp/tesaiot.parquet"


# -----------------------------
# HELPERS
# -----------------------------

def json_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return obj


def check_dateOutOfBound(values):
    if pd.notna(values):
        if (pd.Timestamp.max < values) or (values < pd.Timestamp.min):
            return pd.to_datetime(values.replace(year=(values.year-543)), errors='coerce')
        else:
            return pd.to_datetime(values, errors='coerce')


# -----------------------------
# STEP 1 : CHECK NEW DATA
# -----------------------------

def is_latest_id(**kwargs):

    redis_conn = RedisHook(redis_conn_id=REDIS_CONN_ID).get_conn()
    latestId = redis_conn.get('latestOfTesAIoT')

    mongo = MongoHook(conn_id=MONGO_CONN_ID)
    coll = mongo.get_collection(MONGO_COLLECTION, MONGO_DB)

    latest_record = list(
        coll.find({'type': {'$in':[470001]}}).sort('_id', -1).limit(1)
    )

    if not latest_record:
        return False

    latest_mongo_id = latest_record[0]['_id']

    if latestId:
        return latest_mongo_id > ObjectId(latestId.decode())

    return True


# -----------------------------
# STEP 2 : EXTRACT
# -----------------------------

def get_data(**context):

    redis_conn = RedisHook(redis_conn_id=REDIS_CONN_ID).get_conn()
    mongo = MongoHook(conn_id=MONGO_CONN_ID)

    coll = mongo.get_collection(MONGO_COLLECTION, MONGO_DB)

    latestId = redis_conn.get('latestOfTesAIoT')
    limit_row = 100

    query = {'type': {'$in':[470001]}}

    if latestId:
        query['_id'] = {'$gt': ObjectId(latestId.decode())}

    cursor = coll.find(query).sort('_id',1).limit(limit_row)

    df = pd.DataFrame(list(cursor)).reset_index(drop=True)

    if df.empty:
        print("No new data")
        return

    # FIX ObjectId
    df['_id'] = df['_id'].astype(str)

    # FIX nested dict
    df['data'] = df['data'].apply(
        lambda x: json.dumps(x, default=json_serializer) if isinstance(x, dict) else None
    )

    for col in ['ts','crt','mdt']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce').dt.tz_localize(None)

    df.to_parquet(PARQUET_PATH, engine="pyarrow", index=False)

    context['ti'].xcom_push(key='path', value=PARQUET_PATH)


# -----------------------------
# STEP 3 : VALIDATE
# -----------------------------

def check_all_nan(**context):

    ti = context['ti']
    path = ti.xcom_pull(task_ids='task_1_get_mongo', key='path')

    data = pd.read_parquet(path)

    redis_conn = RedisHook(redis_conn_id=REDIS_CONN_ID).get_conn()

    redis_conn.set('latestOfTesAIoT', data['_id'].iloc[-1])

    return not (data['crt'].isna().all() and data['mdt'].isna().all())


# -----------------------------
# STEP 4 : LOAD POSTGRES
# -----------------------------

def load_data(**context):

    ti = context['ti']
    path = ti.xcom_pull(task_ids='task_1_get_mongo', key='path')

    df = pd.read_parquet(path)

    postgres = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)

    engine = postgres.get_sqlalchemy_engine()

    df.columns = [c.lower() for c in df.columns]

    df.to_sql(
        name='tesaiot',
        con=engine,
        if_exists='append',
        index=False,
        method='multi',
        chunksize=50
    )

    redis_conn = RedisHook(redis_conn_id=REDIS_CONN_ID).get_conn()
    redis_conn.set('latestOfTesAIoT', df['_id'].iloc[-1])


# -----------------------------
# ALERT
# -----------------------------

def slack_alert(context):

    slack_webhook_url = "YOUR_WEBHOOK"

    message = {
        "text": f"🚨 Task Failed {context['task_instance'].task_id}"
    }

    requests.post(slack_webhook_url, json=message)


# -----------------------------
# DAG
# -----------------------------

default_args = {
    'owner': 'zg',
    'start_date': datetime.strptime(datetime.now().strftime('%Y-%m-%d 00:00'),'%Y-%m-%d 00:00').replace(tzinfo=local_tz),
    'retry_delay': timedelta(seconds=5)
}

with DAG(
    'collects_tesaiot',
    default_args=default_args,
    schedule=timedelta(minutes=3),
    catchup=False,
    tags=['mongo','postgres','tesaiot']
) as dag:

    is_latest = ShortCircuitOperator(
        task_id='is_latest',
        python_callable=is_latest_id
    )

    task_1 = PythonOperator(
        task_id='task_1_get_mongo',
        python_callable=get_data,
        on_failure_callback=slack_alert
    )

    task_check_nan = ShortCircuitOperator(
        task_id='check_nan_values',
        python_callable=check_all_nan
    )

    task_2 = PythonOperator(
        task_id='task_2_load_postgres',
        python_callable=load_data,
        on_failure_callback=slack_alert
    )

    is_latest >> task_1 >> task_check_nan >> task_2
