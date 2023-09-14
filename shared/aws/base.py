import boto3
from settings import settings


class BaseAWSService:
    def __init__(self, service: str, client_kwargs: dict) -> None:
        self.initialize_service(service, client_kwargs)

    def initialize_service(self, service: str, client_kwargs: dict):
        self.client = boto3.client(service,
                                   region_name=settings.AWS_REGION,
                                   aws_access_key_id=settings.AWS_KEY_ID,
                                   aws_secret_access_key=settings.AWS_SECRET,
                                   **client_kwargs)
