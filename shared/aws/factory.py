from .s3 import S3Service


class AWSServiceFactory:
    @staticmethod
    def get_service(service: str, *args):
        catalog = {
            's3': S3Service
        }
        service_class = catalog.get(service, None)
        if not service_class:
            raise KeyError('Requested service is not available')
        return service_class(*args)
