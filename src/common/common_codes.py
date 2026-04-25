from enum import Enum

class ResponseStatus(Enum):
    # (HTTP 상태코드, 내부 코드, 메시지)
    SUCCESS      = (200, "S0000", "성공")
    BAD_REQUEST  = (400, "E0001", "잘못된 요청입니다")
    UNAUTHORIZED = (401, "E0002", "인증이 필요합니다")
    FORBIDDEN    = (403, "E0003", "접근이 거부되었습니다")
    NOT_FOUND    = (404, "E0004", "리소스를 찾을 수 없습니다")
    CONFLICT     = (409, "E0005", "이미 존재하는 리소스입니다")
    TIMEOUT      = (408, "E0009", "응답 시간이 초과되었습니다")
    SERVER_ERROR = (500, "E0500", "서버 내부 오류가 발생했습니다")

    def __init__(self, http_code, code, msg):
        self.http_code = http_code
        self.info = {"code": code, "msg": msg}

    @classmethod
    def from_http_code(cls, http_code):
        """HTTP 코드로 해당 Enum 상수를 찾는 팩토리 메서드"""
        # 다음은 파이썬의 Generator expression을 사용한 효율적인 검색입니다.
        return next((status for status in cls if status.http_code == http_code), cls.SERVER_ERROR)