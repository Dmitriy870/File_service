from pydantic import BaseModel, Field


class AwsS3Config(BaseModel):
    aws_access_key_id: str = Field(...)
    aws_secret_access_key: str = Field(...)
    endpoint_url: str = Field(...)
    bucket_name: str = Field(...)
