# src/service/logging/logging_api.py
from fastapi import APIRouter, Request, status, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
import asyncio
from pathlib import Path
import orjson
from src.utils.rabbitmq_utils import rmq_send_response

router = APIRouter(prefix="/api/system", tags=["System"])

class LogMessage(BaseModel):
    level: str = "WARNING"
    service: Optional[str] = "web-client"
    duration: float = 1.0

async def generate_simulation_logs(ctx, log_data: LogMessage):
    queue_name = "tryangle-send-logs"
    data_path = Path(__file__).resolve().parents[3] / "transformed_hex_payloads.jsonl"

    if not data_path.exists():
        ctx.log.error("LogProducer", f"JSONL file not found: {data_path}")
        return

    total_lines = 0
    with data_path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                total_lines += 1

    delay = 0.0
    if log_data.duration and total_lines > 0:
        delay = log_data.duration / total_lines

    with data_path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue

            try:
                payload = orjson.loads(line)
            except orjson.JSONDecodeError as exc:
                ctx.log.error("LogProducer", f"Invalid JSONL line: {exc}")
                continue

            await rmq_send_response(ctx, queue_name, payload)
            if delay > 0:
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

