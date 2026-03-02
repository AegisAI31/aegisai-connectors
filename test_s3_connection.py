"""
Test AWS S3 Connection
Run this to verify your S3 credentials are working
"""
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import os
from dotenv import load_dotenv

load_dotenv()

def test_s3_connection():
    print("Testing AWS S3 Connection...")
    print("-" * 50)
    
    # Get credentials from .env
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('AWS_REGION', 'us-east-1')
    bucket_name = os.getenv('S3_BUCKET_NAME')
    
    # Check if credentials exist
    if not access_key:
        print("❌ AWS_ACCESS_KEY_ID not found in .env")
        return False
    
    if not secret_key:
        print("❌ AWS_SECRET_ACCESS_KEY not found in .env")
        return False
    
    if not bucket_name:
        print("❌ S3_BUCKET_NAME not found in .env")
        return False
    
    print(f"✓ Access Key ID: {access_key[:8]}...")
    print(f"✓ Secret Key: {'*' * 20}")
    print(f"✓ Region: {region}")
    print(f"✓ Bucket: {bucket_name}")
    print()
    
    try:
        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        # Test 1: List buckets
        print("Test 1: Listing buckets...")
        response = s3_client.list_buckets()
        buckets = [b['Name'] for b in response['Buckets']]
        print(f"✓ Found {len(buckets)} bucket(s)")
        
        # Test 2: Check if our bucket exists
        print(f"\nTest 2: Checking bucket '{bucket_name}'...")
        if bucket_name in buckets:
            print(f"✓ Bucket '{bucket_name}' exists")
        else:
            print(f"❌ Bucket '{bucket_name}' not found")
            print(f"Available buckets: {', '.join(buckets)}")
            return False
        
        # Test 3: Upload test file
        print("\nTest 3: Testing upload...")
        test_content = b"AegisAI S3 Connection Test"
        test_key = "test/connection_test.txt"
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=test_content,
            ServerSideEncryption='AES256'
        )
        print(f"✓ Successfully uploaded test file")
        
        # Test 4: Generate presigned URL
        print("\nTest 4: Testing presigned URL...")
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': test_key},
            ExpiresIn=3600
        )
        print(f"✓ Generated presigned URL (expires in 1 hour)")
        
        # Test 5: Delete test file
        print("\nTest 5: Cleaning up...")
        s3_client.delete_object(Bucket=bucket_name, Key=test_key)
        print(f"✓ Deleted test file")
        
        print("\n" + "=" * 50)
        print("✅ ALL TESTS PASSED!")
        print("✅ S3 connection is working correctly!")
        print("=" * 50)
        return True
        
    except NoCredentialsError:
        print("\n❌ ERROR: No AWS credentials found")
        print("Check your .env file")
        return False
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        print(f"\n❌ ERROR: {error_code}")
        print(f"Message: {e.response['Error']['Message']}")
        
        if error_code == 'InvalidAccessKeyId':
            print("\nSolution: Your Access Key ID is invalid")
            print("1. Go to AWS IAM Console")
            print("2. Create new access keys")
            print("3. Update .env file")
        elif error_code == 'SignatureDoesNotMatch':
            print("\nSolution: Your Secret Access Key is incorrect")
            print("1. Regenerate access keys in IAM")
            print("2. Update .env file")
        elif error_code == 'AccessDenied':
            print("\nSolution: IAM user lacks S3 permissions")
            print("1. Go to IAM Console")
            print("2. Attach 'AmazonS3FullAccess' policy to user")
        
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    test_s3_connection()
