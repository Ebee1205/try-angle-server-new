from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class FileMetadata(BaseModel):
    id: str
    filename: str
    stored_name: str
    path: str
    url: str
    size: int
    content_type: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class FileListResponse(BaseModel):
    files: list[FileMetadata]
    total: int
