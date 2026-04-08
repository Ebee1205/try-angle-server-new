import json
from datetime import datetime

# Apple Epoch(2001.01.01)와 Unix Epoch(1970.01.01) 사이의 초 단위 차이
APPLE_TO_UNIX_OFFSET = 978307200.0

def to_hex_string(value, length=4):
    """정수를 고정된 길이의 Hex 문자열로 변환 (예: 854 -> '0356')"""
    # max값 제한 (length=4인 경우 65535, 넘어가면 FFFF로 고정)
    max_val = (16 ** length) - 1
    safe_val = max(0, min(max_val, int(value)))
    return f"{safe_val:0{length}x}"

def encode_bbox_hex(bbox):
    """BBox 리스트를 16자리 Hex String으로 변환"""
    if not bbox or len(bbox) != 4:
        return ""
    # 각 좌표를 4자리 Hex로 변환하여 이어붙임 (4 x 4 = 16 chars)
    return "".join([to_hex_string(x, 4) for x in bbox])

def encode_kp_hex(keypoints):
    """Keypoints 실수 리스트를 압축된 Hex String으로 변환"""
    if not keypoints:
        return ""
    
    hex_list = []
    for val in keypoints:
        # 1. 소수점 4자리 보존을 위해 10,000을 곱함 (Quantization)
        # 예: 0.3935 -> 3935
        scaled_val = val * 10000
        
        # 2. 4자리 Hex로 변환 (예: 3935 -> '0f5f')
        hex_str = to_hex_string(scaled_val, 4)
        hex_list.append(hex_str)
        
    # 3. 구분자 없이 모두 이어붙임
    return "".join(hex_list)

def transform_log_payload(log_line):
    try:
        data = json.loads(log_line.strip())
        
        # Timestamp 변환
        unix_ts_sec = data['ts'] + APPLE_TO_UNIX_OFFSET
        unix_ts_ms = int(unix_ts_sec * 1000)
        
        # Keypoints 1차원 평탄화
        flat_keypoints = [val for point in data['kp'] for val in point]
        
        # --- [압축 로직 적용] ---
        bbox_hex = encode_bbox_hex(data.get("bbox"))
        kp_hex = encode_kp_hex(flat_keypoints)
        
        payload = {
            "hd": {
                "event": "log.pose",
                "tid": int(datetime.now().timestamp() * 1000)
            },
            "bd": {
                "meta": {
                    "model": data.get("model", "DWPose-M"),
                    "fseq": data.get("f"),
                    "fts": unix_ts_ms,
                },
                "detc": [
                    {
                        "type": "person",
                        "bbox_hex": bbox_hex, # [압축됨] 16자리 문자열
                        "kp_hex": kp_hex      # [압축됨] 긴 16진수 문자열
                    }
                ]
            }
        }
        return payload

    except Exception as e:
        print(f"Error converting log: {e}")
        return None

# --- 파일 처리 실행 ---
input_filename = 'kp_260208_160123.json'
output_filename = 'transformed_hex_payloads.json'

processed_count = 0

with open(input_filename, 'r') as infile, open(output_filename, 'w') as outfile:
    for line in infile:
        if not line.strip(): continue
            
        transformed_data = transform_log_payload(line)
        
        if transformed_data:
            json_string = json.dumps(transformed_data)
            outfile.write(json_string + '\n')
            processed_count += 1

print(f"✅ Hex 압축 변환 완료! '{output_filename}' 저장됨. (처리 건수: {processed_count})")