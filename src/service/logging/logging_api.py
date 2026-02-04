# src/service/logging/logging_api.py
from fastapi import APIRouter, Request, status, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import random
import asyncio
from src.utils.rabbitmq_utils import rmq_send_response

router = APIRouter(prefix="/system", tags=["System"])

class LogMessage(BaseModel):
    level: str = "WARNING"
    service: Optional[str] = "web-client"
    duration: float = 1.0

async def generate_simulation_logs(ctx, log_data: LogMessage):
    total_frames = int(log_data.duration * 30)
    delay = 1.0 / 30.0
    queue_name = "tryangle-send-logs"

    for _ in range(total_frames):
        details = {
            "temp": round(random.uniform(40.0, 90.0), 1),
            "cpu": round(random.uniform(10.0, 99.9), 1),
            "fps_drop": random.choice([True, False])
        }

        payload = {
            "hd": {
                "event": "system.log",
                "tid": int(datetime.now().timestamp() * 1000)
            },
            "bd": {
                "level": log_data.level,
                "category": "Thermal",
                "code": "HIGH_TEMPERATURE",
                "service": log_data.service,
                "details": details
            }
        }
        
        await rmq_send_response(ctx, queue_name, payload)
        await asyncio.sleep(delay)

@router.post("/log", status_code=status.HTTP_202_ACCEPTED)
async def send_log(request: Request, log_data: LogMessage, background_tasks: BackgroundTasks):
    """
    클라이언트 로그를 수신하여 RabbitMQ로 전송합니다.
    (Thermal 이벤트 시뮬레이션 데이터 생성 - 30fps)
    """
    ctx = request.app.state.ctx
    background_tasks.add_task(generate_simulation_logs, ctx, log_data)
    
    return {
        "status": "accepted", 
        "detail": f"Started generating logs for {log_data.duration}s",
        "count": int(log_data.duration * 30)
    }
    
@router.get("/search", status_code=status.HTTP_200_OK)
async def search_logs(
    request: Request,
    start_time: int,  # ms timestamp
    end_time: int,    # ms timestamp
    service: Optional[str] = None,
    level: Optional[str] = None,
    limit: int = 100
):
    """
    MongoDB에서 특정 시간 범위의 로그를 검색합니다.
    """
    ctx = request.app.state.ctx
    
    if not ctx.mongo_handler:
        return {"status": "error", "message": "MongoDB not initialized"}
        
    db = ctx.mongo_handler.get_db()
    collection = db["system_logs"]
    
    # 쿼리 구성
    query = {
        "tid": {
            "$gte": start_time,
            "$lte": end_time
        }
    }
    
    if service:
        query["service"] = service
        
    if level:
        query["level"] = level
        
    try:
        cursor = collection.find(query).sort("tid", -1).limit(limit)
        logs = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])  # ObjectId 문자열 변환
            logs.append(doc)
            
        return {"status": "success", "count": len(logs), "data": logs}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

