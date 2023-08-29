import re
from datetime import datetime
from fastapi import UploadFile
from .base import BaseAWSService
from settings import settings
from api.services.errors import raise_http_exception


class S3Service(BaseAWSService):
    SERVICE_NAME = 's3'
    
    def __init__(self, bucket_name: str):
        super().__init__(self.SERVICE_NAME)
