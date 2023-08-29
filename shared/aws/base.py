import boto3
from settings import settings


class BaseAWSService:
    def __init__(self, service: str) -> None:
        self.initialize_service(service)

    def initialize_service(self, service: str):
        self.client = boto3.client(service,
                                   region_name=settings.AWS_REGION,
                                   aws_access_key_id=settings.AWS_KEY_ID,
                                   aws_secret_access_key=settings.AWS_SECRET)