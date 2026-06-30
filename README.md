# FInancial-Data-Platform-on-AWS-Prototype
This is a prototype of ingesting files from sources into S3, event driven by Amazon EventBridge, ETL by AWS Glue and ready-to-consume datasets in Redshift. Use AWS Step Functions to orchestrate the pipeline.

1.	Built an end-to-end AWS data lake that ingests trade files into Amazon S3 and automatically processes newly arriving files.
2.	Used AWS Glue Crawlers and Glue ETL Jobs to identify schema in files and convert files into partitioned Parquet datasets while supporting automatic incremental processing after an initial full load.
3.	Loaded processed data into Amazon RDS (PostgreSQL) and Amazon Redshift for analytics, with Athena used to query raw S3 data through the Glue Data Catalog.
4.	Implemented two orchestration approaches: EventBridge → Lambda → Step Functions and EventBridge → Lambda, both fully automating the ETL workflow. Also tried to add a bit of Amazon MWAA (Airflow) to do the same orchestration as of Step Functions to compare results.
5.	Used Docker, Amazon ECR, IAM roles, CloudWatch, EC2, and partitioned S3 storage to build a scalable, production-style serverless data engineering pipeline.

Overall Architecture
                  Local Laptop
                        │
          synthetic_data.py creates files
                        │
                        ▼
           transferRealtime.py watches folder
                        │
                        ▼
                  Amazon S3 Raw Zone
                  s3://bucket/raw/
                        │
             EventBridge detects upload
                        │
         ┌──────────────┴───────────────┐
         │                              │
         ▼                              ▼
 Option 1                        Option 2
 Step Functions                 MWAA Airflow
         │                              │
         └──────────────┬───────────────┘
                        ▼
                 AWS Glue ETL Job
                        │
             CSV → Parquet Conversion
                        │
         Job Bookmark = Incremental Load
                        │
                        ▼
         S3 Processed (Partitioned Parquet)
 processed/trades/year=YYYY/month=MM/day=DD/
                        │
        ┌───────────────┴────────────────┐
        ▼                                ▼
     Amazon Athena                 Lambda Loader
 (Query S3 directly)                     │
                                         ▼
                             Amazon RDS PostgreSQL
                                         │
                                         ▼
                                 Amazon Redshift
                                         │
                                         ▼
                                   Analytics
________________________________________
Technologies Used
Category	Services
Storage	Amazon S3
Metadata	Glue Data Catalog
ETL	AWS Glue (Spark)
Query	Athena
Database	Amazon RDS PostgreSQL
Data Warehouse	Amazon Redshift
Compute	AWS Lambda
Orchestration	Step Functions, Amazon MWAA (Airflow)
Eventing	Amazon EventBridge
Container	Docker, Amazon ECR
Monitoring	CloudWatch
Networking	VPC, Security Groups
Compute Instance	EC2
________________________________________
Pipeline Stages
Stage 1 – Data Generation
synthetic_data.py
Creates synthetic trade CSV files.
________________________________________
Stage 2 – Real-time Ingestion
transferRealtime.py
•	Watches local folder
•	Automatically uploads files to
S3/raw/
Runs automatically at Windows startup using a batch file.
________________________________________
Stage 3 – Metadata Discovery
Glue Crawler
S3/raw
       ↓
Glue Catalog
       ↓
Athena
Allows SQL querying directly on S3.
________________________________________
Stage 4 – ETL
Glue Job
CSV
   ↓
Clean
   ↓
Transform
   ↓
Deduplicate
   ↓
Parquet
Output:
processed/trades/
year=YYYY/
month=MM/
day=DD/
________________________________________
Stage 5 – Incremental Processing
Uses
Glue Job Bookmarks
which automatically remember which S3 files have already been processed.
Result:
•	First run → Full Load
•	Later runs → Incremental only
No custom Spark logic required.
________________________________________
Stage 6 – Database Load
Container-based Lambda
Parquet
    ↓
Read
    ↓
Insert
    ↓
Amazon RDS
Supports
•	Full Load
•	Incremental Load
using Lambda test events.
________________________________________
Stage 7 – Orchestration Option 1
S3 Upload
      ↓
EventBridge
      ↓
Lambda
      ↓
Step Functions
      ↓
Glue Job
      ↓
Lambda
      ↓
RDS
________________________________________
Stage 8 – Orchestration Option 2
S3 Upload
      ↓
EventBridge
      ↓
Lambda
      ↓
MWAA Airflow DAG
      ↓
Glue Job
      ↓
Lambda
      ↓
RDS


