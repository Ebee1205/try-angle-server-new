from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any
import threading
import uuid

from fastapi import UploadFile

from service.files.files_schema import FileMetadata


_FILES_DIR = Path("files")
_STORE: Dict[str, FileMetadata] = {}
_STORE_LOCK = threading.Lock()


def _ensure_dir() -> None:
    _FILES_DIR.mkdir(parents=True, exist_ok=True)


def save_file(ctx, file: UploadFile, meta: Optional[Dict[str, Any]] = None) -> FileMetadata:
    _ensure_dir()

    file_id = uuid.uuid4().hex
    safe_name = Path(file.filename or "uploaded.bin").name
    stored_name = f"{file_id}_{safe_name}"
    dest = _FILES_DIR / stored_name

    size = 0
    with dest.open("wb") as out:
        while True:
            chunk = file.file.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            out.write(chunk)

    metadata = FileMetadata(
        id=file_id,
        filename=safe_name,
        stored_name=stored_name,
        path=str(dest),
        url=f"/files/{stored_name}",
        size=size,
        content_type=file.content_type,
        meta=meta or {},
        created_at=datetime.utcnow(),
    )

    with _STORE_LOCK:
        _STORE[file_id] = metadata

    ctx.log.info(f"Stored file | id={file_id} name={safe_name} size={size}")
    return metadata


def delete_file(ctx, file_id: str) -> Optional[FileMetadata]:
    with _STORE_LOCK:
        info = _STORE.pop(file_id, None)

    if not info:
        return None

    path = Path(info.path)
    try:
        if path.exists():
            path.unlink()
    except Exception as e:
        ctx.log.warning(f"Failed to delete file | id={file_id} | err={e}")

    ctx.log.info(f"Deleted file | id={file_id}")
    return info


def get_file(file_id: str) -> Optional[FileMetadata]:
    with _STORE_LOCK:
        return _STORE.get(file_id)


def list_files() -> list[FileMetadata]:
    with _STORE_LOCK:
        return list(_STORE.values())


def resolve_path_by_stored_name(stored_name: str) -> Optional[Path]:
    # stored_name는 저장 시점에 id_safeName 형태라서 파일명만 허용
    candidate = _FILES_DIR / Path(stored_name).name
    if candidate.exists():
        return candidate
    return None
