"""
Reference Service
참고용 이미지 관리 비즈니스 로직
"""

import sys
import os
from typing import List, Optional, Dict
from datetime import datetime
from fastapi.responses import JSONResponse

from service.reference.pinterest_crawler import SimplePinterestClient
from service.reference.reference_model import (
    ReferenceModel,
    ReferenceCreateRequest,
    ReferenceResponse,
    PinterestSearchResponse
)

# 간단한 인메모리 저장소 (나중에 DB로 교체 가능)
_reference_storage: Dict[int, ReferenceModel] = {}
_reference_id_counter = 1


class ReferenceService:
    """Reference 관리 서비스"""
    
    def __init__(self, ctx=None):
        self.ctx = ctx
        self.pinterest_client = SimplePinterestClient()
    
    async def search_pinterest(
        self,
        category: str,
        limit: int = 10,
        auto_save: bool = False
    ) -> JSONResponse:
        """
        Pinterest에서 카테고리로 이미지 검색
        
        Args:
            category: 검색 카테고리 (전신, 셀카, 카페 등)
            limit: 반환할 이미지 개수
            auto_save: 자동 저장 여부
            
        Returns:
            검색 결과 (이미지 URL 리스트)
        """
        try:
            if self.ctx:
                self.ctx.log.info(f"[START] Pinterest search: {category} (limit={limit})")
            else:
                print(f"[START] Pinterest search: {category} (limit={limit})")
            
            # Pinterest 크롤링
            images = self.pinterest_client.search_references(category, limit)
            
            if not images:
                return JSONResponse({
                    "images": [],
                    "total_count": 0,
                    "source": "pinterest",
                    "message": f"No images found for '{category}'"
                }, status_code=404)
            
            # 자동 저장
            if auto_save:
                for img in images:
                    await self._save_reference(
                        image_url=img["url"],
                        source="pinterest",
                        external_id=img.get("external_id"),
                        category=category
                    )
            
            if self.ctx:
                self.ctx.log.info(f"[COMPLETE] Pinterest search completed: {len(images)} images collected")
            else:
                print(f"[COMPLETE] Pinterest search completed: {len(images)} images collected")
            
            return JSONResponse({
                "images": images,
                "total_count": len(images),
                "source": "pinterest"
            })
        
        except Exception as e:
            if self.ctx:
                self.ctx.log.error(f"[ERROR] Pinterest search failed: {e}")
            else:
                print(f"[ERROR] Pinterest search failed: {e}")
            
            import traceback
            traceback.print_exc()
            
            return JSONResponse({
                "error": str(e),
                "images": [],
                "total_count": 0,
                "source": "pinterest"
            }, status_code=500)
    
    async def _save_reference(
        self,
        image_url: str,
        source: str,
        category: str,
        external_id: Optional[str] = None,
        popularity_score: int = 0
    ) -> ReferenceResponse:
        """
        Reference 저장
        """
        global _reference_id_counter
        
        ref = ReferenceModel(
            id=_reference_id_counter,
            image_url=image_url,
            source=source,
            external_id=external_id,
            category=category,
            popularity_score=popularity_score,
            is_active=True,
            created_at=datetime.now()
        )
        
        _reference_storage[_reference_id_counter] = ref
        _reference_id_counter += 1
        
        if self.ctx:
            self.ctx.log.debug(f"[SAVE] Reference saved: {ref.id}")
        
        return self._convert_to_response(ref)
    
    async def get_references(
        self,
        category: Optional[str] = None,
        is_active: bool = True,
        limit: int = 50,
        offset: int = 0
    ) -> JSONResponse:
        """
        저장된 Reference 조회
        """
        try:
            filtered = []
            
            for ref in _reference_storage.values():
                # 필터링
                if not is_active or not ref.is_active:
                    continue
                
                if category and ref.category != category:
                    continue
                
                filtered.append(ref)
            
            # 생성일 역순 정렬
            filtered.sort(key=lambda x: x.created_at, reverse=True)
            
            # 페이징
            total = len(filtered)
            paginated = filtered[offset:offset + limit]
            
            if self.ctx:
                self.ctx.log.info(f"[LIST] References retrieved: total={total}, returned={len(paginated)}")
            
            return JSONResponse({
                "references": [self._convert_to_response(ref) for ref in paginated],
                "total_count": total,
                "limit": limit,
                "offset": offset
            })
        
        except Exception as e:
            if self.ctx:
                self.ctx.log.error(f"[ERROR] Reference retrieval failed: {e}")
            
            return JSONResponse({
                "error": str(e)
            }, status_code=500)
    
    async def get_reference_by_category(
        self,
        category: str,
        limit: int = 20
    ) -> JSONResponse:
        """
        카테고리별 Reference 조회
        """
        try:
            if self.ctx:
                self.ctx.log.info(f"[FILTER] References by category: {category}")
            
            filtered = [
                ref for ref in _reference_storage.values()
                if ref.is_active and ref.category == category
            ]
            
            # 인기도 순 정렬
            filtered.sort(key=lambda x: x.popularity_score, reverse=True)
            
            return JSONResponse({
                "category": category,
                "references": [
                    self._convert_to_response(ref)
                    for ref in filtered[:limit]
                ],
                "total_count": len(filtered)
            })
        
        except Exception as e:
            if self.ctx:
                self.ctx.log.error(f"[ERROR] Category filter failed: {e}")
            
            return JSONResponse({
                "error": str(e)
            }, status_code=500)
    
    async def create_reference(
        self,
        request: ReferenceCreateRequest
    ) -> JSONResponse:
        """
        Reference 수동 생성
        """
        try:
            if self.ctx:
                self.ctx.log.info(f"[CREATE] Reference creation: {request.category}")
            
            # 중복 체크 (external_id)
            if request.external_id:
                for ref in _reference_storage.values():
                    if ref.external_id == request.external_id and ref.source == request.source:
                        return JSONResponse({
                            "error": "Reference already exists (duplicate)",
                            "existing_id": ref.id
                        }, status_code=409)
            
            response = await self._save_reference(
                image_url=request.image_url,
                source=request.source,
                category=request.category,
                external_id=request.external_id,
                popularity_score=request.popularity_score
            )
            
            return JSONResponse({
                "reference": response,
                "message": "Reference saved successfully"
            }, status_code=201)
        
        except Exception as e:
            if self.ctx:
                self.ctx.log.error(f"[ERROR] Reference creation failed: {e}")
            
            return JSONResponse({
                "error": str(e)
            }, status_code=500)
    
    async def update_reference(
        self,
        ref_id: int,
        **kwargs
    ) -> JSONResponse:
        """
        Reference 업데이트
        """
        try:
            if ref_id not in _reference_storage:
                return JSONResponse({
                    "error": "Reference not found"
                }, status_code=404)
            
            ref = _reference_storage[ref_id]
            
            # 업데이트 가능한 필드
            updatable_fields = ['is_active', 'popularity_score', 'category']
            
            for field in updatable_fields:
                if field in kwargs and kwargs[field] is not None:
                    setattr(ref, field, kwargs[field])
            
            if self.ctx:
                self.ctx.log.info(f"[UPDATE] Reference updated: {ref_id}")
            
            return JSONResponse({
                "reference": self._convert_to_response(ref),
                "message": "Reference updated successfully"
            })
        
        except Exception as e:
            if self.ctx:
                self.ctx.log.error(f"[ERROR] Reference update failed: {e}")
            
            return JSONResponse({
                "error": str(e)
            }, status_code=500)
    
    async def delete_reference(self, ref_id: int) -> JSONResponse:
        """
        Reference 삭제 (soft delete)
        """
        try:
            if ref_id not in _reference_storage:
                return JSONResponse({
                    "error": "Reference not found"
                }, status_code=404)
            
            # Soft delete (is_active = False)
            _reference_storage[ref_id].is_active = False
            
            if self.ctx:
                self.ctx.log.info(f"[DELETE] Reference deleted: {ref_id}")
            
            return JSONResponse({
                "message": "Reference deleted successfully",
                "id": ref_id
            })
        
        except Exception as e:
            if self.ctx:
                self.ctx.log.error(f"[ERROR] Reference deletion failed: {e}")
            
            return JSONResponse({
                "error": str(e)
            }, status_code=500)
    
    @staticmethod
    def _convert_to_response(ref: ReferenceModel) -> dict:
        """Model을 Response로 변환"""
        return {
            "id": ref.id,
            "image_url": ref.image_url,
            "source": ref.source,
            "category": ref.category,
            "popularity_score": ref.popularity_score,
            "is_active": ref.is_active,
            "created_at": ref.created_at.isoformat() if ref.created_at else None,
            "external_id": ref.external_id
        }


# 글로벌 서비스 인스턴스
_reference_service: Optional[ReferenceService] = None


def get_reference_service(ctx=None) -> ReferenceService:
    """Reference Service 인스턴스 획득"""
    global _reference_service
    if _reference_service is None:
        _reference_service = ReferenceService(ctx)
    return _reference_service
