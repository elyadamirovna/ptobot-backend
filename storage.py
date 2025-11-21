import boto3
import os
from uuid import uuid4
from io import BytesIO

S3_BUCKET = os.getenv("YANDEX_BUCKET")
S3_ACCESS_KEY = os.getenv("YANDEX_ACCESS_KEY")
S3_SECRET_KEY = os.getenv("YANDEX_SECRET_KEY")
S3_ENDPOINT = os.getenv("YANDEX_ENDPOINT", "https://storage.yandexcloud.net")
S3_REGION = os.getenv("YANDEX_REGION", "ru-central1")

s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION
)

def upload_to_yandex(file_bytes: bytes, filename: str, content_type: str) -> str:
    key = f"reports/{uuid4().hex}_{filename}"

    s3.upload_fileobj(
        Fileobj=BytesIO(file_bytes),
        Bucket=S3_BUCKET,
        Key=key,
        ExtraArgs={
            "ACL": "public-read",
            "ContentType": content_type
        }
    )

    return f"{S3_ENDPOINT}/{S3_BUCKET}/{key}"
