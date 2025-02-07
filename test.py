import boto3
import json
import requests
from botocore.exceptions import NoCredentialsError, ClientError

# Initialize AWS clients
s3_client = boto3.client('s3')
lambda_client = boto3.client('lambda')

# Replace these with your actual resource names/IDs
bucket_name = "statements-bucket-21321"
lambda_function_name = "generate-presigned-url"
vpc_endpoint_id = "vpce-052b7d314e5d****"
test_file = "test-file.txt"


def test_s3_bucket_access():
    try:
        # Attempt to list objects in the bucket
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        print("S3 Bucket Access Test: Success")
        print("Objects in bucket:", response.get('Contents', []))
    except ClientError as e:
        print("S3 Bucket Access Test: Failed")
        print("Error:", e)
 

    # Check server-side encryption
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=test_file)
        encryption = response.get('ServerSideEncryption', 'None')
        if encryption == "AES256":
            print(f"✅ Server-side encryption is enabled with AES256.")
        else:
            print(f"Server-side encryption is not enabled or not using AES256.")
    except Exception as e:
        print(f"Error checking encryption: {e}")


    # Check public access of bucket
    try:
        response = s3_client.get_public_access_block(Bucket=bucket_name)
        public_access = response["PublicAccessBlockConfiguration"]

        if (
            public_access.get("BlockPublicAcls", False)
            and public_access.get("BlockPublicPolicy", False)
            and public_access.get("IgnorePublicAcls", False)
            and public_access.get("RestrictPublicBuckets", False)
        ):
            print(f"✅ Public access is fully blocked on bucket '{bucket_name}'.")
        else:
            print(f"⚠️ Public access is not fully blocked on bucket '{bucket_name}'. Check configuration.")

    except s3_client.exceptions.NoSuchPublicAccessBlockConfiguration:
        print(f"❌ No Public Access Block configuration found on bucket '{bucket_name}'.")
    except Exception as e:
        print(f"⚠️ Error checking public access block: {e}")

    # Test 1: Try accessing the S3 object using HTTPS
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=test_file)
        print(f"✅ HTTPS access successful. Object Content: {response['Body'].read().decode()}")
    except ClientError as e:
        if e.response['Error']['Code'] == "403":
            print("❌ HTTPS access denied. Check the bucket policy.")
        else:
            print(f"⚠️ Error accessing S3 via HTTPS: {e}")

    # Test 2: Try accessing the S3 object using HTTP (should be denied)
    try:
        http_url = f"http://{bucket_name}.s3.amazonaws.com/{test_file}"  # HTTP request
        response = requests.get(http_url)
        if response.status_code == 403:
            print("✅ HTTP access correctly denied by policy.")
        else:
            print(f"⚠️ Unexpected HTTP response: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Error making HTTP request: {e}")

    # Test 3: Check if access is restricted to a specific VPC endpoint

    try:
    # First ensure policy is parsed from JSON if it's a string
        response = s3_client.get_bucket_policy(Bucket=bucket_name)
        policy = response['Policy']
        if isinstance(policy, str):
            policy = json.loads(policy)
            
        for statement in policy['Statement']:
            if statement.get('Condition', {}).get('StringEquals', {}).get('aws:SourceVpce') == vpc_endpoint_id:
                print(f"✅ VPC Endpoint restriction is correctly applied for {vpc_endpoint_id}.")
                return True
        print("⚠️ VPC Endpoint restriction might not be applied correctly.")
        return False
    except Exception as e:
        print(f"⚠️ Error checking VPC Endpoint restriction: {str(e)}")
        return False

def test_s3_lifecycle_rules():
    """Check and verify the lifecycle rules applied to the S3 bucket."""
    try:
        response = s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
        rules = response.get("Rules", [])
        
        if not rules:
            print("❌ No lifecycle rules found.")
            return

        print("\n✅ Lifecycle Rules Configured:")
        for rule in rules:
            print(f"Rule ID: {rule.get('ID', 'N/A')}")
            print(f"Status: {rule.get('Status', 'Disabled')}")

            if 'NoncurrentVersionTransitions' in rule:
                for transition in rule['NoncurrentVersionTransitions']:
                    print(f"   🔄 Transition: {transition['StorageClass']} after {transition['NoncurrentDays']} days")

            if 'NoncurrentVersionExpiration' in rule:
                print(f"   🗑 Delete non-current versions after {rule['NoncurrentVersionExpiration']['NoncurrentDays']} days")

            if 'AbortIncompleteMultipartUpload' in rule:
                print(f"   🚫 Abort incomplete multipart uploads after {rule['AbortIncompleteMultipartUpload']['DaysAfterInitiation']} days")

            if 'Expiration' in rule and rule['Expiration'].get('ExpiredObjectDeleteMarker'):
                print("   ✅ Expired object delete marker is enabled.")

    except s3_client.exceptions.NoSuchLifecycleConfiguration:
        print("❌ No lifecycle configuration found.")
    except Exception as e:
        print(f"⚠️ Error retrieving lifecycle configuration: {e}")

def test_lambda_function():
    try:
        # Invoke the Lambda function to generate a presigned URL
        response = lambda_client.invoke(
            FunctionName=lambda_function_name,
            InvocationType='RequestResponse'
        )
        response_payload = json.loads(response['Payload'].read().decode('utf-8'))
        # Parse the 'body' field as JSON
        body_dict = json.loads(response_payload['body'])
        print("Lambda Function Test: Success")
        print("Presigned URL:", body_dict.get('url'))
    except ClientError as e:
        print("Lambda Function Test: Failed")
        print("Error:", e)

def main():
    print("Testing S3 Bucket Access...")
    test_s3_bucket_access()

    print("\nTesting Life Cycle Rules...")
    test_s3_lifecycle_rules()

    print("\nTesting Lambda Function...")
    test_lambda_function()

if __name__ == "__main__":
    main()
