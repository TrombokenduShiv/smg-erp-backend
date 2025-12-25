import os
import django
import boto3

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

def test_upload():
    print(f"Target Bucket: {settings.AWS_STORAGE_BUCKET_NAME}")

    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )

    # Create a dummy file
    content = "This is a test file from the SMG Backend."

    try:
        s3.put_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key='test_connection.txt',
            Body=content
        )
        print("✅ Upload Successful! Check your S3 Bucket.")
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    test_upload()