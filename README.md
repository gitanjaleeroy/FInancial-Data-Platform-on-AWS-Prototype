# Financial Data Platform on AWS (Prototype)

An end-to-end AWS data engineering pipeline that ingests financial trade data, performs event-driven ETL processing, and delivers analytics-ready datasets using modern AWS services.

## 🚀 Overview

This project demonstrates a production-style, serverless data platform capable of:

- Automatically ingesting trade files into Amazon S3
- Triggering ETL workflows through Amazon EventBridge
- Transforming raw CSV files into partitioned Parquet datasets using AWS Glue
- Supporting both full and incremental data processing
- Loading curated datasets into Amazon RDS PostgreSQL and Amazon Redshift
- Querying raw data directly with Amazon Athena
- Comparing Step Functions and Amazon MWAA (Airflow) for orchestration

---

# 🏗️ Architecture

```text
                 Local Laptop
                      │
      synthetic_data.py generates CSV files
                      │
                      ▼
       transferRealtime.py monitors folder
                      │
                      ▼
              Amazon S3 (Raw Zone)
                 s3://bucket/raw/
                      │
          Amazon EventBridge Trigger
                      │
        ┌─────────────┴─────────────┐
        │                           │
        ▼                           ▼
 AWS Step Functions          Amazon MWAA
        │                    (Airflow DAG)
        └─────────────┬─────────────┘
                      ▼
               AWS Glue ETL Job
                      │
           CSV → Partitioned Parquet
                      │
             Glue Job Bookmarks
            (Incremental Processing)
                      │
                      ▼
        Amazon S3 Processed Zone
 processed/trades/year=YYYY/month=MM/day=DD/
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
    Amazon Athena          Lambda Loader
                                   │
                                   ▼
                      Amazon RDS PostgreSQL
                                   │
                                   ▼
                          Amazon Redshift
                                   │
                                   ▼
                               Analytics
```

---

# ✨ Features

- Event-driven architecture using Amazon EventBridge
- Fully automated ETL with AWS Glue
- Incremental processing using Glue Job Bookmarks
- CSV to Parquet conversion
- Partitioned data lake design
- Athena querying via Glue Data Catalog
- Containerized Lambda functions
- Data loading into PostgreSQL and Redshift
- Two orchestration implementations:
  - AWS Step Functions
  - Amazon MWAA (Apache Airflow)

---

# 🛠️ Technology Stack

| Category | Technology |
|-----------|------------|
| Storage | Amazon S3 |
| Metadata | AWS Glue Data Catalog |
| ETL | AWS Glue (Spark) |
| Query Engine | Amazon Athena |
| Database | Amazon RDS PostgreSQL |
| Data Warehouse | Amazon Redshift |
| Compute | AWS Lambda |
| Orchestration | AWS Step Functions, Amazon MWAA |
| Eventing | Amazon EventBridge |
| Containers | Docker, Amazon ECR |
| Monitoring | Amazon CloudWatch |
| Networking | VPC, Security Groups |
| Compute Instance | Amazon EC2 |

---

# 📈 Pipeline Workflow

## 1. Data Generation

**`synthetic_data.py`**

- Generates synthetic financial trade CSV files.

---

## 2. Real-Time Ingestion

**`transferRealtime.py`**

- Monitors a local directory
- Automatically uploads new files to:

```
S3/raw/
```

Runs automatically at Windows startup.

---

## 3. Metadata Discovery

```
S3 Raw
   │
   ▼
Glue Crawler
   │
   ▼
Glue Data Catalog
   │
   ▼
Amazon Athena
```

Allows SQL queries directly against raw data stored in S3.

---

## 4. ETL Processing

AWS Glue performs:

```
CSV
 │
 ▼
Cleaning
 │
 ▼
Transformation
 │
 ▼
Deduplication
 │
 ▼
Parquet
```

Output structure:

```
processed/
└── trades/
    ├── year=YYYY/
    ├── month=MM/
    └── day=DD/
```

---

## 5. Incremental Processing

Uses **Glue Job Bookmarks** to automatically process only new files.

| Run | Behavior |
|------|----------|
| First Execution | Full Load |
| Subsequent Runs | Incremental Load |

No custom Spark tracking logic is required.

---

## 6. Database Loading

Containerized AWS Lambda:

```
Parquet
   │
   ▼
Read
   │
   ▼
Insert
   │
   ▼
Amazon RDS PostgreSQL
```

Supports both:

- Full loads
- Incremental loads

---

# ⚙️ Orchestration

## Option 1 — AWS Step Functions

```
S3 Upload
     │
     ▼
Amazon EventBridge
     │
     ▼
Lambda
     │
     ▼
Step Functions
     │
     ▼
Glue Job
     │
     ▼
Lambda
     │
     ▼
Amazon RDS
```

---

## Option 2 — Amazon MWAA (Airflow)

```
S3 Upload
     │
     ▼
Amazon EventBridge
     │
     ▼
Lambda
     │
     ▼
MWAA Airflow DAG
     │
     ▼
Glue Job
     │
     ▼
Lambda
     │
     ▼
Amazon RDS
```

---

# 📊 Key Concepts Demonstrated

- Data Lake Architecture
- Event-Driven Processing
- Serverless ETL
- Incremental Data Pipelines
- Data Partitioning
- Metadata Management
- Workflow Orchestration
- Infrastructure for Analytics
- Production-style AWS Data Engineering

---

# 🎯 Project Goal

This prototype demonstrates how modern AWS services can be combined to build an automated, scalable, event-driven financial data platform capable of ingesting, transforming, and serving analytics-ready datasets with minimal operational overhead.