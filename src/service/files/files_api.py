from __future__ import annotations

from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
import orjson

import src.common.common_codes as codes
from service.files import files_service
from service.files.files_schema import FileListResponse

router = APIRouter(prefix="/api/files", tags=["Files"])
public_router = APIRouter(prefix="/files", tags=["Files Public"])


@router.post("/upload", status_code=201)
async def upload_file(request: Request, file: UploadFile = File(...), metadata: str | None = Form(None)):
    ctx = request.app.state.ctx

    meta_dict = None
    if metadata:
        try:
            meta_dict = orjson.loads(metadata)
        except Exception:
            raise HTTPException(status_code=400, detail="metadata must be JSON string")

    stored = files_service.save_file(ctx, file, meta_dict)
    return {"code": codes.ResponseStatus.SUCCESS["code"], "data": stored}


@router.get("")
async def list_all_files():
    files = files_service.list_files()
    return {
        "code": codes.ResponseStatus.SUCCESS["code"],
        "data": FileListResponse(files=files, total=len(files))
    }


@router.get("/{file_id}")
async def get_file_meta(file_id: str):
    info = files_service.get_file(file_id)
    if not info:
        raise HTTPException(status_code=404, detail="file not found")
    return {"code": codes.ResponseStatus.SUCCESS["code"], "data": info}


@router.delete("/{file_id}")
async def delete_file(request: Request, file_id: str):
    ctx = request.app.state.ctx
    info = files_service.delete_file(ctx, file_id)
    if not info:
        raise HTTPException(status_code=404, detail="file not found")
    return {"code": codes.ResponseStatus.SUCCESS["code"], "data": {"id": file_id}}


@public_router.get("/{stored_name}")
async def download_file(stored_name: str):
    path = files_service.resolve_path_by_stored_name(stored_name)
    if not path:
        raise HTTPException(status_code=404, detail="file not found")
    return FileResponse(path)
