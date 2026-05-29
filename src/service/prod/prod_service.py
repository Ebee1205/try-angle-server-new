import time

from fastapi import HTTPException

from src.app_context import AppContext
from src.utils.db_utils import execute_query
from src.service.prod.prod_schema import (
	ProdCreateRequest,
	ProdItem,
	ProdListResponse,
	ProdUpdateRequest,
)

_VALID_P_STAT = (0, 1, 2)


def _row_to_prod_item(row: tuple) -> ProdItem:
	return ProdItem(
		id=row[0],
		userName=row[1],
		name=row[2],
		brand=row[3],
		price=row[4],
		thumbUrl=row[5],
		pStat=row[6],
		cDate=row[7],
		uDate=row[8],
	)


def list_prods(
	ctx: AppContext,
	page: int = 1,
	limit: int = 20,
	name: str | None = None,
	p_stat: int | None = None,
) -> ProdListResponse:
	"""상품 목록 조회"""
	if ctx.log:
		ctx.log.debug(
			f"Prod list requested | page={page} limit={limit} name={name} p_stat={p_stat}"
		)

	if not ctx.db_handler:
		raise HTTPException(status_code=500, detail="Database not initialized")

	offset = (page - 1) * limit
	if p_stat is not None and p_stat not in _VALID_P_STAT:
		raise HTTPException(status_code=400, detail="Invalid pStat value")

	where_conditions: list[str] = []
	where_params: list = []
	if name is not None and name.strip() != "":
		where_conditions.append("i.name LIKE %s")
		where_params.append(f"%{name.strip()}%")
	if p_stat is not None:
		where_conditions.append("i.pStat = %s")
		where_params.append(p_stat)

	where_clause = f"WHERE {' AND '.join(where_conditions)}" if where_conditions else ""
	where_params_tuple = tuple(where_params)

	count_sql = f"SELECT COUNT(*) FROM tb_prod i {where_clause}"
	count_params = where_params_tuple
	list_sql = f"""
		SELECT
			i.id,
			COALESCE(NULLIF(u.nickname, ''), NULLIF(u.name, ''), u.email) AS creatorName,
			i.name,
			i.brand,
			i.price,
			i.thumbUrl,
			i.pStat,
			i.cDate,
			i.uDate
		FROM tb_prod i
		INNER JOIN tb_user u ON u.id = i.userId
		{where_clause}
		ORDER BY i.cDate DESC
		LIMIT %s OFFSET %s
	"""
	list_params = where_params_tuple + (limit, offset)

	count_rows = execute_query(ctx.db_handler, count_sql, count_params)
	total = count_rows[0][0] if count_rows else 0

	rows = execute_query(ctx.db_handler, list_sql, list_params)
	items = [_row_to_prod_item(row) for row in rows]

	return ProdListResponse(items=items, total=total, page=page, limit=limit)


def get_prod(ctx: AppContext, prod_id: int) -> ProdItem:
	"""상품 상세 조회"""
	if ctx.log:
		ctx.log.debug(f"Prod get requested | id={prod_id}")

	if not ctx.db_handler:
		raise HTTPException(status_code=500, detail="Database not initialized")

	sql = """
		SELECT
			i.id,
			COALESCE(NULLIF(u.nickname, ''), NULLIF(u.name, ''), u.email) AS creatorName,
			i.name,
			i.brand,
			i.price,
			i.thumbUrl,
			i.pStat,
			i.cDate,
			i.uDate
		FROM tb_prod i
		INNER JOIN tb_user u ON u.id = i.userId
		WHERE i.id = %s
	"""
	rows = execute_query(ctx.db_handler, sql, (prod_id,))
	if not rows:
		raise HTTPException(status_code=404, detail="Product not found")

	return _row_to_prod_item(rows[0])


