-- TryAngle initial schema
-- Target: MySQL 8.0+ (utf8mb4)

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

START TRANSACTION;

CREATE TABLE IF NOT EXISTS tb_user (
	id VARCHAR(64) NOT NULL,
	email VARCHAR(255) NOT NULL,
	password VARCHAR(255) NOT NULL,
	name VARCHAR(100) NULL,
	nickname VARCHAR(100) NULL,
	phone VARCHAR(30) NULL,
	emailConf VARCHAR(1) NOT NULL DEFAULT '2',
	`desc` TEXT NULL,
	fileId VARCHAR(128) NULL,
	role ENUM('SUPER_ADMIN', 'ADMIN', 'CLIENT') NOT NULL DEFAULT 'CLIENT',
	extra JSON NULL,
	cDate BIGINT NOT NULL,
	uDate BIGINT NOT NULL,
	PRIMARY KEY (id),
	UNIQUE KEY uk_tb_user_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS tb_img_ctg (
	id VARCHAR(64) NOT NULL,
	name VARCHAR(100) NOT NULL,
	cDate BIGINT NOT NULL,
	uDate BIGINT NOT NULL,
	PRIMARY KEY (id),
	UNIQUE KEY uk_tb_img_ctg_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS tb_tag (
	id VARCHAR(64) NOT NULL,
	userId VARCHAR(64) NOT NULL,
	parentCode VARCHAR(64) NULL,
	code VARCHAR(64) NOT NULL,
	tagName VARCHAR(100) NOT NULL,
	cDate BIGINT NOT NULL,
	uDate BIGINT NOT NULL,
	PRIMARY KEY (id),
	UNIQUE KEY uk_tb_tag_code (code),
	KEY idx_tb_tag_userId (userId),
	KEY idx_tb_tag_parentCode (parentCode),
	CONSTRAINT fk_tb_tag_userId FOREIGN KEY (userId) REFERENCES tb_user (id)
		ON DELETE RESTRICT ON UPDATE CASCADE,
	CONSTRAINT fk_tb_tag_parentCode FOREIGN KEY (parentCode) REFERENCES tb_tag (code)
		ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS tb_img (
	id VARCHAR(64) NOT NULL,
	userId VARCHAR(64) NOT NULL,
	ctgId VARCHAR(64) NOT NULL,
	imgUrl VARCHAR(2048) NOT NULL,
	title VARCHAR(200) NULL,
	`desc` TEXT NULL,
	useCnt INT NOT NULL DEFAULT 0,
	kwd JSON NULL,
	aiDocId VARCHAR(128) NULL,
	expWeight FLOAT NOT NULL DEFAULT 0,
	pri INT NOT NULL DEFAULT 0,
	cDate BIGINT NOT NULL,
	uDate BIGINT NOT NULL,
	PRIMARY KEY (id),
	KEY idx_tb_img_userId (userId),
	KEY idx_tb_img_ctgId (ctgId),
	KEY idx_tb_img_rank (useCnt, expWeight, pri),
	CONSTRAINT fk_tb_img_userId FOREIGN KEY (userId) REFERENCES tb_user (id)
		ON DELETE RESTRICT ON UPDATE CASCADE,
	CONSTRAINT fk_tb_img_ctgId FOREIGN KEY (ctgId) REFERENCES tb_img_ctg (id)
		ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS mtb_bookmark (
	id VARCHAR(64) NOT NULL,
	userId VARCHAR(64) NOT NULL,
	imgId VARCHAR(64) NOT NULL,
	cDate BIGINT NOT NULL,
	PRIMARY KEY (id),
	UNIQUE KEY uk_mtb_bookmark_user_img (userId, imgId),
	KEY idx_mtb_bookmark_userId (userId),
	KEY idx_mtb_bookmark_imgId (imgId),
	CONSTRAINT fk_mtb_bookmark_userId FOREIGN KEY (userId) REFERENCES tb_user (id)
		ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_mtb_bookmark_imgId FOREIGN KEY (imgId) REFERENCES tb_img (id)
		ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS mtb_img_tag (
	id VARCHAR(64) NOT NULL,
	imgId VARCHAR(64) NOT NULL,
	tagId VARCHAR(64) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE KEY uk_mtb_img_tag_img_tag (imgId, tagId),
	KEY idx_mtb_img_tag_imgId (imgId),
	KEY idx_mtb_img_tag_tagId (tagId),
	CONSTRAINT fk_mtb_img_tag_imgId FOREIGN KEY (imgId) REFERENCES tb_img (id)
		ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_mtb_img_tag_tagId FOREIGN KEY (tagId) REFERENCES tb_tag (id)
		ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
