# 📊 Airflow Data Pipeline - DAG Collection

This repository contains multiple Apache Airflow DAGs designed for data ingestion, transformation, monitoring, and notification workflows.

Primary goal:

👉 Build modular data pipelines that support local development and TESAIoT production deployment.

---

# 📁 Project Structure

```
dags/
│
├── tesaiot.py
├── api_to_postgres_dag.py
├── demo_retry_alert.py
└── line_notify.py
```

---

# 🚀 Overview of DAGs

---

## 1️⃣ tesaiot.py

### Purpose

Incremental data pipeline for ingesting IoT data from MongoDB into PostgreSQL using Redis as offset storage.

This DAG:

* Extracts data from MongoDB (TESAIoT data-log collection)
* Performs cleansing and transformation
* Saves intermediate data as Parquet
* Loads data into PostgreSQL
* Uses Redis to track latest processed record (_id)

---

### Data Pipeline Flow

```
is_latest
     ↓
task_1_get_mongo
     ↓
check_nan_values
     ↓
task_2_load_postgres
```

---

### Flow Description

#### ✅ Step 1 — Check new data

* Reads latest processed `_id` from Redis
* Checks MongoDB for newer records
* Skip downstream tasks if no new data

---

#### ✅ Step 2 — Extract and Clean

* Pull incremental data from MongoDB
* Convert ObjectId → string
* Normalize datetime
* Convert nested JSON into JSON string
* Save as parquet:

```
/opt/airflow/dags/temp/tesaiot.parquet
```

---

#### ✅ Step 3 — Validate

* Check if important fields contain only NaN
* Update Redis offset

---

#### ✅ Step 4 — Load

* Append data into PostgreSQL table `tesaiot`

---

## Architecture

```
MongoDB → Airflow → Parquet → PostgreSQL
                 ↓
               Redis (offset tracking)
```

---

# ⚙️ Airflow UI Configuration

Navigate:

```
Airflow UI → Admin → Connections
```

---

## MongoDB Connection

```
Conn Id: mongoAuth
Conn Type: MongoDB

Host: localhost
Port: 27017
Login: airflow
Password: xxxx
Schema: sl-core
```

---

## PostgreSQL Connection

```
Conn Id: postgres_local
Conn Type: Postgres

Host: localhost
Port: 5432
Schema: postgres
Login: airflow
Password: airflow
```

---

## Redis Connection

```
Conn Id: redisCon
Conn Type: Redis

Host: localhost
Port: 6379
```

---

# 🔄 Switching to TESAIoT Production Environment

This DAG is designed to support multiple environments without changing code.

To connect to TESAIoT infrastructure:

1. Go to Airflow UI → Connections
2. Modify existing connection values:

### MongoDB

Change:

```
Host → TESAIoT Mongo IP
Port → custom port
Login/Password → TESAIoT credentials
```

---

### PostgreSQL

Change:

```
Host → TESAIoT Postgres IP
Port → TESAIoT port
Database → TESAIoT DB
```

---

### Redis

Change:

```
Host → TESAIoT Redis instance
```

No DAG code changes required.

---

# 🧪 Additional DAG Files

---

## 2️⃣ api_to_postgres_dag.py

### Purpose

Example ETL pipeline for extracting data from external API and storing into PostgreSQL.

### Workflow

1. Extract data from:

```
https://www.worldometers.info/coronavirus/
```

2. Clean and transform data
3. Automatically create PostgreSQL table
4. Insert processed records

---

### Use Case

* External data ingestion
* Automated table creation
* API-based ETL pattern
* Example for future API pipelines

---

## 3️⃣ demo_retry_alert.py

### Purpose

Demonstrate Airflow retry and failure callback mechanisms.

### Callback Functions

```python
def retry_callback(context):
    logging.info(f"{context}")
    logging.error("Cannot call API at this moment. Wait for retrying..")

def failure_callback(context):
    logging.info(f"{context}")
    logging.error("Cannot call API. Plase contact the admin.")
```

Simulated failure:

```python
def _get_data_from_api():
    raise ValueError()
```

---

### Use Case

* Monitoring workflow
* Custom alert logic
* Error handling design

---

## 4️⃣ line_notify.py

### Purpose

Daily air quality monitoring pipeline.

Workflow:

1. Fetch PM2.5 data from:

```
https://aqicn.org/city/bangkok/th/
```

2. Send alert to LINE Notify API

Schedule:

```
Every day at 08:00
```

---

### Use Case

* Environmental monitoring
* Scheduled notifications
* Integration with messaging platforms

---

# 🧩 Developer Notes

### Local Development

Ensure services running:

* Airflow
* MongoDB
* PostgreSQL
* Redis

---

### Recommended Setup

Use Docker Compose environment for consistency.

---

### Best Practices Used

* Airflow Hooks instead of hardcoded credentials
* Incremental processing via Redis offset
* Data validation before load
* Modular DAG design

---

# 📌 Summary

This repository demonstrates production-style Airflow pipelines including:

* Incremental IoT ingestion
* API-based ETL
* Retry and failure callbacks
* Scheduled notification workflows

Designed to run locally and easily migrate to TESAIoT infrastructure.
