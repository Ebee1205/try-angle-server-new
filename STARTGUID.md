## 개발 방식

- DI(Dependency Injection) 방식으로 구성되어 있습니다.
- 필요한 handler는 `app_context`에 추가해서 주입받는 형태로 작성합니다.
- 비즈니스 로직은 `src/service` 하위에서 구현합니다.

## 프로젝트 구조

서비스 코드는 기능별 디렉터리로 분리되어 있으며, 각 기능은 아래 구조를 기본으로 사용합니다.

- `_api`: FastAPI 라우터와 요청 진입점 담당
- `_service`: 실제 비즈니스 로직 담당
- `_schema`: 요청/응답 스키마 및 데이터 검증 담당

구조가 비교적 명확해서 각 도메인 디렉터리만 따라가면 흐름을 파악할 수 있습니다.

## 참고 문서

- 배포 방법: `ec2/tryangle-web.service`
- API 명세: `src/service/API.md`, `try-angle-server.postman_collection.json`
- database: `src/sql/DATABASE.md`

## 규격

- 카카오톡으로 전달받은 csv(엑셀)파일이 최신, API명세는 md와 postman파일로 대체