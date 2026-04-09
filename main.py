from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from utils.s3 import delete_file, ensure_bucket_exists, generate_presigned_url, list_files, upload_file


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_bucket_exists()
    yield


app = FastAPI(title="ministack S3 demo", lifespan=lifespan)


@app.get("/")
async def index():
    return FileResponse("templates/index.html")


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()
        key = file.filename or "upload"
        content_type = file.content_type or "application/octet-stream"
        upload_file(file_bytes, key, content_type)
        url = generate_presigned_url(key)
        return JSONResponse({"url": url, "key": key})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/files")
async def list_bucket_files():
    try:
        return JSONResponse(list_files())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/files/{key:path}")
async def delete(key: str):
    try:
        delete_file(key)
        return JSONResponse({"deleted": key})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/presigned-url/{key:path}")
async def presigned_url(key: str):
    try:
        url = generate_presigned_url(key)
        return JSONResponse({"url": url, "key": key})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
