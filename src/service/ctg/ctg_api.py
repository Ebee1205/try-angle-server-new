from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
import time

from src.service.auth.jwt_auth import require_user
from src.service.ctg import ctg_service
from src.service.ctg.ctg_schema import (
    CtgCreateRequest,
    CtgDeleteRequest,
    CtgGetRequest,
    CtgListRequest,
    CtgUpdateRequest,
)
from src.common.common_codes import ResponseStatus

router = APIRouter(prefix="/api/ctg", tags=["Category"])


@router.post("/list")
async def list_ctgs(request: Request, payload: CtgListRequest, _=Depends(require_user)):
    ctx = request.app.state.ctx
    try:
        result = ctg_service.list_ctgs(ctx, page=payload.page, limit=payload.limit)
        body = {
            "tid": int(time.time() * 1000),
            "status": ResponseStatus.SUCCESS.info,
            "data": result.dict(),
        }
        return (
            JSONResponse(
                status_code=200,
                content=body,
            )
        )
    
    except HTTPException as e:
        status_enum = ResponseStatus.from_http_code(e.status_code)
        body = {
            "tid": int(time.time() * 1000),
            "status": status_enum.info,
            "data": {},
        }
        return (
            JSONResponse(
                status_code=e.status_code,
                content=body,
            )
        )
    
    except Exception as e:
        if ctx.log:
            ctx.log.error(f"Unexpected error in list_ctgs: {e}")
        status_enum = ResponseStatus.SERVER_ERROR
        body = {
            "tid": int(time.time() * 1000),
            "status": status_enum.info,
            "data": {},
        }
        return (
            JSONResponse(
                status_code=500,
                content=body,
            )
        )


@router.post("/get")
async def get_ctg(request: Request, payload: CtgGetRequest, _=Depends(require_user)):
    ctx = request.app.state.ctx
    try:
        result = ctg_service.get_ctg(ctx, payload.id)
        body = {
            "tid": int(time.time() * 1000),
            "status": ResponseStatus.SUCCESS.info,
            "data": result.dict(),
        }
        return (
            JSONResponse(
                status_code=200,
                content=body,
            )
        )
    except HTTPException as e:
        status_enum = ResponseStatus.from_http_code(e.status_code)
        body = {
            "tid": int(time.time() * 1000),
            "status": status_enum.info,
            "data": {},
        }
        return (
            JSONResponse(
                status_code=e.status_code,
                content=body,
            )
        )
    except Exception as e:
        if ctx.log:
            ctx.log.error(f"Unexpected error in get_ctg: {e}")
        status_enum = ResponseStatus.SERVER_ERROR
        body = {
            "tid": int(time.time() * 1000),
            "status": status_enum.info,
            "data": {},
        }
        return (
            JSONResponse(
                status_code=500,
                content=body,
            )
        )


@router.post("/create")
async def create_ctg(request: Request, payload: CtgCreateRequest, _=Depends(require_user)):
    ctx = request.app.state.ctx
    try:
        result = ctg_service.create_ctg(ctx, payload)
        body = {
            "tid": int(time.time() * 1000),
            "status": ResponseStatus.SUCCESS.info,
            "data": result.dict(),
        }
        return (
            JSONResponse(
                status_code=200,
                content=body,
            )
        )
    except HTTPException as e:
        status_enum = ResponseStatus.from_http_code(e.status_code)
        body = {
            "tid": int(time.time() * 1000),
            "status": status_enum.info,
            "data": {},
        }
        return (
            JSONResponse(
                status_code=e.status_code,
                content=body,
            )
        )
    except Exception as e:
        if ctx.log:
            ctx.log.error(f"Unexpected error in create_ctg: {e}")
        status_enum = ResponseStatus.SERVER_ERROR
        body = {
            "tid": int(time.time() * 1000),
            "status": status_enum.info,
            "data": {},
        }
        return (
            JSONResponse(
                status_code=500,
                content=body,
            )
        )


@router.post("/update")
async def update_ctg(request: Request, payload: CtgUpdateRequest, _=Depends(require_user)):
    ctx = request.app.state.ctx
    try:
        result = ctg_service.update_ctg(ctx, payload)
        body = {
            "tid": int(time.time() * 1000),
            "status": ResponseStatus.SUCCESS.info,
            "data": result.dict(),
        }
        return (
            JSONResponse(
                status_code=200,
                content=body,
            )
        )
    except HTTPException as e:
        status_enum = ResponseStatus.from_http_code(e.status_code)
        body = {
            "tid": int(time.time() * 1000),
            "status": status_enum.info,
            "data": {},
        }
        return (
            JSONResponse(
                status_code=e.status_code,
                content=body,
            )
        )
    except Exception as e:
        if ctx.log:
            ctx.log.error(f"Unexpected error in update_ctg: {e}")
        status_enum = ResponseStatus.SERVER_ERROR
        body = {
            "tid": int(time.time() * 1000),
            "status": status_enum.info,
            "data": {},
        }
        return (
            JSONResponse(
                status_code=500,
                content=body,
            )
        )


@router.post("/delete")
async def delete_ctg(request: Request, payload: CtgDeleteRequest, _=Depends(require_user)):
    ctx = request.app.state.ctx
    try:
        result = ctg_service.delete_ctg(ctx, payload.id)
        body = {
            "tid": int(time.time() * 1000),
            "status": ResponseStatus.SUCCESS.info,
            "data": result,
        }
        return (
            JSONResponse(
                status_code=200,
                content=body,
            )
        )
    except HTTPException as e:
        status_enum = ResponseStatus.from_http_code(e.status_code)
        body = {
            "tid": int(time.time() * 1000),
            "status": status_enum.info,
            "data": {},
        }
        return (
            JSONResponse(
                status_code=e.status_code,
                content=body,
            )
        )
    except Exception as e:
        if ctx.log:
            ctx.log.error(f"Unexpected error in delete_ctg: {e}")
        status_enum = ResponseStatus.SERVER_ERROR
        body = {
            "tid": int(time.time() * 1000),
            "status": status_enum.info,
            "data": {},
        }
        return (
            JSONResponse(
                status_code=500,
                content=body,
            )
        )
