import json
from pathlib import Path

from src.app_context import AppContext
from src.service.reference.reference_schema import ReferenceListItem, ReferenceListResponse, ReferenceResponse


SAMPLE_AI_DATA_PATH = Path(__file__).resolve().parents[3] / "ref-ai-data-sample.json"
SAMPLE_UNIX_TIMESTAMP = 1774180800


def _load_sample_ai_data() -> dict:
	with SAMPLE_AI_DATA_PATH.open("r", encoding="utf-8") as file:
		return json.load(file)


def _get_sample_reference_base() -> dict:
	return {
		"url": "https://example.com/reference/hot1.jpg",
		"title": "Sample Reference Image",
		"desc": "테스트용 레퍼런스 이미지 상세 정보",
		"category": "reference",
		"u_date": SAMPLE_UNIX_TIMESTAMP,
		"c_date": SAMPLE_UNIX_TIMESTAMP,
	}


def list_references(ctx: AppContext, page: int = 1, limit: int = 20) -> ReferenceListResponse:
	"""테스트용 레퍼런스 이미지 목록 조회"""
	if ctx.log:
		ctx.log.debug(f"Reference list requested | page={page} limit={limit}")

	items = [ReferenceListItem(**_get_sample_reference_base())]
	start = max((page - 1) * limit, 0)
	end = start + max(limit, 0)
	paged_items = items[start:end]

	return ReferenceListResponse(
		items=paged_items,
		total=len(items),
		page=page,
		limit=limit,
	)


def get_reference(ctx: AppContext, reference_id: str) -> ReferenceResponse:
	"""테스트용 레퍼런스 이미지 상세 정보 조회"""
	if ctx.log:
		ctx.log.debug(f"Reference requested | reference_id={reference_id}")

	return ReferenceResponse(
		**_get_sample_reference_base(),
		ai_data=_load_sample_ai_data(),
	)

