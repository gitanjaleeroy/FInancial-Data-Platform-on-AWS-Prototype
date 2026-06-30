# FInancial-Data-Platform-on-AWS-Prototype
This is a prototype of ingesting files from sources into S3, event driven by Amazon EventBridge, ETL by AWS Glue and ready-to-consume datasets in Redshift. Use AWS Step Functions to orchestrate the pipeline.

1.	Built an end-to-end AWS data lake that ingests trade files into Amazon S3 and automatically processes newly arriving files.
2.	Used AWS Glue Crawlers and Glue ETL Jobs to identify schema in files and convert files into partitioned Parquet datasets while supporting automatic incremental processing after an initial full load.
3.	Loaded processed data into Amazon RDS (PostgreSQL) and Amazon Redshift for analytics, with Athena used to query raw S3 data through the Glue Data Catalog.
4.	Implemented two orchestration approaches: EventBridge → Lambda → Step Functions and EventBridge → Lambda, both fully automating the ETL workflow. Also tried to add a bit of Amazon MWAA (Airflow) to do the same orchestration as of Step Functions to compare results.
5.	Used Docker, Amazon ECR, IAM roles, CloudWatch, EC2, and partitioned S3 storage to build a scalable, production-style serverless data engineering pipeline.

