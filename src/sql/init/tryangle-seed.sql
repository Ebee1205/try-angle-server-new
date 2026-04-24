-- TryAngle seed scaffold

START TRANSACTION;

-- TODO: seed required base data
-- Example:
-- INSERT INTO tb_img_ctg (id, name, cDate, uDate)
-- VALUES ('ctg-default', 'default', 0, 0);

START TRANSACTION;

-- 1. 사용자 시드 데이터 (기존 유지)
INSERT INTO tb_user (id, email, password, name, nickname, phone, emailConf, `desc`, role, cDate, uDate) VALUES
('usr_001', '2025tryangle@gmail.com', 'smwhg2025!', '트라이앵글', '슈퍼어드민', '010-0000-0000', '1', '시스템 최고 관리자입니다.', 'SUPER_ADMIN', 1712966400, 1712966400),
('usr_002', 'admin@email.com', 'admin', '트라이앵글어드민', '관리자', '010-1111-1111', '1', '서비스 운영 관리자입니다.', 'ADMIN', 1712966400, 1712966400),
('usr_003', 'guest@email.com', 'guest', '김예공', '게스트', '010-2222-2222', '1', '일반 사용자입니다.', 'CLIENT', 1712966400, 1712966400);

-- 2. 태그 시드 데이터

-- [SHOT: 샷타입]
INSERT INTO tb_tag (id, userId, parentCode, code, tagName, cDate, uDate) VALUES
('tag_100', 'usr_001', NULL, 'SHOT_ROOT', '샷타입', 1712966400, 1712966400),
('tag_101', 'usr_001', 'SHOT_ROOT', 'SHOT_FULL', '전신', 1712966400, 1712966400),
('tag_102', 'usr_001', 'SHOT_ROOT', 'SHOT_UPPER', '상체 중심', 1712966400, 1712966400),
('tag_103', 'usr_001', 'SHOT_ROOT', 'SHOT_LOWER', '하체 중심', 1712966400, 1712966400),
('tag_104', 'usr_001', 'SHOT_ROOT', 'SHOT_SELFIE', '셀카', 1712966400, 1712966400),
('tag_105', 'usr_001', 'SHOT_ROOT', 'SHOT_SELFMODE', '내찍사', 1712966400, 1712966400),
('tag_106', 'usr_001', 'SHOT_ROOT', 'SHOT_TAKEFORME', '남찍사', 1712966400, 1712966400);

-- [MOOD: 분위기]
INSERT INTO tb_tag (id, userId, parentCode, code, tagName, cDate, uDate) VALUES
('tag_200', 'usr_001', NULL, 'MOOD_ROOT', '분위기', 1712966400, 1712966400),
('tag_201', 'usr_001', 'MOOD_ROOT', 'MOOD_CUTE', '러블리', 1712966400, 1712966400),
('tag_202', 'usr_001', 'MOOD_ROOT', 'MOOD_Y2K', 'Y2K', 1712966400, 1712966400),
('tag_203', 'usr_001', 'MOOD_ROOT', 'MOOD_STREET', '스트릿', 1712966400, 1712966400),
('tag_204', 'usr_001', 'MOOD_ROOT', 'MOOD_CHIC', '시크', 1712966400, 1712966400),
('tag_205', 'usr_001', 'MOOD_ROOT', 'MOOD_REFRESH', '청량', 1712966400, 1712966400),
('tag_206', 'usr_001', 'MOOD_ROOT', 'MOOD_VINTAGE', '빈티지', 1712966400, 1712966400);

-- [CLOTH: 옷 - 대분류]
INSERT INTO tb_tag (id, userId, parentCode, code, tagName, cDate, uDate) VALUES
('tag_300', 'usr_001', NULL, 'CLOTH_ROOT', '옷', 1712966400, 1712966400),
('tag_301', 'usr_001', 'CLOTH_ROOT', 'CLOTH_TOP', '상의', 1712966400, 1712966400),
('tag_302', 'usr_001', 'CLOTH_ROOT', 'CLOTH_BOTTOM', '하의', 1712966400, 1712966400),
('tag_303', 'usr_001', 'CLOTH_ROOT', 'CLOTH_SHOES', '신발', 1712966400, 1712966400),
('tag_304', 'usr_001', 'CLOTH_ROOT', 'CLOTH_BAG', '가방', 1712966400, 1712966400),
('tag_305', 'usr_001', 'CLOTH_ROOT', 'CLOTH_DRESS', '원피스', 1712966400, 1712966400),
('tag_306', 'usr_001', 'CLOTH_ROOT', 'CLOTH_ACC', '잡화', 1712966400, 1712966400),
('tag_307', 'usr_001', 'CLOTH_ROOT', 'CLOTH_OUTER', '아우터', 1712966400, 1712966400),
('tag_308', 'usr_001', 'CLOTH_ROOT', 'CLOTH_SKIRT', '치마', 1712966400, 1712966400);

