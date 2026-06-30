from airflow import DAG
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.providers.amazon.aws.operators.lambda_function import LambdaInvokeFunctionOperator

from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

with DAG(
    dag_id="csv_pipeline",
    start_date=datetime(2025,1,1),
    schedule_interval=None,
    catchup=False,
    default_args=default_args
) as dag:

    glue_task = GlueJobOperator(
        task_id="glue_etl",
        job_name="csv-to-parquet-job",
        script_args={
            "--input_path": "{{ dag_run.conf['input_path'] }}",
            "--output_path": "{{ dag_run.conf['output_path'] }}"
        },
        wait_for_completion=True
    )

    lambda_task = LambdaInvokeFunctionOperator(
        task_id="load_to_rds",
        function_name="load-parquet-to-rds",
        payload="""
        {
            "parquet_path": "{{ dag_run.conf['output_path'] }}"
        }
        """
    )

    glue_task >> lambda_task