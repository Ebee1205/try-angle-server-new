from __future__ import annotations

from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException, Depends
import orjson

import src.common.common_codes as codes
from src.service.auth.static_token_auth import require_user
from src.service.files import files_service
from src.service.files.files_schema import FileListResponse

router = APIRouter(prefix="/api/files", tags=["Files"])

@router.post("/upload", status_code=201)
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    folder: str = Form(..., description="Upload folder inside the bucket (e.g. profiles, reference)"),
    metadata: str | None = Form(None),
    _=Depends(require_user),
):
    ctx = request.app.state.ctx

    meta_dict = None
    if metadata:
        try:
            meta_dict = orjson.loads(metadata)
        except Exception:
            raise HTTPException(status_code=400, detail="metadata must be JSON string")

    stored = await files_service.save_file(ctx, file, meta_dict, prefix=folder)
    return {"code": codes.ResponseStatus.SUCCESS["code"], "data": stored}


@router.get("")
async def list_all_files(_=Depends(require_user)):
    files = files_service.list_files()
    return {
        "code": codes.ResponseStatus.SUCCESS["code"],
        "data": FileListResponse(files=files, total=len(files))
    }


@router.get("/{file_id}")
async def get_file_meta(file_id: str, _=Depends(require_user)):
    info = files_service.get_file(file_id)
    if not info:
        raise HTTPException(status_code=404, detail="file not found")
    return {"code": codes.ResponseStatus.SUCCESS["code"], "data": info}


@router.delete("/{file_id}")
async def delete_file(request: Request, file_id: str, _=Depends(require_user)):
    ctx = request.app.state.ctx
    info = await files_service.delete_file(ctx, file_id)
    if not info:
        raise HTTPException(status_code=404, detail="file not found")
    return {"code": codes.ResponseStatus.SUCCESS["code"], "data": {"id": file_id}}


@router.get("/{file_id}/presigned")
async def get_presigned_url(request: Request, file_id: str, _=Depends(require_user)):
    ctx = request.app.state.ctx
    url = await files_service.get_presigned_url(ctx, file_id)
    if not url:
        raise HTTPException(status_code=404, detail="file not found")
    return {"code": codes.ResponseStatus.SUCCESS["code"], "data": {"url": url}}
