import io
import logging
from contextlib import asynccontextmanager

from aioboto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from dependency_injector.wiring import Provide, inject
from fastapi import BackgroundTasks

from containers.configs import ClientContainer
from files.logging_conf import configure_logging
from files.schema import AwsS3Config
from files.utils import slugify

logger = configure_logging(logging.INFO)


class S3Client:
    def __init__(self):
        self.session = Session()

    @inject
    @asynccontextmanager
    async def get_client(self, config: AwsS3Config = Provide[ClientContainer.config]):
        async with self.session.client(
            "s3", **config.model_dump(exclude={"bucket_name"})
        ) as client:
            yield client

    async def upload_file(self, file, background_tasks: BackgroundTasks):
        slug = slugify(file.filename)
        file_content = await file.read()
        file_obj = io.BytesIO(file_content)
        background_tasks.add_task(self._upload_file_task, file_obj, slug)
        await file.close()
        return {"message": "Start loading", "slug": slug}

    @staticmethod
    async def safe_file_iterator(file_stream, chunk_size: int = 8192):
        try:
            async for chunk in file_stream.iter_chunks(chunk_size):
                yield chunk
        except ClientError as ce:
            logger.error(f"Client error during streaming: {ce}")
            return
        except BotoCoreError as bce:
            logger.error(f"BotoCore error during streaming: {bce}")
            return
        except RuntimeError as re:
            logger.error(f"Runtime error during streaming: {re}")
            return

    @inject
    async def _upload_file_task(
        self, file_obj, object_name: str, s3config: AwsS3Config = Provide[ClientContainer.s3config]
    ):
        async with self.get_client() as client:
            try:
                logger.info(f"Uploading {object_name}")
                await client.upload_fileobj(file_obj, s3config.BUCKET_NAME, object_name)
                logger.info(f"File {object_name} loaded in {s3config.BUCKET_NAME}")
            except ClientError as ce:
                logger.error(f"Client error loading file {object_name}: {ce}")
            except BotoCoreError as bce:
                logger.error(f"BotoCore error loading file {object_name}: {bce}")

    @inject
    async def delete_file(
        self, slug: str, s3config: AwsS3Config = Provide[ClientContainer.s3config]
    ):
        async with self.get_client() as client:
            try:
                logger.info(f"Deleting {slug} from bucket {s3config.BUCKET_NAME}")
                await client.delete_object(Bucket=s3config.BUCKET_NAME, Key=slug)
                logger.info(f"File {slug} deleted.")
                return {"message": f"File {slug} deleted."}
            except ClientError as ce:
                logger.error(f"Client error deleting file {slug}: {ce}")
                return {"error": str(ce)}
            except BotoCoreError as bce:
                logger.error(f"BotoCore error deleting file {slug}: {bce}")
                return {"error": str(bce)}

    @inject
    async def download_file_stream(
        self, object_name: str, s3config: AwsS3Config = Provide[ClientContainer.s3config]
    ):
        async with self.get_client() as client:
            try:
                response = await client.get_object(Bucket=s3config.BUCKET_NAME, Key=object_name)
                file_stream = response["Body"]
                return self.safe_file_iterator(file_stream)
            except ClientError as ce:
                logger.error(f"Client error downloading file {object_name}: {ce}")
                raise
            except BotoCoreError as bce:
                logger.error(f"BotoCore error downloading file {object_name}: {bce}")
                raise
