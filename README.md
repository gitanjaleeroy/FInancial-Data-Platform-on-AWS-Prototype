# Financial Data Platform on AWS (Prototype)

An end-to-end AWS data engineering pipeline that ingests financial trade data, performs event-driven ETL processing, and delivers analytics-ready datasets using modern AWS services.

## 

## Overview

1\.	Built an end-to-end AWS data lake that ingests trade files into Amazon S3 and automatically processes newly arriving files.

2\.	Used AWS Glue Crawlers and Glue ETL Jobs to identify schema in files and convert files into partitioned Parquet datasets while supporting automatic incremental processing after an initial full load.

3\.	Loaded processed data into Amazon RDS (PostgreSQL) and Amazon Redshift for analytics, with Athena used to query raw S3 data through the Glue Data Catalog.

4\.	Implemented two orchestration approaches: EventBridge → Lambda → Step Functions and EventBridge → Lambda, both fully automating the ETL workflow. Also tried to add a bit of Amazon MWAA (Airflow) to do the same orchestration as of Step Functions to compare results.

5\.	Used Docker, Amazon ECR, IAM roles, CloudWatch, EC2, and partitioned S3 storage to build a scalable, production-style serverless data engineering pipeline.

\---

# Architecture

```text
                 Local Laptop
                      │
      synthetic\_data.py generates CSV files
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

# Technology Stack

|Category|Technology|
|-|-|
|Storage|Amazon S3|
|Metadata|AWS Glue Data Catalog|
|ETL|AWS Glue (Spark)|
|Query Engine|Amazon Athena|
|Database|Amazon RDS PostgreSQL|
|Data Warehouse|Amazon Redshift|
|Compute|AWS Lambda|
|Orchestration|AWS Step Functions, Amazon MWAA|
|Eventing|Amazon EventBridge|
|Containers|Docker, Amazon ECR|
|Monitoring|Amazon CloudWatch|
|Networking|VPC, Security Groups|
|Compute Instance|Amazon EC2|

\---

# 📈 Pipeline Workflow

## 1\. Data Generation

**`synthetic\_data.py`**

* Generates synthetic financial trade CSV files.

\---

## 2\. Real-Time Ingestion

**`transferRealtime.py`**

* Monitors a local directory
* Automatically uploads new files to:

```
S3/raw/
```

Runs automatically at Windows startup.

\---

## 3\. Metadata Discovery

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

\---

## 4\. ETL Processing

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

\---

## 5\. Incremental Processing

Uses **Glue Job Bookmarks** to automatically process only new files.

|Run|Behavior|
|-|-|
|First Execution|Full Load|
|Subsequent Runs|Incremental Load|

No custom Spark tracking logic is required.

\---

## 6\. Database Loading

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

* Full loads
* Incremental loads

\---

# Orchestration

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

\---

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

\---

