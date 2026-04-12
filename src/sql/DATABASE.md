확정된 ERD 구조와 요구사항(축약형 네이밍, 유닉스 타임스탬프 적용)을 바탕으로 상세한 데이터베이스 설계 문서(Markdown)를 작성해 드립니다.

---

# TryAngle 데이터베이스 설계 명세서 (v1.0.0)

본 문서는 **TryAngle** 서비스의 백엔드 인프라 중 RDBMS(PostgreSQL/MySQL 등) 영역의 스키마 설계를 기술합니다. 실시간 AI 분석 데이터는 **MongoDB**와 **Cloudflare R2**에 분산 저장하며, 본 DB는 메타데이터 관리 및 관계 정의를 핵심으로 합니다.

## 1. 공통 설정
* **Timestamp:** 모든 날짜 데이터(`cDate`, `uDate`)는 **Unix Timestamp (BigInt/Integer)** 형식을 사용합니다.
* **Character Set:** `utf8mb4` (다국어 및 이모지 지원)
* **Naming Convention:** * 기본 테이블: `tb_{name}`
    * 매핑 테이블: `mtb_{name}`
    * 생성일/수정일: `cDate` / `uDate`

---

## 2. 테이블 정의

### 2.1 사용자 정보 (`tb_user`)
사용자의 기본 계정 정보 및 권한을 관리합니다.

| 컬럼명 | 타입 | 제약사항 | 설명 |
| :--- | :--- | :--- | :--- |
| **id** | varchar | PK | 사용자 고유 식별자 |
| **email** | varchar | Unique, Not Null | 로그인 이메일 |
| **password** | varchar | - | 암호화된 비밀번호 |
| **name** | varchar | - | 실명 |
| **nickname** | varchar | - | 서비스 내 별명 |
| **phone** | varchar | - | 연락처 |
| **emailConf** | varchar | Default: "2" | 이메일 인증 여부 (1: 인증, 2: 미인증) |
| **desc** | text | - | 프로필 자기소개 |
| **fileId** | varchar | - | 프로필 이미지 R2 ID |
| **role** | enum | Default: "CLIENT" | 권한 (SUPER_ADMIN, ADMIN, CLIENT) |
| **extra** | json | - | 기타 부가 정보 (Key-Value) |
| **cDate** | bigint | - | 생성일 (Unix Time) |
| **uDate** | bigint | - | 수정일 (Unix Time) |

### 2.2 이미지 카테고리 (`tb_img_ctg`)
이미지의 대분류를 관리합니다.

| 컬럼명 | 타입 | 제약사항 | 설명 |
| :--- | :--- | :--- | :--- |
| **id** | varchar | PK | 카테고리 고유 식별자 |
| **name** | varchar | Not Null | 카테고리 명칭 |
| **cDate** | bigint | - | 생성일 (Unix Time) |
| **uDate** | bigint | - | 수정일 (Unix Time) |

### 2.3 이미지 데이터 (`tb_img`)
이미지의 메타데이터 및 AI 분석 결과 연결 고리를 관리합니다.

| 컬럼명 | 타입 | 제약사항 | 설명 |
| :--- | :--- | :--- | :--- |
| **id** | varchar | PK | 이미지 고유 식별자 |
| **userId** | varchar | FK (tb_user) | 등록자 ID |
| **ctgId** | varchar | FK (tb_img_ctg) | 카테고리 ID |
| **imgUrl** | varchar | Not Null | Cloudflare R2 이미지 주소 |
| **title** | varchar | - | 이미지 제목 |
| **desc** | text | - | 이미지 설명 |
| **useCnt** | int | Default: 0 | 총 사용 횟수 |
| **kwd** | json | - | 키워드 코드 리스트 (`["K001", "K002"]`) |
| **aiDocId** | varchar | - | **MongoDB Document ID** (실시간 분석 데이터) |
| **expWeight** | float | Default: 0 | 노출 가중치 (추천 알고리즘용) |
| **pri** | int | Default: 0 | 우선순위 (정렬용) |
| **cDate** | bigint | - | 생성일 (Unix Time) |
| **uDate** | bigint | - | 수정일 (Unix Time) |

### 2.4 태그 관리 (`tb_tag`)
계층 구조를 가진 서비스 내 태그 시스템입니다.

| 컬럼명 | 타입 | 제약사항 | 설명 |
| :--- | :--- | :--- | :--- |
| **id** | varchar | PK | 태그 고유 식별자 |
| **userId** | varchar | FK (tb_user) | 태그 생성자 ID |
| **parentCode** | varchar | - | 상위 태그 코드 (Self-referencing) |
| **code** | varchar | Unique | 태그 식별 코드 |
| **tagName** | varchar | Not Null | 태그 표시 명칭 |
| **cDate** | bigint | - | 생성일 (Unix Time) |
| **uDate** | bigint | - | 수정일 (Unix Time) |

---

## 3. 매핑 테이블 (Mapping Tables)

### 3.1 북마크 (`mtb_bookmark`)
사용자와 이미지 간의 북마크 관계를 관리합니다.

| 컬럼명 | 타입 | 제약사항 | 설명 |
| :--- | :--- | :--- | :--- |
| **id** | varchar | PK | 매핑 고유 ID |
| **userId** | varchar | FK (tb_user) | 북마크한 사용자 |
| **imgId** | varchar | FK (tb_img) | 대상 이미지 |
| **cDate** | bigint | - | 북마크 일시 (Unix Time) |

### 3.2 이미지-태그 매핑 (`mtb_img_tag`)
이미지에 부여된 다중 태그 관계를 관리합니다.

| 컬럼명 | 타입 | 제약사항 | 설명 |
| :--- | :--- | :--- | :--- |
| **id** | varchar | PK | 매핑 고유 ID |
| **imgId** | varchar | FK (tb_img) | 대상 이미지 |
| **tagId** | varchar | FK (tb_tag) | 연결된 태그 |

* **Unique Index:** `(imgId, tagId)` 조합은 중복될 수 없습니다.

---

## 4. 특이사항 및 구현 가이드
1.  **실시간 데이터 연동:** `tb_img` 테이블의 `aiDocId`를 통해 MongoDB의 `img_analysis` 컬렉션에 접근합니다. 해당 컬렉션에는 133포인트 Hex String 등 대용량 데이터가 포함됩니다.
2.  **데이터 무결성:** 모든 매핑 테이블(`mtb_`)은 데이터 삭제 시 정책(Cascade 혹은 Soft Delete)을 프로젝트 성격에 맞춰 결정해야 합니다.
3.  **성능 최적화:** 자주 조회되는 `useCnt`, `expWeight`, `pri` 컬럼에는 복합 인덱스 설정을 권장합니다.