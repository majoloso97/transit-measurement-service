from .s3 import S3Service


class AWSServiceFactory:
    @staticmethod
    def get_service(service: str, config: dict):
        catalog = {
            'S3': S3Service
        }
        service_class = catalog.get(service.upper(), None)
        if not service_class:
            raise KeyError('Requested service is not available')
        return service_class(**config)
