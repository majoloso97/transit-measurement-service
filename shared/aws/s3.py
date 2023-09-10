import re
import logging
from datetime import datetime
from tempfile import SpooledTemporaryFile
from botocore.exceptions import ClientError
from .base import BaseAWSService
from settings import settings


logger = logging.getLogger(__name__)


class S3Service(BaseAWSService):
    SERVICE_NAME = 's3'
    
    def __init__(self, bucket_name: str):
        super().__init__(self.SERVICE_NAME)
        self.bucket = bucket_name
        self.create_or_set_bucket()

    def create_or_set_buckets(self):
        response = self.client.list_buckets()

        existing_buckets = [bucket['Name'] for bucket in response['Buckets']]

        if self.bucket not in existing_buckets:
            self.client.create_bucket(Bucket=self.bucket)

    def generate_presigned_url(self,
                               object_key: str,
                               content_type: str = 'video/mp4',
                               expiration: int = 3600) -> str:
        allowed_content_types = ['video/mp4']
        
        if content_type not in allowed_content_types:
            raise ValueError("Unsupported content type")
        
        try:
            url = self.client.generate_presigned_url(
                'put_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': object_key,
                    'ContentType': content_type
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.exception(f"Error generating presigned URL: {e}")
            return ""

    def get_presigned_url(self,
                          object_key: str,
                          expiration: int = 3600) -> str:
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket,
                        'Key': object_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.exception(f"Error generating presigned URL: {e}")
            return ''

    def remove_file(self, key: str):
        self.client.delete_object(Bucket=self.bucket, Key=key)

    def remove_existing_file(self, prefix: str):
        response = self.client.list_objects(Bucket=self.bucket,
                                            Prefix=prefix)
        if 'Contents' in response:
            for obj in response['Contents']:
                self.remove_file(bucket=self.bucket,
                                 key=obj['Key'])

    def create_unique_name(self, identifier: str, original_filename: str):
        regex_for_file_extension = r'(.\w+)$'
        file_ext = re.findall(regex_for_file_extension, original_filename)[0]
        timestamp = str(datetime.utcnow())
        key = f'{identifier}_{timestamp.replace(" ","_")}{file_ext}'

        return key

    def upload_new_file_and_remove_previous(self,
                                            bucket: str,
                                            file_name: str,
                                            content_type: str,
                                            file: SpooledTemporaryFile,
                                            identifier: str):
        try:
            self.remove_existing_file(bucket=bucket, prefix=identifier)
            key = self.create_unique_name(identifier=identifier,
                                          original_filename=file_name)

            update_extra_args = {'ContentType': content_type}

            self.client.upload_fileobj(Fileobj=file,
                                       Bucket=self.bucket,
                                       Key=key,
                                       ExtraArgs=update_extra_args)

            return self.get_presigned_url(key)
        except Exception:
            raise RuntimeError('Could not upload the file')