def create_prod(ctx: AppContext, payload: ProdCreateRequest, user_id: int) -> ProdItem:
	"""상품 등록"""
	if ctx.log:
		ctx.log.debug(f"Prod create requested | name={payload.name} userId={user_id}")

	if not ctx.db_handler:
		raise HTTPException(status_code=500, detail="Database not initialized")

	if payload.pStat not in _VALID_P_STAT:
		raise HTTPException(status_code=400, detail="Invalid pStat value")

	now = int(time.time())

	sql = """
		INSERT INTO tb_prod (userId, name, brand, price, thumbUrl, pStat, cDate, uDate)
		VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
	"""
	params = (
		user_id,
		payload.name,
		payload.brand,
		payload.price,
		payload.thumbUrl,
		payload.pStat,
		now,
		now,
	)

	conn = ctx.db_handler.get_connection()
	new_id: int | None = None
	try:
		with conn.cursor() as cursor:
			cursor.execute(sql, params)
			new_id = cursor.lastrowid
		conn.commit()
	except Exception as e:
		conn.rollback()
		if ctx.log:
			ctx.log.error(f"Failed to create prod: {e}")
		raise HTTPException(status_code=500, detail="Failed to create product")

	created_rows = execute_query(
		ctx.db_handler,
		"""
			SELECT
				i.id,
				COALESCE(NULLIF(u.nickname, ''), NULLIF(u.name, ''), u.email) AS creatorName,
				i.name,
				i.brand,
				i.price,
				i.thumbUrl,
				i.pStat,
				i.cDate,
				i.uDate
			FROM tb_prod i
			INNER JOIN tb_user u ON u.id = i.userId
			WHERE i.id = %s
		""",
		(new_id,),
	)
	return _row_to_prod_item(created_rows[0])


def update_prod(ctx: AppContext, payload: ProdUpdateRequest) -> ProdItem:
	"""상품 수정"""
	if ctx.log:
		ctx.log.debug(f"Prod update requested | id={payload.id}")

	if not ctx.db_handler:
		raise HTTPException(status_code=500, detail="Database not initialized")

	rows = execute_query(
		ctx.db_handler,
		"SELECT id, userId, name, brand, price, thumbUrl, pStat, cDate, uDate FROM tb_prod WHERE id = %s",
		(payload.id,),
	)
	if not rows:
		raise HTTPException(status_code=404, detail="Product not found")

	if payload.pStat is not None and payload.pStat not in _VALID_P_STAT:
		raise HTTPException(status_code=400, detail="Invalid pStat value")

	fields = []
	params = []
	if payload.name is not None:
		fields.append("name = %s")
		params.append(payload.name)
	if payload.brand is not None:
		fields.append("brand = %s")
		params.append(payload.brand)
	if payload.price is not None:
		fields.append("price = %s")
		params.append(payload.price)
	if payload.thumbUrl is not None:
		fields.append("thumbUrl = %s")
		params.append(payload.thumbUrl)
	if payload.pStat is not None:
		fields.append("pStat = %s")
		params.append(payload.pStat)

	if not fields:
		raise HTTPException(status_code=400, detail="No fields to update")

	now = int(time.time())
	fields.append("uDate = %s")
	params.append(now)
	params.append(payload.id)

	sql = f"UPDATE tb_prod SET {', '.join(fields)} WHERE id = %s"
	conn = ctx.db_handler.get_connection()
	try:
		with conn.cursor() as cursor:
			cursor.execute(sql, params)
		conn.commit()
	except Exception as e:
		conn.rollback()
		if ctx.log:
			ctx.log.error(f"Failed to update prod: {e}")
		raise HTTPException(status_code=500, detail="Failed to update product")

	updated_rows = execute_query(
		ctx.db_handler,
		"""
			SELECT
				i.id,
				COALESCE(NULLIF(u.nickname, ''), NULLIF(u.name, ''), u.email) AS creatorName,
				i.name,
				i.brand,
				i.price,
				i.thumbUrl,
				i.pStat,
				i.cDate,
				i.uDate
			FROM tb_prod i
			INNER JOIN tb_user u ON u.id = i.userId
			WHERE i.id = %s
		""",
		(payload.id,),
	)
	return _row_to_prod_item(updated_rows[0])


def delete_prod(ctx: AppContext, prod_id: int) -> dict:
	"""상품 삭제"""
	if ctx.log:
		ctx.log.debug(f"Prod delete requested | id={prod_id}")

	if not ctx.db_handler:
		raise HTTPException(status_code=500, detail="Database not initialized")

	rows = execute_query(
		ctx.db_handler,
		"SELECT id FROM tb_prod WHERE id = %s",
		(prod_id,),
	)
	if not rows:
		raise HTTPException(status_code=404, detail="Product not found")

	conn = ctx.db_handler.get_connection()
	try:
		with conn.cursor() as cursor:
			cursor.execute("DELETE FROM tb_prod WHERE id = %s", (prod_id,))
		conn.commit()
	except Exception as e:
		conn.rollback()
		if ctx.log:
			ctx.log.error(f"Failed to delete prod: {e}")
		raise HTTPException(status_code=500, detail="Failed to delete product")

	return {"id": prod_id}
