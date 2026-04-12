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
		"id": "img-sample-001",
		"userId": "user-sample-001",
		"ctgId": "ctg-reference",
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

