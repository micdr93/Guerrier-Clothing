import os
import boto3
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Uploads all local media files to S3."

    def handle(self, *args, **options):
        # Ensure MEDIA_ROOT is defined in your settings
        local_media_path = Path(settings.MEDIA_ROOT)
        if not local_media_path.exists():
            self.stdout.write(self.style.ERROR("MEDIA_ROOT does not exist."))
            return

        # S3 configuration from settings
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        s3_media_prefix = "media/"  # Make sure this matches your MEDIA_URL configuration

        # Initialize boto3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            region_name=settings.AWS_S3_REGION_NAME
        )

        # Iterate over all files in MEDIA_ROOT
        for root, dirs, files in os.walk(local_media_path):
            for filename in files:
                local_file = Path(root) / filename
                relative_path = local_file.relative_to(local_media_path)
                s3_key = os.path.join(s3_media_prefix, str(relative_path)).replace("\\", "/")
                try:
                    s3_client.upload_file(
                        Filename=str(local_file),
                        Bucket=bucket_name,
                        Key=s3_key,
                        ExtraArgs={'ACL': 'public-read'}
                    )
                    self.stdout.write(self.style.SUCCESS(
                        f"Uploaded {local_file} to s3://{bucket_name}/{s3_key}"
                    ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f"Error uploading {local_file}: {e}"
                    ))
