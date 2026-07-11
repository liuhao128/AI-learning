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
        # 获取数据库引擎对象，代表与数据库的连接池
        engine = self._get_engine()
        # 从已连接的数据库中读取结构信息（表名、列名、主键、外键等），而不需要定义 ORM 模型类。
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
        print("获取表结构中...")
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
        print(f"Agent SQL: {sql}")
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


if __name__ == "__main__":
    db = DBManager(
        username="root",
        password="root",
        host="localhost",
        port=3306,
        database="test"
    )

    # print("1.数据库中的所有表：")
    # tables = db.get_table_names()
    # for i, table in enumerate(tables, 1):
    #     print(f"{i}. {table}")
    """
    1.数据库中的所有表：
    1. orders
    2. products
    """

    # print("2.数据库中的所有表&评论：")
    # tables_with_comment = db.get_table_names_with_comments()
    # for i, (table_name, table_comment) in enumerate(tables_with_comment.items(), 1):
    #     print(f"{i}. {table_name}. {table_comment}")
    """
    2.数据库中的所有表&评论：
    1. orders. 订单记录表
    2. products. 商品信息表
    """

    # print("3.获取所有表的完整结构信息：")
    # schemas = db.get_all_table_schemas()
    # print("=" * 70)
    # print("【所有表结构信息】")
    # print("=" * 70)
    # for table_name, info in schemas.items():
    #     print(f"\n📋 表名: {table_name}")
    #     print(f"📝 注释: {info['comment']}")
    #     print("\n  字段:")
    #     for col in info["columns"]:
    #         null_str = "可空" if col["nullable"] else "非空"
    #         auto_str = "自增" if col["auto_increment"] else ""
    #         print(f"    - {col['name']} ({col['type']}) {null_str} {auto_str} 注释: {col['comment']}")
    #     if info["primary_keys"]:
    #         print(f"\n  主键: {', '.join(info['primary_keys'])}")
    #     if info["indexes"]:
    #         print("\n  索引:")
    #         for idx in info["indexes"]:
    #             unique_str = "唯一" if idx["unique"] else "普通"
    #             print(f"    - {idx['name']} ({unique_str}): {', '.join(idx['columns'])}")
    #     print("-" * 50)
    """
    3.获取所有表的完整结构信息：
    获取表结构中...
    ======================================================================
    【所有表结构信息】
    ======================================================================

    📋 表名: orders
    📝 注释: 订单记录表

      字段:
        - id (INTEGER) 非空 自增 注释: 订单ID
        - product_id (INTEGER) 非空  注释: 商品ID
        - quantity (INTEGER) 非空  注释: 购买数量
        - order_date (DATE) 非空  注释: 订单日期

      主键: id

      索引:
        - product_id (普通): product_id
    --------------------------------------------------

    📋 表名: products
    📝 注释: 商品信息表

      字段:
        - id (INTEGER) 非空 自增 注释: 商品ID
        - name (VARCHAR(100)) 非空  注释: 商品名称
        - category (VARCHAR(50)) 非空  注释: 商品类别

      主键: id
    --------------------------------------------------

    """

    # print("4.直接传入 SQL 查询：")
    # result = db.execute_query("""
    #     SELECT p.name, SUM(o.quantity) AS total_sales
    #     FROM orders o
    #     JOIN products p ON o.product_id = p.id
    #     GROUP BY p.name
    #     ORDER BY total_sales DESC
    #     LIMIT 5;
    # """)
    #
    # for row in result:
    #     print(row)
    """
    4.直接传入 SQL 查询：
    Agent SQL: 
            SELECT p.name, SUM(o.quantity) AS total_sales
            FROM orders o
            JOIN products p ON o.product_id = p.id
            GROUP BY p.name
            ORDER BY total_sales DESC
            LIMIT 5;

    {'name': '苹果手机', 'total_sales': Decimal('6')}
    {'name': '耐克运动鞋', 'total_sales': Decimal('5')}
    {'name': '小米手机', 'total_sales': Decimal('3')}
    {'name': '阿迪达斯运动鞋', 'total_sales': Decimal('3')}
    {'name': '华为手机', 'total_sales': Decimal('2')}
    """

    db.close()
