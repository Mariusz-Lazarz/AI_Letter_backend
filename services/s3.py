import boto3
from config import AWS_ACCESS_KEY_ID, AWS_REGION, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME
from botocore.exceptions import ClientError
from helpers.logger import AppLogger

logger = AppLogger(log_file="s3.log", logger_name="s3_service")


def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )


def upload_to_s3(file_bytes: bytes, key: str, content_type: str, tags: str):
    s3 = get_s3_client()
    try:
        s3.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=key,
            Body=file_bytes,
            ContentType=content_type,
            Tagging=tags
        )

    except ClientError as e:
        logger.log_error(f"Failed to upload S3 object '{key}': {e}")
        return False

    return True


def delete_from_s3(key):
    s3 = get_s3_client()
    try:
        s3.delete_object(
            Bucket=S3_BUCKET_NAME,
            Key=key,
        )
    except ClientError as e:
        logger.log_error(f"Failed to delete S3 object '{key}': {e}")
        return False

    return True
