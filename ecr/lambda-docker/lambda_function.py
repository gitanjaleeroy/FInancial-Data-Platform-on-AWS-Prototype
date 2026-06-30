import boto3
import psycopg2
import pandas as pd
import os

from io import BytesIO
from psycopg2.extras import execute_values

s3 = boto3.client("s3")

DB_HOST = os.environ["DB_HOST"]
DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]

BUCKET = os.environ["S3_BUCKET"]
PREFIX = os.environ["S3_PREFIX"]


def connect_db():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=5432
    )


def get_s3_files():
    response = s3.list_objects_v2(
        Bucket=BUCKET,
        Prefix=PREFIX
    )

    return [
        obj["Key"]
        for obj in response.get("Contents", [])
        if obj["Key"].endswith(".parquet")
    ]


def get_processed_files(conn):

    query = """
    SELECT file_name
    FROM etl_control
    """

    with conn.cursor() as cur:
        cur.execute(query)

        rows = cur.fetchall()

    return set(row[0] for row in rows)

def mark_file_processed(conn, file_name):
handler

    query = """
    INSERT INTO etl_control(file_name)
    VALUES (%s)
    ON CONFLICT DO NOTHING
    """

    with conn.cursor() as cur:
        cur.execute(query, (file_name,))

    conn.commit()



def read_parquet(key):
    obj = s3.get_object(Bucket=BUCKET, Key=key)

    return pd.read_parquet(
        BytesIO(obj["Body"].read())
    )


def upsert_data(conn, df):

    values = [
        tuple(row)
        for row in df.to_numpy()
    ]

    query = """
    INSERT INTO trades (
        trade_id,
        xid,
        price,
        quantity,
        timestamp_eastern,
        order_value
    )
    VALUES %s
    ON CONFLICT (trade_id)
    DO UPDATE SET
        xid = EXCLUDED.xid,
        price = EXCLUDED.price,
        quantity = EXCLUDED.quantity,
        timestamp_eastern = EXCLUDED.timestamp_eastern,
        order_value = EXCLUDED.order_value;
    """

    with conn.cursor() as cur:
        execute_values(cur, query, values)

    conn.commit()


def lambda_handler(event, context):
    load_type = event.get(
        "load_type",
        "INCREMENTAL"
    )

    conn = connect_db()

    all_files = get_s3_files()

    if load_type == "FULL":

        print("Running FULL LOAD")

        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE trades")

        conn.commit()

        files_to_process = all_files
    
    else:

        print("Running INCREMENTAL LOAD")

        processed_files = get_processed_files(conn)

        files_to_process = [
            f for f in all_files
            if f not in processed_files
        ]

    print(f"Files to process: {files_to_process}")

    for file in files_to_process:

        df = read_parquet(file)

        if df.empty:
            continue

        upsert_data(conn, df)

        mark_file_processed(conn, file)

        print(f"Loaded file: {file}")

    conn.close()

    return {
        "status": "SUCCESS",
        "load_type": load_type,
        "files_processed": len(files_to_process)
    }