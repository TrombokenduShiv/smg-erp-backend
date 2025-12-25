import os
import boto3
import environ

# Setup Env
env = environ.Env()
environ.Env.read_env()

def test_connection():
    print("Testing AWS Connection...")
    
    try:
        # Try to connect to IAM service (Identity) to verify keys
        client = boto3.client(
            'iam',
            aws_access_key_id=env('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=env('AWS_SECRET_ACCESS_KEY'),
            region_name=env('AWS_REGION')
        )
        
        # Get current user details
        user = client.get_user()
        print("✅ SUCCESS!")
        print(f"Connected as User: {user['User']['UserName']}")
        print(f"User ARN: {user['User']['Arn']}")
        
    except Exception as e:
        print("❌ FAILED.")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_connection()