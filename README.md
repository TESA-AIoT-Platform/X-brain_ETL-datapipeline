# 🎓 Airflow Data Pipeline

> 🇹🇭 ตัวอย่างการสร้าง Apache Airflow Data Pipeline แบบ Local Environment สำหรับการพัฒนา ทดสอบ และทดลอง workflow orchestration
> 🇬🇧 Example project demonstrating a local Apache Airflow data pipeline environment for development, testing, and workflow orchestration.

---

# 🎯 Objectives

## 🇹🇭

โปรเจกต์นี้ช่วยให้คุณ:

* รัน Apache Airflow แบบ Local ด้วย Docker
* สร้าง data pipeline workflow
* ทดลอง DAG development
* ใช้ LocalExecutor สำหรับ single-node orchestration
* เชื่อมต่อ PostgreSQL metadata database

## 🇬🇧

This project enables:

* Running Apache Airflow locally via Docker
* Developing DAG-based data pipelines
* Testing workflow orchestration
* Using LocalExecutor for single-node execution
* PostgreSQL-backed metadata storage

---

# 🧭 Architecture Overview

```
+---------------------+
|  Developer Machine  |
+----------+----------+
           |
           v
+---------------------+
| Docker Environment  |
|                     |
|  Airflow Webserver  |
|  Airflow Scheduler  |
|  PostgreSQL DB      |
+---------------------+
```

---

# 📂 Project Structure

```
airflow-data-pipeline/
├── docker-compose.yml
├── dags/
├── plugins/
├── requirements.txt
└── README.md
```

---

# 🚀 Quick Start

---

## 1️⃣ Start Services

```bash
docker compose up -d
```

---

## 2️⃣ Access Airflow UI

```
http://localhost:8080
```

---

## 3️⃣ Default Components

* Webserver → UI access
* Scheduler → DAG execution
* PostgreSQL → metadata database

---

# 🧪 Local Development Workflow

## 🇹🇭

1. เพิ่ม DAG ในโฟลเดอร์ `dags/`
2. reload หน้า Airflow UI
3. enable DAG
4. trigger run

## 🇬🇧

1. Add DAG files into `dags/`
2. Refresh Airflow UI
3. Enable DAG
4. Trigger execution

---

# 🔐 Environment Configuration

Key environment variables:

```
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
```

---

# 📦 Python Environment (Optional Local Dev)

## Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 🧩 Development Guidelines

## DAG Development

* Keep tasks modular
* Use retry policies
* Avoid long blocking tasks

## Project Organization

Suggested structure:

```
func/
  __init__.py
  constants.py
  settings/
  definitions.py
```

---

# 🧪 Expected Result

* Airflow UI accessible
* DAGs visible in dashboard
* Scheduler executing tasks

---

# 🎯 Recommended Next Steps

1. Create example DAG
2. Add external data source integration
3. Implement ETL workflow
4. Add monitoring and logging

---

<div align="center">

Local Development Environment
Apache Airflow

</div>