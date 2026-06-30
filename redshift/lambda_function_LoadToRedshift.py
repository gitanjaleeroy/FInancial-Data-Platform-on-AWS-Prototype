import boto3
import time
import os

client = boto3.client("redshift-data")

CLUSTER = os.environ["CLUSTER_ID"]
DATABASE = os.environ["DATABASE"]
DB_USER = os.environ["DB_USER"]
IAM_ROLE = os.environ["IAM_ROLE"]
S3_PATH = os.environ["S3_PATH"]


def execute_sql(sql):
    response = client.execute_statement(
        ClusterIdentifier=CLUSTER,
        Database=DATABASE,
        DbUser=DB_USER,
        Sql=sql
    )
    return response["Id"]


def wait_for_completion(stmt_id):
    while True:
        desc = client.describe_statement(Id=stmt_id)
        status = desc["Status"]

        if status in ["FINISHED", "FAILED", "ABORTED"]:
            if status != "FINISHED":
                raise Exception(f"SQL failed: {desc}")
            return
        time.sleep(2)


def run(sql):
    stmt_id = execute_sql(sql)
    wait_for_completion(stmt_id)


def lambda_handler(event, context):

    load_type = event.get("load_type", "INCREMENTAL")

    # -----------------------
    # FULL LOAD
    # -----------------------
    if load_type == "FULL":

        sqls = [
            "TRUNCATE staging_trades;",

            f"""
            COPY staging_trades
            FROM '{S3_PATH}'
            IAM_ROLE '{IAM_ROLE}'
            FORMAT AS PARQUET;
            """,

            "INSERT INTO trades SELECT * FROM staging_trades;",

            "INSERT INTO etl_control VALUES ('FULL_LOAD','FULL');"
        ]

    # -----------------------
    # INCREMENTAL LOAD
    # -----------------------
    else:

        sqls = [
            "TRUNCATE staging_trades;",

            f"""
            COPY staging_trades
            FROM '{S3_PATH}'
            IAM_ROLE '{IAM_ROLE}'
            FORMAT AS PARQUET;
            """,

            """
            MERGE INTO trades t
            USING staging_trades s
            ON t.trade_id = s.trade_id

            WHEN MATCHED THEN UPDATE SET
                xid = s.xid,
                price = s.price,
                quantity = s.quantity,
                timestamp_eastern = s.timestamp_eastern,
                order_value = s.order_value,
                yyyymmdd = s.yyyymmdd

            WHEN NOT MATCHED THEN INSERT (
                trade_id, xid, price, quantity,
                timestamp_eastern, order_value, yyyymmdd
            )
            VALUES (
                s.trade_id, s.xid, s.price, s.quantity,
                s.timestamp_eastern, s.order_value, s.yyyymmdd
            );
            """,

            "INSERT INTO etl_control VALUES ('INCREMENTAL','INCREMENTAL');"
        ]

    for sql in sqls:
        run(sql)

    return {
        "status": "SUCCESS",
        "load_type": load_type
    }