-- [CLOTH_TOP: 상의 하위]
INSERT INTO tb_tag (id, userId, parentCode, code, tagName, cDate, uDate) VALUES
('tag_401', 'usr_001', 'CLOTH_TOP', 'TOP_LONGSLEEVE', '긴팔', 1712966400, 1712966400),
('tag_402', 'usr_001', 'CLOTH_TOP', 'TOP_TSHIRT', '반팔', 1712966400, 1712966400),
('tag_403', 'usr_001', 'CLOTH_TOP', 'TOP_SWEATSHIRT', '맨투맨', 1712966400, 1712966400),
('tag_404', 'usr_001', 'CLOTH_TOP', 'TOP_SHIRT', '셔츠', 1712966400, 1712966400),
('tag_405', 'usr_001', 'CLOTH_TOP', 'TOP_HOODIE', '후드티', 1712966400, 1712966400),
('tag_406', 'usr_001', 'CLOTH_TOP', 'TOP_SWEATER', '스웨터', 1712966400, 1712966400),
('tag_407', 'usr_001', 'CLOTH_TOP', 'TOP_TANKTOP', '민소매', 1712966400, 1712966400);

-- [CLOTH_SHOES: 신발 하위]
INSERT INTO tb_tag (id, userId, parentCode, code, tagName, cDate, uDate) VALUES
('tag_501', 'usr_001', 'CLOTH_SHOES', 'SHOES_SNEAKERS', '스니커즈', 1712966400, 1712966400),
('tag_502', 'usr_001', 'CLOTH_SHOES', 'SHOES_SPROTS', '스포츠화', 1712966400, 1712966400),
('tag_503', 'usr_001', 'CLOTH_SHOES', 'SHOES_DRESS', '구두', 1712966400, 1712966400),
('tag_504', 'usr_001', 'CLOTH_SHOES', 'SHOES_BOOTS', '부츠', 1712966400, 1712966400),
('tag_505', 'usr_001', 'CLOTH_SHOES', 'SHOES_SANDALS', '샌들', 1712966400, 1712966400),
('tag_506', 'usr_001', 'CLOTH_SHOES', 'SHOES_SLPPERS', '슬리퍼', 1712966400, 1712966400),
('tag_507', 'usr_001', 'CLOTH_SHOES', 'SHOES_PUR', '퍼 신발', 1712966400, 1712966400);

-- [CLOTH_OUTER: 아우터 하위]
INSERT INTO tb_tag (id, userId, parentCode, code, tagName, cDate, uDate) VALUES
('tag_601', 'usr_001', 'CLOTH_OUTER', 'OUTER_HOODIE', '후드집업', 1712966400, 1712966400),
('tag_602', 'usr_001', 'CLOTH_OUTER', 'OUTER_BLOUSON', '블루종', 1712966400, 1712966400),
('tag_603', 'usr_001', 'CLOTH_OUTER', 'OUTER_LEATHER', '레더 자켓', 1712966400, 1712966400),
('tag_604', 'usr_001', 'CLOTH_OUTER', 'OUTER_SUIT', '슈트', 1712966400, 1712966400),
('tag_605', 'usr_001', 'CLOTH_OUTER', 'OUTER_CARDIGAN', '가디건', 1712966400, 1712966400),
('tag_606', 'usr_001', 'CLOTH_OUTER', 'OUTER_LIGHTDOWN', '경량패딩', 1712966400, 1712966400),
('tag_607', 'usr_001', 'CLOTH_OUTER', 'OUTER_HUNTING', '헌팅 자켓', 1712966400, 1712966400),
('tag_608', 'usr_001', 'CLOTH_OUTER', 'OUTER_TRUCKER', '트러커 자켓', 1712966400, 1712966400),
('tag_609', 'usr_001', 'CLOTH_OUTER', 'OUTER_TRACK', '트레이닝 자켓', 1712966400, 1712966400),
('tag_610', 'usr_001', 'CLOTH_OUTER', 'OUTER_FLEECE', '플리스', 1712966400, 1712966400),
('tag_611', 'usr_001', 'CLOTH_OUTER', 'OUTER_SHEARLING', '무스탕', 1712966400, 1712966400),
('tag_612', 'usr_001', 'CLOTH_OUTER', 'OUTER_COAT', '코트', 1712966400, 1712966400),
('tag_613', 'usr_001', 'CLOTH_OUTER', 'OUTER_DOUBLECOAT', '더블코트', 1712966400, 1712966400),
('tag_614', 'usr_001', 'CLOTH_OUTER', 'OUTER_LONGPADDING', '롱패딩', 1712966400, 1712966400),
('tag_615', 'usr_001', 'CLOTH_OUTER', 'OUTER_SHORTPADDING', '숏패딩', 1712966400, 1712966400),
('tag_616', 'usr_001', 'CLOTH_OUTER', 'OUTER_STADIUM', '스타디움 자켓', 1712966400, 1712966400);

