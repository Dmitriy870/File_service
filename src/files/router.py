from fastapi import APIRouter, BackgroundTasks, Depends, File, UploadFile
from fastapi.responses import StreamingResponse

from files.dependencies import get_s3_client
from files.service import S3Client

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    service: S3Client = Depends(get_s3_client),
):
    return await service.upload_file(file, background_tasks)


@router.delete("/{slug}/")
async def delete_file(slug: str, service: S3Client = Depends(get_s3_client)):
    return await service.delete_file(slug)


@router.get("/{slug}/")
async def get_file(slug: str, service: S3Client = Depends(get_s3_client)):
    file_iterator = await service.download_file_stream(slug)
    return StreamingResponse(
        file_iterator,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={slug}"},  # noqa
    )
