FROM apache/airflow:3.1.8

# มั่นใจว่าอยู่ใน Folder หลักของ Airflow
WORKDIR /opt/airflow

# คัดลอกเฉพาะไฟล์ที่จำเป็น
COPY requirements.txt . 

# ติดตั้ง Library ในฐานะ User airflow
USER airflow
RUN pip install --no-cache-dir -r requirements.txt