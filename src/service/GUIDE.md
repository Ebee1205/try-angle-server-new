## Keypoint (kp) 규격 및 코드

---

포즈의 좌표값(x, y)과 신뢰도(confidence)를 양자화하여 압축 전송하는 규격입니다.

### **[kp] 인코딩 규격**

| 항목 | 상세 내용 | 비고 |
| --- | --- | --- |
| **데이터 포맷** | 가변 길이 Hex String | 4자리 Hex × (Keypoint 개수 × 3) |
| **데이터 구조** | `[x, y, confidence]` 순서 반복 | 1개 포인트당 12자리 Hex 할당 |
| **양자화 방식** | (Original Value × 10,000) → 정수화 → Hex 변환 | 소수점 4자리까지 보존 |
| **결측치 처리** | 측정 불가 시 해당 영역을 `0000` 또는 제외 처리 | 디코딩 시 길이 체크 필요 |

**인덱스 매핑 (DWPose-M 133 Points)**

| **인덱스 범위** | **부위** | **개수** | **비고** |
| --- | --- | --- | --- |
| **0 ~ 16** | **Body** | 17 | COCO 17 표준 포맷 |
| **17 ~ 22** | **Feet** | 6 | 발 세부 정보 |
| **23 ~ 90** | **Face** | 68 | 얼굴 랜드마크 |
| **91 ~ 111** | **Left Hand** | 21 | 왼손 마디 및 관절 |
| **112 ~ 132** | **Right Hand** | 21 | 오른손 마디 및 관절 |

### **[kp] 디코딩 예제 코드 (Python)**

```python
def decode_kp_hex(kp_hex):
    """
    Keypoint HEX 데이터를 좌표 리스트로 복원
    """
    kp_flat = []
    # 1. 4자리(Chunk)씩 잘라 정수로 변환 후 10,000으로 나눠 Float 복원 
    for i in range(0, len(kp_hex), 4):
        int_val = int(kp_hex[i:i+4], 16)
        kp_flat.append(int_val / 10000.0)

    # 2. [x, y, c] 구조로 3개씩 묶어 133개 키포인트 생성 
    kp_structured = [kp_flat[i:i+3] for i in range(0, len(kp_flat), 3)]
    
    return kp_structured
```

## Pose Vector (pv) 규격 및 코드

---

각 키포인트별 각도 오차(Diff)와 부위별 중요도(Weight)를 결합하여 전송하는 규격입니다.

### **[pv] 인코딩 규격**

| 항목 | 상세 내용 | 비고 |
| --- | --- | --- |
| **데이터 포맷** | 고정 길이 Hex String (1,064자) | 8자리 Hex × 133개 키포인트 |
| **데이터 구조** | `[Diff (4자리)]` + `[Weight (4자리)]` | 1개 포인트당 8자리 Hex (4바이트) |
| **Diff 영역** | (각도 차이 $0.0^\circ \sim 360.0^\circ$) × 100 → Hex | 데이터 없을 경우 **`FFFF`** 로 채움 |
| **Weight 영역** | (가중치 $0.0 \sim 1.5$) × 100 → Hex | 데이터 없을 경우 **`0000`** 으로 채움 |
| **특이사항** | `FFFF` 수신 시 프론트엔드 시각화 제외 가능 | 데이터 유무 판단 기준 |

### **[pv] 디코딩 예제 코드 (Python)**

```python
def decode_pv_hex(pv_hex):
    """
    Pose Vector HEX 데이터를 Diff와 Weight 리스트로 복원
    """
    pv_results = []
    # 8자리씩 잘라서 분석 (Diff 4자 + Weight 4자)
    for i in range(0, len(pv_hex), 8):
        chunk = pv_hex[i:i+8]
        diff_hex = chunk[:4]
        weight_hex = chunk[4:]
        
        # Diff 복원 (FFFF인 경우 None 처리)
        if diff_hex.upper() == "FFFF":
            diff = None
        else:
            diff = int(diff_hex, 16) / 100.0
            
        # Weight 복원
        weight = int(weight_hex, 16) / 100.0
        
        pv_results.append({"diff": diff, "weight": weight})
        
    return pv_results
```

## **BBox 디코딩**

---

### **[bbox] 인코딩 규격**

| 항목 | 상세 내용 | 비고 |
| --- | --- | --- |
| **데이터 포맷** | 16자리 Hex String | x, y, w, h 각 4자리 할당 |
| **데이터 구조** | `[x(4)]` + `[y(4)]` + `[w(4)]` + `[h(4)]` | 각 좌표/크기에 10,000 곱연산 적용 |

### **[bbox] 디코딩 예제 코드 (Python)**

```python
bbox = [int(bbox_hex[i:i+4], 16) for i in range(0, len(bbox_hex), 4)]
```