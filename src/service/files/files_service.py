from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any
import threading
import uuid

import aioboto3
from fastapi import UploadFile, HTTPException

from src.service.files.files_schema import FileMetadata, IMAGE_MAX_BYTES, ALLOWED_CONTENT_TYPES, ALLOWED_FOLDERS


_STORE: Dict[str, FileMetadata] = {}
_STORE_LOCK = threading.Lock()


def _r2_client(ctx):
    r2 = ctx.cfg.r2
    session = aioboto3.Session()
    return session.client(
        "s3",
        endpoint_url=r2.endpoint_url,
        aws_access_key_id=r2.access_key_id,
        aws_secret_access_key=r2.secret_access_key,
        region_name=r2.region,
    )


async def save_file(ctx, file: UploadFile, meta: Optional[Dict[str, Any]] = None, prefix: Optional[str] = None) -> FileMetadata:
    # --- 유효성 검사 ---
    content_type = file.content_type or ""
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported media type '{content_type}'. Allowed: {sorted(ALLOWED_CONTENT_TYPES)}",
        )

    data = await file.read()
    if len(data) > IMAGE_MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Image too large ({len(data)} bytes). Max allowed: {IMAGE_MAX_BYTES} bytes (10 MB)",
        )

    # --- R2 업로드 ---
    r2_cfg = ctx.cfg.r2
    if not prefix:
        raise HTTPException(status_code=400, detail="'prefix' (upload folder) is required")
    folder = prefix.strip("/")
    if folder not in ALLOWED_FOLDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid folder '{folder}'. Allowed: {sorted(ALLOWED_FOLDERS)}",
        )
    file_id = uuid.uuid4().hex
    safe_name = Path(file.filename or "upload.bin").name
    key = f"{folder}/{file_id}_{safe_name}"

    async with _r2_client(ctx) as client:
        await client.put_object(
            Bucket=r2_cfg.bucket_name,
            Key=key,
            Body=data,
            ContentType=content_type,
        )

    base_url = (r2_cfg.public_base_url or "").rstrip("/")
    public_url = f"{base_url}/{key}"

    metadata = FileMetadata(
        id=file_id,
        filename=safe_name,
        stored_name=key,
        path=key,
        url=public_url,
        size=len(data),
        content_type=content_type,
        meta=meta or {},
        created_at=datetime.utcnow(),
    )

    with _STORE_LOCK:
        _STORE[file_id] = metadata

    ctx.log.info(f"Uploaded to R2 | id={file_id} key={key} size={len(data)}")
    return metadata


async def delete_file(ctx, file_id: str) -> Optional[FileMetadata]:
    with _STORE_LOCK:
        info = _STORE.pop(file_id, None)

    if not info:
        return None

    try:
        async with _r2_client(ctx) as client:
            await client.delete_object(
                Bucket=ctx.cfg.r2.bucket_name,
                Key=info.stored_name,
            )
    except Exception as e:
        ctx.log.warning(f"Failed to delete from R2 | id={file_id} | err={e}")

    ctx.log.info(f"Deleted from R2 | id={file_id}")
    return info


def get_file(file_id: str) -> Optional[FileMetadata]:
    with _STORE_LOCK:
        return _STORE.get(file_id)


def list_files() -> list[FileMetadata]:
    with _STORE_LOCK:
        return list(_STORE.values())


async def get_presigned_url(ctx, file_id: str) -> Optional[str]:
    with _STORE_LOCK:
        info = _STORE.get(file_id)
    if not info:
        return None

    r2_cfg = ctx.cfg.r2
    async with _r2_client(ctx) as client:
        url = await client.generate_presigned_url(
            "get_object",
            Params={"Bucket": r2_cfg.bucket_name, "Key": info.stored_name},
            ExpiresIn=r2_cfg.upload_url_expire_seconds,
        )
    return url
