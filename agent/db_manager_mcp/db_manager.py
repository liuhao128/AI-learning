from sqlalchemy import create_engine, inspect, text
from typing import List, Dict, Any


class DBManager:
    """
    数据库管理类，负责创建和管理 SQLAlchemy 连接：
    如果想要连接数据库，那么就必须使用 sqlalchemy（数据库操作），根据 mysql+pymysql://root:123456@localhost:3306/test_db?charset=utf8mb4 的格式连接数据库。
    """

    def __init__(
            self,
            username: str,
            password: str,
            host: str = "localhost",
            port: int = 3306,
            database: str = "",
            driver: str = "mysql+pymysql",
            charset: str = "utf8mb4",
            **kwargs
    ):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.driver = driver
        self.charset = charset
        self.extra_params = kwargs

        self._engine = None

    def _build_connection_string(self) -> str:
        """构建数据库连接字符串"""
        conn_str = f"{self.driver}://{self.username}:{self.password}@{self.host}:{self.port}"
        if self.database:
            conn_str += f"/{self.database}?charset={self.charset}"
        else:
            conn_str += f"?charset={self.charset}"
        for key, value in self.extra_params.items():
            conn_str += f"&{key}={value}"
        return conn_str

    def _get_engine(self):
        """获取 Engine 对象（内部使用）"""
        if self._engine is None:
            self._engine = create_engine(
                self._build_connection_string(),
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=False
            )
        return self._engine

    def get_table_names(self) -> List[str]:
        """
        获取数据库中所有表名
        Returns:
            表名列表
        """
        engine = self._get_engine()
        inspector = inspect(engine)
        return inspector.get_table_names()

    def get_table_names_with_comments(self) -> Dict[str, str]:
        """
        获取 MySQL 数据库中所有表名及其对应的注释（comment）

        Returns:
            字典，键为表名，值为表注释
        """
        engine = self._get_engine()

        sql = text("""
            SELECT table_name, table_comment 
            FROM information_schema.tables 
            WHERE table_schema = :database
        """)

        with engine.connect() as conn:
            result = conn.execute(sql, {"database": self.database})
            return {row[0]: row[1] or "" for row in result.fetchall()}

    def get_all_table_schemas(self) -> Dict[str, Dict]:
        """
        获取数据库中所有表的完整结构信息（不含外键）

        Returns:
            字典，键为表名，值为表结构信息
            包含：注释、字段列表、主键、索引
        """
        engine = self._get_engine()
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        comments = self.get_table_names_with_comments()

        result = {}

        for table_name in tables:
            # 获取字段信息
            columns = []
            cols = inspector.get_columns(table_name)
            for col in cols:
                columns.append({
                    # 列名 类型 是否非空 默认值 comment 是否自增
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col["nullable"],
                    "default": str(col.get("default")) if col.get("default") is not None else None,
                    "comment": col.get("comment", ""),
                    "auto_increment": col.get("autoincrement", False)
                })

            # 获取主键
            primary_keys = inspector.get_pk_constraint(table_name)
            pk_columns = primary_keys.get("constrained_columns", []) if primary_keys else []

            # 获取索引（不含主键索引）
            indexes = []
            for idx in inspector.get_indexes(table_name):
                # 跳过主键索引（主键已单独展示）
                if not idx.get("primary_key", False):
                    indexes.append({
                        "name": idx.get("name", ""),
                        "columns": idx.get("column_names", []),
                        "unique": idx.get("unique", False)
                    })

            result[table_name] = {
                "table_name": table_name,
                "comment": comments.get(table_name, ""),
                "columns": columns,
                "primary_keys": pk_columns,
                "indexes": indexes
            }

        return result

    def execute_query(self, sql: str) -> List[Dict[str, Any]]:
        """
        执行查询语句（SELECT），返回查询结果

        Args:
            sql: SELECT 查询语句

        Returns:
            查询结果列表，每行以字典形式返回
        """
        engine = self._get_engine()

        try:
            with engine.connect() as conn:
                raw_result = conn.execute(text(sql))
                rows = raw_result.fetchall()

                # 获取列名
                columns = []
                if hasattr(raw_result, 'keys'):
                    columns = list(raw_result.keys())
                elif raw_result.cursor and hasattr(raw_result.cursor, 'description'):
                    columns = [desc[0] for desc in raw_result.cursor.description]

                # 转换为字典列表
                data = []
                for row in rows:
                    if columns:
                        row_dict = {}
                        for i, col in enumerate(columns):
                            row_dict[col] = row[i]
                        data.append(row_dict)
                    else:
                        data.append(row)

                return data

        except Exception as e:
            raise Exception(f"查询失败: {str(e)}")

    def close(self) -> None:
        """关闭数据库连接池"""
        if self._engine:
            self._engine.dispose()
            self._engine = None