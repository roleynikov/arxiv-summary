import boto3
import os


def get_s3():
    return boto3.client('s3',endpoint_url=os.environ.get('S3_ENDPOINT'),aws_access_key_id=os.environ.get('S3_ACCESS_KEY'),aws_secret_access_key=os.environ.get('S3_SECRET_KEY'),region_name='ru-central1')


def upload_file(local_path, s3_key):
    s3 = get_s3()
    bucket = os.environ.get('S3_BUCKET')
    s3.upload_file(Filename=str(local_path),Bucket=bucket,Key=s3_key)


def upload_dir(local_dir, prefix):
    for path in local_dir.rglob('*'):
        if path.is_file():
            rel = path.relative_to(local_dir)
            upload_file(path, f'{prefix}/{rel}')