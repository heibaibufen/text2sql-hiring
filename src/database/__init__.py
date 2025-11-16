from src.config import cfg
from typing import Optional, Any, List, Dict, Union
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine import Engine


class DatabaseManager:
    """数据库连接管理器"""

    def __init__(self):
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None

    def get_database_url(self) -> str:
        return cfg.postgres_uri

    def create_engine(self, echo: bool = False) -> Engine:
        if self._engine is None:
            database_url = self.get_database_url()
            self._engine = create_engine(
                database_url,
                echo=echo,
                pool_size=10,
                max_overflow=20,
                pool_timeout=30,
                pool_recycle=3600
            )
        return self._engine

    def get_session_factory(self) -> sessionmaker:
        if self._session_factory is None:
            engine = self.create_engine()
            self._session_factory = sessionmaker(bind=engine)
        return self._session_factory

    def get_session(self) -> Session:
        session_factory = self.get_session_factory()
        return session_factory()

    def get_tables_schemas(self) -> List[Dict[str, Any]]:
        sql = """
        SELECT
            c.relname AS table_name,
            obj_description(c.oid) AS table_comment,
            a.attname AS column_name,
            pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
            pg_get_expr(ad.adbin, ad.adrelid) AS column_default,
            col_description(a.attrelid, a.attnum) AS column_comment
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        JOIN pg_attribute a ON a.attrelid = c.oid
        LEFT JOIN pg_attrdef ad ON a.attrelid = ad.adrelid AND a.attnum = ad.adnum
        WHERE c.relkind = 'r'
          AND n.nspname = 'public'
          AND a.attnum > 0
          AND NOT a.attisdropped
        ORDER BY c.relname, a.attnum;
        """

        rows = self.execute_sql(sql)
        tables: Dict[str, Dict[str, Any]] = {}

        for row in rows:
            table_name = row["table_name"]
            if table_name not in tables:
                tables[table_name] = {
                    "table_name": table_name,
                    "table_desc": row["table_comment"],
                    "columns": []
                }
            tables[table_name]["columns"].append({
                "column_name": row["column_name"],
                "data_type": row["data_type"],
                "column_default": row["column_default"],
                "column_comment": row["column_comment"],
            })

        return list(tables.values())

    def execute_sql(
            self,
            sql: str,
            params: Optional[Union[Dict[str, Any], List[Any]]] = None,
            fetch: bool = True,
            commit: bool = False,
    ) -> Optional[List[Dict[str, Any]]]:
        """
        执行任意 SQL 语句

        :param sql: SQL 语句（可带参数）
        :param params: 可选参数 dict 或 list
        :param fetch: 是否返回结果（默认 True）
        :param commit: 是否提交事务（用于 INSERT/UPDATE/DELETE）
        :return: 若 fetch=True，返回结果列表（每行是 dict）
        """
        engine = self.create_engine()
        with engine.connect() as conn:
            try:
                result = conn.execute(text(sql), params or {})
                if commit:
                    conn.commit()
                if fetch:
                    # 返回结果为 list[dict]
                    rows = result.mappings().all()
                    return [dict(row) for row in rows]
            except Exception as e:
                print(f"执行 SQL 失败: {e}\nSQL: {sql}")
                raise

    def test_connection(self) -> bool:
        try:
            engine = self.create_engine()
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                return result.fetchone()[0] == 1
        except Exception as e:
            print(f"数据库连接测试失败: {e}")
            return False

    def close(self):
        """关闭数据库连接"""
        if self._engine:
            self._engine.dispose()
            self._engine = None
            self._session_factory = None


db_manager = DatabaseManager()