-- [CLOTH_BOTTOM: 하의 하위]
INSERT INTO tb_tag (id, userId, parentCode, code, tagName, cDate, uDate) VALUES
('tag_701', 'usr_001', 'CLOTH_BOTTOM', 'BOTTOM_DENIM', '데님', 1712966400, 1712966400),
('tag_702', 'usr_001', 'CLOTH_BOTTOM', 'BOTTOM_TRACK', '트레이닝', 1712966400, 1712966400),
('tag_703', 'usr_001', 'CLOTH_BOTTOM', 'BOTTOM_CHINOS', '코튼', 1712966400, 1712966400),
('tag_704', 'usr_001', 'CLOTH_BOTTOM', 'BOTTOM_SLACKS', '슬랙스', 1712966400, 1712966400),
('tag_705', 'usr_001', 'CLOTH_BOTTOM', 'BOTTOM_SHORTS', '반바지', 1712966400, 1712966400),
('tag_706', 'usr_001', 'CLOTH_BOTTOM', 'BOTTOM_LEGGINGS', '레깅스', 1712966400, 1712966400),
('tag_707', 'usr_001', 'CLOTH_BOTTOM', 'BOTTOM_JUMPSUIT', '점프슈트', 1712966400, 1712966400);

-- [CLOTH_DRESS / SKIRT: 원피스 및 치마 하위]
INSERT INTO tb_tag (id, userId, parentCode, code, tagName, cDate, uDate) VALUES
('tag_801', 'usr_001', 'CLOTH_DRESS', 'DRESS_MINI', '미니 원피스', 1712966400, 1712966400),
('tag_802', 'usr_001', 'CLOTH_DRESS', 'DRESS_MIDI', '미디 원피스', 1712966400, 1712966400),
('tag_803', 'usr_001', 'CLOTH_DRESS', 'DRESS_MAXI', '맥시 원피스', 1712966400, 1712966400),
('tag_804', 'usr_001', 'CLOTH_SKIRT', 'SKIRT_MINI', '미니 스커트', 1712966400, 1712966400),
('tag_805', 'usr_001', 'CLOTH_SKIRT', 'SKIRT_MIDI', '미디 스커트', 1712966400, 1712966400),
('tag_806', 'usr_001', 'CLOTH_SKIRT', 'SKIRT_MAXI', '롱스커트', 1712966400, 1712966400);

-- [CLOTH_BAG / ACC: 가방 및 잡화 하위]
INSERT INTO tb_tag (id, userId, parentCode, code, tagName, cDate, uDate) VALUES
('tag_901', 'usr_001', 'CLOTH_BAG', 'BAG_CROSS', '크로스백', 1712966400, 1712966400),
('tag_902', 'usr_001', 'CLOTH_BAG', 'BAG_SHOULDER', '숄더백', 1712966400, 1712966400),
('tag_903', 'usr_001', 'CLOTH_BAG', 'BAG_BACKPACK', '백팩', 1712966400, 1712966400),
('tag_904', 'usr_001', 'CLOTH_BAG', 'BAG_TOTE', '토트백', 1712966400, 1712966400),
('tag_905', 'usr_001', 'CLOTH_BAG', 'BAG_ECO', '에코백', 1712966400, 1712966400),
('tag_906', 'usr_001', 'CLOTH_BAG', 'BAG_BOSTON', '보스턴백', 1712966400, 1712966400),
('tag_907', 'usr_001', 'CLOTH_ACC', 'ACC_GLASSES', '안경', 1712966400, 1712966400),
('tag_908', 'usr_001', 'CLOTH_ACC', 'ACC_HAT', '모자', 1712966400, 1712966400),
('tag_909', 'usr_001', 'CLOTH_ACC', 'ACC_SCARP', '머플러', 1712966400, 1712966400),
('tag_910', 'usr_001', 'CLOTH_ACC', 'ACC_BELT', '벨트', 1712966400, 1712966400),
('tag_911', 'usr_001', 'CLOTH_ACC', 'ACC_WATCH', '시계', 1712966400, 1712966400);

COMMIT;