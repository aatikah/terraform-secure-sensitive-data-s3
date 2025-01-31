import json
import boto3

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # Your S3 bucket name and object key
    bucket_name = 'statements-bucket-21321'  # Replace with your actual bucket name
    object_key = 'test-file.txt'  # Replace with your object key
    expiration = 3600  # URL expiration time in seconds

    # Generate the presigned URL
    try:
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_key},
            ExpiresIn=expiration
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'url': presigned_url})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
