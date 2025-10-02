import json

import boto3
from django.conf import settings
from django.core.management.base import BaseCommand


def s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_STORAGE_BUCKET_REGION,
        config=settings.AWS_S3_CLIENT_CONFIG,
    )


class Command(BaseCommand):
    def handle(self, *args, **options):
        client = s3_client()

        for bucket_name in settings.AWS_STORAGE_BUCKET_NAME, settings.AWS_STORAGE_BUCKET_NAME_PUBLIC:
            try:
                client.create_bucket(Bucket=bucket_name)
            except client.exceptions.BucketAlreadyOwnedByYou:
                pass

        # Set up public access to the AWS_STORAGE_BUCKET_NAME_PUBLIC bucket
        public_bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicRead",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{settings.AWS_STORAGE_BUCKET_NAME_PUBLIC}/*"],
                }
            ],
        }
        client.put_bucket_policy(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME_PUBLIC,
            Policy=json.dumps(public_bucket_policy),
        )
