from typing import Optional

from pydantic import BaseModel, Field


class CtgListRequest(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)


class CtgGetRequest(BaseModel):
    id: str = Field(...)


class CtgCreateRequest(BaseModel):
    userId: str = Field(...)
    name: str = Field(...)


class CtgUpdateRequest(BaseModel):
    id: str = Field(...)
    name: Optional[str] = Field(None)


class CtgDeleteRequest(BaseModel):
    id: str = Field(...)


class CtgItem(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    cDate: int = Field(...)
    uDate: int = Field(...)

    class Config:
        from_attributes = True


class CtgListResponse(BaseModel):
    items: list[CtgItem]
    total: int
    page: int
    limit: int

    class Config:
        from_attributes = True
