from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
import time

from src.common.common_codes import ResponseStatus

from src.service.auth.jwt_auth import require_user
from src.service.tag import tag_service
from src.service.tag.tag_schema import (
	TagCreateRequest,
	TagDeleteRequest,
	TagGetRequest,
	TagListRequest,
	TagUpdateRequest,
)

router = APIRouter(prefix="/api/tag", tags=["Tag"])


@router.post("/list")
async def list_tags(request: Request, payload: TagListRequest, _=Depends(require_user)):
	"""태그 목록 조회"""
	ctx = request.app.state.ctx
	try:
		result = tag_service.list_tags(
			ctx,
			page=payload.page,
			limit=payload.limit,
			parent_code=payload.parentCode,
		)
		body = {
			"tid": int(time.time() * 1000),
			"status": ResponseStatus.SUCCESS.info,
			"data": result.dict() if hasattr(result, "dict") else result,
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
			ctx.log.error(f"Unexpected error in list_tags: {e}")
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
async def get_tag(request: Request, payload: TagGetRequest, _=Depends(require_user)):
	"""태그 상세 조회"""
	ctx = request.app.state.ctx
	try:
		result = tag_service.get_tag(ctx, payload.id)
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
			ctx.log.error(f"Unexpected error in get_tag: {e}")
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
async def create_tag(request: Request, payload: TagCreateRequest, _=Depends(require_user)):
	"""태그 생성"""
	ctx = request.app.state.ctx
	try:
		result = tag_service.create_tag(ctx, payload)
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
			ctx.log.error(f"Unexpected error in create_tag: {e}")
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
async def update_tag(request: Request, payload: TagUpdateRequest, _=Depends(require_user)):
	"""태그 수정"""
	ctx = request.app.state.ctx
	try:
		result = tag_service.update_tag(ctx, payload)
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
			ctx.log.error(f"Unexpected error in update_tag: {e}")
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
async def delete_tag(request: Request, payload: TagDeleteRequest, _=Depends(require_user)):
	"""태그 삭제"""
	ctx = request.app.state.ctx
	try:
		result = tag_service.delete_tag(ctx, payload.id)
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
			ctx.log.error(f"Unexpected error in delete_tag: {e}")
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
