import boto3
import os

codebuild = boto3.client('codebuild')

def lambda_handler(event, context):
    s3_key = event['detail']['object']['key']
    bucket = event['detail']['bucket']['name']
    project = os.environ['CODEBUILD_PROJECT_NAME']

    if not s3_key.endswith("requirements.txt"):
        print("Not a requirements file. Ignoring.")
        return

    response = codebuild.start_build(
        projectName=project,
        environmentVariablesOverride=[
            {'name': 'S3_KEY', 'value': s3_key, 'type': 'PLAINTEXT'},
            {'name': 'BUCKET_NAME', 'value': bucket, 'type': 'PLAINTEXT'}
        ]
    )
    print(f"Started build for {s3_key}")
    return response
