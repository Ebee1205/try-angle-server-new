# TryAngle API Specification

본 문서는 현재 서버에 실제 등록된 라우터 기준의 API 명세입니다.

## 공통 응답 형식

모든 API는 공통 응답 포맷을 사용합니다.

```json
{
  "tid": 1705298638704,
  "status": {
    "code": "S0000",
    "msg": "성공"
  },
  "data": {}
}
```

## 설계 규칙

- 식별자 전달: 주요 id 값은 Request Body로 전달
- 시간 형식: cDate, uDate 등은 Unix Timestamp(BigInt)
- 메타데이터 저장소: RDBMS 중심, 파일은 Cloudflare R2 사용

## 현재 활성 엔드포인트

아래 목록은 실제 소스코드에 구현된 라우터를 기준으로 작성되었습니다.

### 1) Auth

- POST /api/auth/signup - 회원가입
- POST /api/auth/login - 로그인 (JWT 발급)
- GET /api/auth/me - 현재 사용자 정보 조회 (JWT 인증 필요)
- POST /api/auth/exists - 사용자 ID 존재 여부 체크
- POST /api/auth/checkEmail - 이메일 중복 체크
- POST /api/auth/logout - 로그아웃 (JWT 인증 필요)
- POST /api/auth/update - 사용자 정보 수정 (JWT 인증 필요)

### 2) Files

- POST /api/files/create - 파일 업로드 (multipart/form-data)
- POST /api/files/list - 파일 목록 조회 (JWT 인증 필요)
- POST /api/files/get - 파일 메타 정보 조회 (JWT 인증 필요)
- POST /api/files/getPresigned - S3 Presigned URL 조회 (JWT 인증 필요)
- POST /api/files/delete - 파일 삭제 (JWT 인증 필요)

### 3) Category

- POST /api/ctg/list - 카테고리 목록 조회 (JWT 인증 필요)
- POST /api/ctg/get - 카테고리 상세 조회 (JWT 인증 필요)
- POST /api/ctg/create - 카테고리 등록 (JWT 인증 필요)
- POST /api/ctg/update - 카테고리 수정 (JWT 인증 필요)
- POST /api/ctg/delete - 카테고리 삭제 (JWT 인증 필요)

### 4) Reference

- POST /api/ref/list - 레퍼런스 이미지 목록 조회 (JWT 인증 필요, 필터: ctgId, title, kwd)
- POST /api/ref/get - 레퍼런스 이미지 상세 조회 (JWT 인증 필요)
- POST /api/ref/create - 레퍼런스 이미지 등록 (JWT 인증 필요)
- POST /api/ref/update - 레퍼런스 이미지 수정 (JWT 인증 필요)
- POST /api/ref/delete - 레퍼런스 이미지 삭제 (JWT 인증 필요)

### 5) Product

- POST /api/prod/list - 상품 목록 조회 (JWT 인증 필요, 필터: name, pStat)
- POST /api/prod/get - 상품 상세 조회 (JWT 인증 필요)
- POST /api/prod/create - 상품 등록 (Admin 권한 필요)
- POST /api/prod/update - 상품 수정 (Admin 권한 필요)
- POST /api/prod/delete - 상품 삭제 (Admin 권한 필요)

### 6) Session

- POST /api/session/list - 촬영 세션 목록 조회 (JWT 인증 필요, 필터: userId, imgId, sStat, sDate, eDate)
- POST /api/session/detail - 세션 상세 조회 (JWT 인증 필요, 권한 검증)
- POST /api/session/start - 촬영 세션 시작 (JWT 인증 필요)
- POST /api/session/end - 촬영 세션 종료 (JWT 인증 필요)

### 7) Snap

- POST /api/snap/list - 스냅 목록 조회 (JWT 인증 필요, 정렬/기간 필터 포함)
- POST /api/snap/get - 스냅 상세 조회 (JWT 인증 필요)
- POST /api/snap/create - 스냅 등록 (JWT 인증 필요)
- POST /api/snap/update - 스냅 수정 (Admin 권한 필요)
- POST /api/snap/delete - 스냅 삭제 (Admin 권한 필요)