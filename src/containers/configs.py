from dependency_injector import containers, providers

from config import S3Config
from files.schema import AwsS3Config


class ClientContainer(containers.DeclarativeContainer):
    s3config = providers.Singleton(S3Config)

    config = providers.Factory(
        AwsS3Config,
        aws_access_key_id=s3config.provided.ACCESS_KEY,
        aws_secret_access_key=s3config.provided.SECRET_KEY,
        endpoint_url=s3config.provided.ENDPOINT_URL,
        bucket_name=s3config.provided.BUCKET_NAME,
    )
