import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from config import VersionConfig
from containers.configs import ClientContainer
from files.logging_conf import configure_logging
from files.router import router

version_config = VersionConfig()
logger = configure_logging(logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = ClientContainer()
    container.wire(modules=[__name__, "files.service"])
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router)
