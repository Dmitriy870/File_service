from pydantic import Field
from pydantic_settings import BaseSettings


class KafkaConfig(BaseSettings):
    BOOTSTRAP_SERVERS: str = Field(...)
    TOPIC: str = Field(...)

    class Config:
        env_prefix = "KAFKA_"


class S3Config(BaseSettings):
    ENDPOINT_URL: str = Field(...)
    ACCESS_KEY: str = Field(...)
    SECRET_KEY: str = Field(...)
    BUCKET_NAME: str = Field(...)

    class Config:
        env_prefix = "S3_"


class VersionConfig(BaseSettings):
    API_V1_PREFIX: str = Field(default="/api/v1")
