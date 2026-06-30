import json
import boto3
import requests

mwaa = boto3.client('mwaa')

ENV_NAME = "csv-pipeline-mwaa"
DAG_NAME = "csv_pipeline"

def lambda_handler(event, context):

    bucket = event['detail']['bucket']['name']
    key = event['detail']['object']['key']

    filename = key.split("/")[-1]
    parquet_name = filename.replace(".csv", ".parquet")

    input_path = f"s3://{bucket}/{key}"
    output_path = f"s3://{bucket}/processed/{parquet_name}"

    cli_token = mwaa.create_cli_token(
        Name=ENV_NAME
    )

    hostname = cli_token["WebServerHostname"]
    token = cli_token["CliToken"]

    url = f"https://{hostname}/aws_mwaa/cli"

    command = f"""
    dags trigger {DAG_NAME} --conf '{{"input_path":"{input_path}","output_path":"{output_path}"}}'
    """

    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "text/plain"
        },
        data=command
    )

    return response.text