import boto3
import hashlib
import json

sfn = boto3.client('stepfunctions')

STATE_MACHINE_ARN = "arn:aws:states:us-west-1:211125553511:stateMachine:gitanjaleeTestStateMachine"

def lambda_handler(event, context):

    bucket = event['detail']['bucket']['name']
    key = event['detail']['object']['key']

    # create deterministic id
    base = f"{bucket}/{key}"
    execution_id = hashlib.md5(base.encode()).hexdigest()

    execution_name = f"csv-{execution_id}"

    response = sfn.start_execution(
        stateMachineArn=STATE_MACHINE_ARN,
        name=execution_name,
        input=json.dumps({
            "bucket": bucket,
            "key": key
        })
    )

    return {
        "status": "started",
        "executionArn": response["executionArn"]
    }