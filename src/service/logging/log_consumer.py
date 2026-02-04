# src/service/logging/log_consumer.py
import orjson
from datetime import datetime

async def handle_log_message(ctx, msg: dict):
    """
    큐 'tryangle-send-logs' 에서 들어온 로그 메시지를 처리하는 핸들러
    
    메시지 구조 예시:
    {
        "hd": { "event": "system.log" },
        "bd": { "level": "error", "message": "Something went wrong", "tid": "..." }
    }
    """
    try:
        # ctx.log.info("LogConsumer", f"Received log message: {msg}")

        hd = msg.get("hd", {})
        bd = msg.get("bd", {})
        
        log_entry = {
            "tid": hd.get("tid"),
            "level": bd.get("level", "info"),
            "service": bd.get("service", "unknown"),
            "category": bd.get("category"),
            "code": bd.get("code"),
            "details": bd.get("details"),
            "message": bd.get("message", "") # optional
        }
        
        # MongoDB에 저장 (컬렉션: system_logs)
        if ctx.mongo_handler:
            db = ctx.mongo_handler.get_db()
            collection = db["system_logs"]
            collection.insert_one(log_entry)
            
            # _id는 로깅 시 문자열로 변환 (직렬화 오류 방지)
            log_copy = log_entry.copy()
            log_copy["_id"] = str(log_copy["_id"])
            ctx.log.debug("LogConsumer", f"Log saved to MongoDB: {log_copy}")
        
        return {"status": "success", "msg": "Log processed"}

    except Exception as e:
        ctx.log.error("LogConsumer", f"Error processing log message: {e}")
        return {"status": "error", "msg": str(e)}
