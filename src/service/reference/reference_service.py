import json
from pathlib import Path

from src.app_context import AppContext
from src.service.reference.reference_schema import (
	RefCreateRequest,
	RefListItem,
	RefListResponse,
	RefResponse,
	RefUpdateRequest,
)


SAMPLE_AI_DATA_PATH = Path(__file__).resolve().parents[3] / "ref-ai-data-sample.json"
SAMPLE_UNIX_TIMESTAMP = 1774180800


def _load_sample_ai_data() -> dict:
	with SAMPLE_AI_DATA_PATH.open("r", encoding="utf-8") as file:
		return json.load(file)


def _get_sample_reference_base() -> dict:
	return {
		"id": 1,
		"userId": 1,
		"ctgId": 1,
		"imgUrl": "/legacy/hot1.jpg",
		"title": "하이앵글 컵포즈",
		"desc": "위에서 아래를 극단적으로 내려다보는 하이 앵글(High Angle)로 촬영하여, 얼굴을 가린 컵을 강조하고 신체 비율을 독특하게 왜곡한 구도입니다.",
		"categoryName": "reference",
		"useCnt": 0,
		"kwd": ["K001", "K002"],
		"aiDocId": "ai-doc-sample-001",
		"expWeight": 0,
		"pri": 0,
		"cDate": SAMPLE_UNIX_TIMESTAMP,
		"uDate": SAMPLE_UNIX_TIMESTAMP,
	}


def list_references(
	ctx: AppContext,
	page: int = 1,
	limit: int = 20,
	ctg_id: int | None = None,
) -> RefListResponse:
	"""테스트용 레퍼런스 이미지 목록 조회"""
	if ctx.log:
		ctx.log.debug(f"Ref list requested | page={page} limit={limit} ctg_id={ctg_id}")

	base_item = RefListItem(**_get_sample_reference_base())
	items = [base_item]
	if ctg_id:
		items = [item for item in items if item.ctgId == ctg_id]

	start = max((page - 1) * limit, 0)
	end = start + max(limit, 0)
	paged_items = items[start:end]

	return RefListResponse(
		items=paged_items,
		total=len(items),
		page=page,
		limit=limit,
	)


def get_reference(ctx: AppContext, reference_id: int) -> RefResponse:
	"""테스트용 레퍼런스 이미지 상세 정보 조회"""
	if ctx.log:
		ctx.log.debug(f"Ref requested | reference_id={reference_id}")

	return RefResponse(
		**_get_sample_reference_base(),
		ai_data=_load_sample_ai_data(),
	)


def create_reference(ctx: AppContext, payload: RefCreateRequest) -> RefResponse:
	"""테스트용 레퍼런스 이미지 등록"""
	if ctx.log:
		ctx.log.debug(f"Ref create requested | ctgId={payload.ctgId}")

	base = _get_sample_reference_base()
	base.update(
		{
			"userId": payload.userId,
			"ctgId": payload.ctgId,
			"imgUrl": payload.imgUrl,
			"title": payload.title or base["title"],
			"desc": payload.desc,
			"kwd": payload.kwd or [],
			"aiDocId": payload.aiDocId,
			"expWeight": payload.expWeight,
			"pri": payload.pri,
		}
	)

	return RefResponse(**base, ai_data=_load_sample_ai_data())


def update_reference(ctx: AppContext, payload: RefUpdateRequest) -> RefResponse:
	"""테스트용 레퍼런스 이미지 수정"""
	if ctx.log:
		ctx.log.debug(f"Ref update requested | id={payload.id}")

	base = _get_sample_reference_base()
	base["id"] = payload.id

	if payload.ctgId is not None:
		base["ctgId"] = payload.ctgId
	if payload.imgUrl is not None:
		base["imgUrl"] = payload.imgUrl
	if payload.title is not None:
		base["title"] = payload.title
	if payload.desc is not None:
		base["desc"] = payload.desc
	if payload.kwd is not None:
		base["kwd"] = payload.kwd
	if payload.aiDocId is not None:
		base["aiDocId"] = payload.aiDocId
	if payload.expWeight is not None:
		base["expWeight"] = payload.expWeight
	if payload.pri is not None:
		base["pri"] = payload.pri

	return RefResponse(**base, ai_data=_load_sample_ai_data())


def delete_reference(ctx: AppContext, reference_id: int) -> dict:
	"""테스트용 레퍼런스 이미지 삭제"""
	if ctx.log:
		ctx.log.debug(f"Ref delete requested | id={reference_id}")

	return {
		"status": "success",
		"id": reference_id,
	}

