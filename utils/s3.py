import boto3
from botocore.client import Config
from botocore.exceptions import ClientError

BUCKET_NAME = "my-bucket"
ENDPOINT_URL = "http://localhost:4566"
PRESIGNED_URL_EXPIRY = 3600  # seconds

s3_client = boto3.client(
    "s3",
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id="test",
    aws_secret_access_key="test",
    region_name="us-east-1",
    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": "path"},
    ),
)


def ensure_bucket_exists() -> None:
    try:
        s3_client.head_bucket(Bucket=BUCKET_NAME)
    except ClientError as e:
        if e.response["Error"]["Code"] in ("404", "NoSuchBucket"):
            s3_client.create_bucket(Bucket=BUCKET_NAME)
        else:
            raise


def upload_file(file_bytes: bytes, key: str, content_type: str) -> None:
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=file_bytes,
        ContentType=content_type,
    )


def list_files() -> list[dict]:
    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
    return [
        {"key": obj["Key"], "size": obj["Size"], "last_modified": obj["LastModified"].isoformat()}
        for obj in response.get("Contents", [])
    ]


def delete_file(key: str) -> None:
    s3_client.delete_object(Bucket=BUCKET_NAME, Key=key)


def generate_presigned_url(key: str) -> str:
    return s3_client.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": BUCKET_NAME, "Key": key},
        ExpiresIn=PRESIGNED_URL_EXPIRY,
    )
