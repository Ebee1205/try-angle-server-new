-- TryAngle seed scaffold

START TRANSACTION;

-- TODO: seed required base data
-- Example:
-- INSERT INTO tb_img_ctg (id, name, cDate, uDate)
-- VALUES ('ctg-default', 'default', 0, 0);

-- 1. 사용자 시드 데이터
INSERT INTO tb_user (id, email, password, name, nickname, phone, emailConf, `desc`, role, cDate, uDate) VALUES
('usr_001', '2025tryangle@gmail.com', 'smwhg2025!', '트라이앵글', '슈퍼어드민', '010-0000-0000', '1', '시스템 최고 관리자입니다.', 'SUPER_ADMIN', 1712966400, 1712966400),
('usr_002', 'admin@email.com', 'admin', '트라이앵글어드민', '관리자', '010-1111-1111', '1', '서비스 운영 관리자입니다.', 'ADMIN', 1712966400, 1712966400),
('usr_003', 'guest@email.com', 'guest', '김예공', '게스트', '010-2222-2222', '1', '일반 사용자입니다.', 'CLIENT', 1712966400, 1712966400);


-- 2. 태그 시드 데이터 (카테고리 및 하위 태그)
-- [사용자 관련]
INSERT INTO tb_tag (id, userId, parentCode, code, tagName, cDate, uDate) VALUES
('tag_001', 'usr_001', NULL, 'USER_ROOT', '사용자 관련', 1712966400, 1712966400),
('tag_002', 'usr_001', 'USER_ROOT', 'ROLE_SUPER', '슈퍼어드민', 1712966400, 1712966400),
('tag_003', 'usr_001', 'USER_ROOT', 'ROLE_ADMIN', '어드민', 1712966400, 1712966400),
('tag_004', 'usr_001', 'USER_ROOT', 'ROLE_USER', '유저', 1712966400, 1712966400),
('tag_005', 'usr_001', 'USER_ROOT', 'ROLE_INFL', '인플루언서', 1712966400, 1712966400);

-- [분위기]
INSERT INTO tb_tag (id, userId, parentCode, code, tagName, cDate, uDate) VALUES
('tag_006', 'usr_001', NULL, 'MOOD_ROOT', '분위기', 1712966400, 1712966400),
('tag_007', 'usr_001', 'MOOD_ROOT', 'MOOD_CUTE', '귀여운', 1712966400, 1712966400),
('tag_008', 'usr_001', 'MOOD_ROOT', 'MOOD_HIP', '힙한', 1712966400, 1712966400),
('tag_009', 'usr_001', 'MOOD_ROOT', 'MOOD_EMO', '감성', 1712966400, 1712966400);

-- [샷타입]
INSERT INTO tb_tag (id, userId, parentCode, code, tagName, cDate, uDate) VALUES
('tag_010', 'usr_001', NULL, 'SHOT_ROOT', '샷타입', 1712966400, 1712966400),
('tag_011', 'usr_001', 'SHOT_ROOT', 'SHOT_HIGH', '하이앵글', 1712966400, 1712966400),
('tag_012', 'usr_001', 'SHOT_ROOT', 'SHOT_LOW', '로우앵글', 1712966400, 1712966400),
('tag_013', 'usr_001', 'SHOT_ROOT', 'SHOT_FULL', '전신샷', 1712966400, 1712966400),
('tag_014', 'usr_001', 'SHOT_ROOT', 'SHOT_BUST', '바스트샷', 1712966400, 1712966400),
('tag_015', 'usr_001', 'SHOT_ROOT', 'SHOT_MIRROR', '거울샷', 1712966400, 1712966400);

-- [옷]
INSERT INTO tb_tag (id, userId, parentCode, code, tagName, cDate, uDate) VALUES
('tag_016', 'usr_001', NULL, 'CLOTH_ROOT', '옷', 1712966400, 1712966400),
('tag_017', 'usr_001', 'CLOTH_ROOT', 'CLOTH_TOP', '상의', 1712966400, 1712966400),
('tag_018', 'usr_001', 'CLOTH_ROOT', 'CLOTH_BTM', '하의', 1712966400, 1712966400);

COMMIT;
