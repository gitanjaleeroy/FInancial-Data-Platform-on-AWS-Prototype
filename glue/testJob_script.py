import sys
import logging
import re
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from pyspark.sql.functions import coalesce,col, lit, greatest, from_utc_timestamp
from awsglue.job import Job

# -----------------------------
# Read job parameters
# -----------------------------
args = getResolvedOptions(sys.argv, [
    'JOB_NAME',
    'input_path'
])

input_path = args['input_path']

# Optional mode handling
# This is not needed as Glue bookmark handles mode full load vs incremental load
mode = "incremental"
if '--mode' in sys.argv:
    mode = sys.argv[sys.argv.index('--mode') + 1]

# -------------------------------------------------
# Extract yyyymmdd from S3 path
# Example:
# s3://bucket/raw/yyyymmdd=20260512/file.csv
# -------------------------------------------------
match = re.search(r'yyyymmdd=(\d+)', input_path)

if not match:
    raise Exception(
        f"Could not extract yyyymmdd from path: {input_path}"
    )

yyyymmdd_value = match.group(1)


# -----------------------------
# Initialize
# -----------------------------
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

job.init(args['JOB_NAME'], args)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("glue-job")
logger.info(f"Job started with mode={mode}")
logger.info(f"Input path: {input_path}")
logger.info(f"Extracted yyyymmdd: {yyyymmdd_value}")

# -----------------------------
# Load data (FULL vs INCREMENTAL)
# -----------------------------
logger.info(f"Running {mode} load...")
# Load raw data
#source_dyf = glueContext.create_dynamic_frame.from_catalog(
#    database="rawfinal_db",
#    table_name="raw",
#    transformation_ctx="source"
#)
source_dyf = glueContext.create_dynamic_frame.from_options(
    connection_type="s3",
    connection_options={
        "paths": [input_path]
    },
    format="csv",
    format_options={
        "withHeader": True,
        "separator": ","
    }
)

# -----------------------------
# If no new files → exit
# -----------------------------
if source_dyf.toDF().limit(1).count() == 0:
    logger.info("No new data detected. Exiting gracefully without processing.")
else:
    df = source_dyf.toDF()

    # -----------------------------
    # Transformations
    # -----------------------------
    df = df.dropna()
    logger.info("Dropped null values")
    
    #Convert UTC timestamp to Eastern
    df_clean = df \
        .withColumn("timestamp_Eastern", from_utc_timestamp(col("timestamp"), "America/New_York")) \
        .withColumnRenamed("symbol", "xid")
    
    logger.info("Timestamp converted to America/New_York and column renamed")

    # -------------------------------------------------
    # Add yyyymmdd partition column
    # -------------------------------------------------
    df_clean = df_clean.withColumn(
        "yyyymmdd",
        lit(yyyymmdd_value)
    )

    
    df_transformed = df_clean.withColumn(
        "order_value",
        greatest(
            lit(10000),
            coalesce(col("price"), lit(0)) * coalesce(col("quantity"), lit(0))
        )
    )

    df_transformed = df_transformed[[
    "trade_id",
    "xid",
    "price",
    "quantity",
    "timestamp_eastern",
    "order_value",
    "yyyymmdd"
]]
    
    logger.info("Calculated 'order_value' column")
    
    # -----------------------------
    # DEDUPLICATION (CRITICAL FIX)
    # -----------------------------
    # Replace "trade_id" with your real unique key
    if "trade_id" in df_transformed.columns:
        df_transformed = df_transformed.dropDuplicates(["trade_id"])
        logger.info("Deduplicated using trade_id")
        
    # -----------------------------
    # Write to processed S3
    # -----------------------------
    logger.info(f"Writing data to S3")
    
    #Write the data
    df_transformed.write \
        .mode("append") \
        .partitionBy("yyyymmdd") \
        .parquet("s3://test-gitanjaleeroy/processed/")
        
    logger.info("Job completed successfully.")
    
# -----------------------------
# Commit job (IMPORTANT for bookmarks)
# -----------------------------
job.commit()
logger.info("Job committed successfully")
