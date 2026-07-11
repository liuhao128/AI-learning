# Text-to-SQL 智能查询助手 — 代码实现说明

## 一、项目概述

本项目实现了一个基于 LangChain Agent 的 **Text-to-SQL 智能查询系统**。用户通过自然语言提问（如"销量排名前5的商品是哪些？"），系统自动理解意图、生成 SQL 查询语句、执行查询并将结果以中文回复给用户。

整个系统由三个核心文件组成：

| 文件 | 作用 |
|------|------|
| `db_init.sql` | 初始化 MySQL 数据库（建表 + 插入示例数据） |
| `db_manager.py` | 数据库连接与管理类，封装所有底层 SQL 操作 |
| `db_tools.py` | 将数据库操作包装为 LangChain 工具，驱动 Agent 完成自然语言到 SQL 的转换 |

---

## 二、环境依赖

在运行之前，需安装以下 Python 包：

```bash
pip install langchain langchain-community sqlalchemy pymysql tongyi-client
```

- **langchain / langchain-community**: Agent 框架和工具定义
- **sqlalchemy**: 数据库连接池与 ORM 反射
- **pymysql**: MySQL 驱动
- **tongyi-client**: 阿里云通义千问大模型 SDK（`ChatTongyi`）

---

## 三、数据库初始化（db_init.sql）

### 3.1 表结构

#### products（商品信息表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PRIMARY KEY AUTO_INCREMENT | 商品ID |
| name | VARCHAR(100) | NOT NULL | 商品名称 |
| category | VARCHAR(50) | NOT NULL | 商品类别 |

#### orders（订单记录表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INT | PRIMARY KEY AUTO_INCREMENT | 订单ID |
| product_id | INT | NOT NULL, FOREIGN KEY → products(id) | 关联商品ID |
| quantity | INT | NOT NULL | 购买数量 |
| order_date | DATE | NOT NULL | 订单日期 |

### 3.2 示例数据

- **products**: 8条记录（小米手机、华为手机、苹果手机、联想笔记本、耐克运动鞋、阿迪达斯运动鞋、格力空调、美的冰箱），分为电子产品/服装/家电三类。
- **orders**: 12条记录，分布在 2024-01 至 2024-03 之间。

### 3.3 初始化步骤

```bash
mysql -u root -p < db_init.sql
```

输入密码后会自动创建 `test` 数据库中的两张表并填充数据。

---

## 四、数据库管理类（db_manager.py）

### 4.1 类定义

```python
class DBManager:
    """
    数据库管理类，负责创建和管理 SQLAlchemy 连接。
    """
```

### 4.2 构造函数 `__init__`

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `username` | str | — | 数据库用户名 |
| `password` | str | — | 数据库密码 |
| `host` | str | `"localhost"` | 数据库主机地址 |
| `port` | int | `3306` | 端口号 |
| `database` | str | `""` | 数据库名 |
| `driver` | str | `"mysql+pymysql"` | SQLAlchemy 驱动协议 |
| `charset` | str | `"utf8mb4"` | 字符集 |
| `**kwargs` | — | — | 额外连接参数（透传给 `create_engine`） |

内部属性：
- `self._engine`: SQLAlchemy Engine 对象，初始为 `None`（懒加载）

### 4.3 私有方法

#### `_build_connection_string() -> str`

构建 SQLAlchemy 连接字符串，格式如下：

```
{driver}://{username}:{password}@{host}:{port}/{database}?charset={charset}[&key=value...]
```

例如：`mysql+pymysql://root:password@localhost:3306/test?charset=utf8mb4`

#### `_get_engine() -> Engine`

懒加载创建 SQLAlchemy Engine 对象。首次调用时创建连接池：

```python
create_engine(
    connection_string,
    pool_size=10,          # 连接池基础大小
    max_overflow=20,       # 超出基础大小后的最大溢出连接数
    pool_pre_ping=True,    # 使用前检测连接是否存活
    echo=False             # 不打印 SQL 日志
)
```

### 4.4 公共方法

#### `get_table_names() -> List[str]`

- **作用**: 获取数据库中所有表名列表
- **实现**: 通过 `sqlalchemy.inspect(engine).get_table_names()` 反射获取
- **返回值**: `["orders", "products", ...]`

#### `get_table_names_with_comments() -> Dict[str, str]`

- **作用**: 获取所有表名及其注释
- **实现**: 查询 `information_schema.tables` 中 `table_name` 和 `table_comment` 字段，过滤条件为当前数据库名
- **返回值**: `{"orders": "订单记录表", "products": "商品信息表"}`

#### `get_all_table_schemas() -> Dict[str, Dict]`

- **作用**: 获取所有表的完整结构信息（不含外键）
- **实现流程**:
  1. 调用 `get_table_names()` 获取所有表名
  2. 调用 `get_table_names_with_comments()` 获取表注释
  3. 对每张表，通过 `inspector.get_columns()` 获取字段信息（列名、类型、是否可空、默认值、注释、是否自增）
  4. 通过 `inspector.get_pk_constraint()` 获取主键列
  5. 通过 `inspector.get_indexes()` 获取索引（跳过主键索引）
- **返回值结构**:

```python
{
    "products": {
        "table_name": "products",
        "comment": "商品信息表",
        "columns": [
            {"name": "id", "type": "INTEGER", "nullable": False,
             "default": None, "comment": "商品ID", "auto_increment": True},
            {"name": "name", "type": "VARCHAR(100)", "nullable": False,
             "default": None, "comment": "商品名称", "auto_increment": False},
            {"name": "category", "type": "VARCHAR(50)", "nullable": False,
             "default": None, "comment": "商品类别", "auto_increment": False}
        ],
        "primary_keys": ["id"],
        "indexes": []
    }
}
```

#### `execute_query(sql: str) -> List[Dict[str, Any]]`

- **作用**: 执行 SELECT 查询语句，返回结果
- **参数**: `sql` — SELECT 查询语句字符串
- **实现流程**:
  1. 通过 `engine.connect()` 获取连接
  2. 使用 `text(sql)` 包装 SQL 执行
  3. 调用 `fetchall()` 获取所有行
  4. 从 `raw_result.keys()` 或 `raw_result.cursor.description` 提取列名
  5. 将每行元组转换为字典 `{column_name: value}`
- **返回值**: 字典列表，如 `[{"name": "苹果手机", "total_sales": 6}, ...]`
- **异常处理**: 捕获异常后重新抛出 `Exception("查询失败: ...")`

#### `close() -> None`

- **作用**: 关闭数据库连接池
- **实现**: 调用 `engine.dispose()` 并置 `self._engine = None`

---

## 五、Agent 工具层（db_tools.py）

### 5.1 整体架构

```
用户自然语言提问
       │
       ▼
┌─────────────────────┐
│   LangChain Agent    │  (基于 qwen3-max 大模型)
│   系统提示词指导行为   │
└────────┬────────────┘
         │ 决定调用哪个工具
         ▼
┌──────────────────────────────────┐
│  工具1: get_table_names          │  → 列出所有表
│  工具2: get_table_schema         │  → 展示表结构详情
│  工具3: execute_sql_query        │  → 执行 SQL 并返回结果
└──────────────────────────────────┘
         │
         ▼
   中文自然语言回复
```

### 5.2 数据库连接实例化

```python
from db_manager import DBManager

db = DBManager(
    username="root",
    password="254083",
    host="localhost",
    port=3306,
    database="test"
)
```

### 5.3 三个 LangChain 工具

#### 工具 1: `execute_sql_query`

```python
@tool
def execute_sql_query(sql: str) -> str:
    """执行 SQL 查询语句并返回结果。
    参数 sql: 要执行的 SELECT 查询语句
    返回: 查询结果的文本描述
    """
```

- **功能**: 调用 `db.execute_query(sql)` 执行查询
- **结果格式化**:
  - 结果为空 → 返回 `"查询结果为空"`
  - 单条结果 → 直接转为字符串返回
  - 多条结果 → 格式化为带序号的列表：
    ```
    共查询到 N 条记录：
      1. {行1内容}
      2. {行2内容}
      ...
    ```
- **异常处理**: 返回 `"查询失败: {错误信息}"`

#### 工具 2: `get_table_schema`

```python
@tool
def get_table_schema() -> str:
    """获取当前数据库的所有表结构信息，包括表名、字段、类型、主键等。
    返回: 表结构的文本描述
    """
```

- **功能**: 调用 `db.get_all_table_schemas()` 获取全部表结构
- **输出格式**:

```
【数据库表结构】

   表名: products
   注释: 商品信息表
   字段:
     - id (INTEGER) 非空 注释: 商品ID
     - name (VARCHAR(100)) 非空 注释: 商品名称
     - category (VARCHAR(50)) 非空 注释: 商品类别
   主键: id

   表名: orders
   注释: 订单记录表
   字段:
     - id (INTEGER) 非空 注释: 订单ID
     - product_id (INTEGER) 非空 注释: 商品ID
     - quantity (INTEGER) 非空 注释: 购买数量
     - order_date (DATE) 非空 注释: 订单日期
   主键: id
   索引:
     - product_id (普通): product_id
```

#### 工具 3: `get_table_names`

```python
@tool
def get_table_names() -> str:
    """获取数据库中所有表名列表。
    返回: 表名列表的文本描述
    """
```

- **功能**: 调用 `db.get_table_names()` 获取表名列表
- **输出格式**: `"数据库中的表有：orders, products"`

### 5.4 Agent 创建

```python
agent = create_agent(
    model=ChatTongyi(model="qwen3-max"),
    tools=[get_table_names, get_table_schema, execute_sql_query],
    system_prompt="""
你是一个专业的 SQL 查询助手。你的职责是根据用户的自然语言问题，生成准确的 SQL 查询语句并执行。

【工作流程】
1. 如果用户问的是"有哪些表"，直接调用 get_table_names
2. 如果需要了解表结构，调用 get_table_schema
3. 根据表结构生成正确的 SQL 查询语句
4. 调用 execute_sql_query 执行查询
5. 根据查询结果用中文回答用户

【重要规则】
- 只能使用 SELECT 查询，不能修改数据
- 生成 SQL 前必须先了解表结构
- 涉及多个表时使用 JOIN 关联
- 始终用中文回答用户
"""
)
```

- **模型**: 通义千问 qwen3-max
- **工具列表**: 上述三个 `@tool` 装饰的函数
- **系统提示词**: 定义了 Agent 的行为准则和工作流程

### 5.5 交互方式

#### 批量测试模式

```python
if __name__ == "__main__":
    questions = [
        "数据库里有哪些表？",
        "销量排名前5的商品是哪些？",
        "电子产品类的商品有哪些？",
        "苹果手机一共卖了多少台？",
    ]

    for question in questions:
        result = agent.invoke({
            "messages": [{"role": "user", "content": question}]
        })
        final_message = result["messages"][-1]
        print(f"AI: {final_message.content}")
```

- 每次调用 `agent.invoke()` 传入一条用户消息
- 从返回结果中提取最后一条消息作为 AI 的最终回复
- 最后调用 `db.close()` 关闭数据库连接

---

## 六、端到端执行流程

以用户提问 **"销量排名前5的商品是哪些？"** 为例：

```
Step 1: Agent 接收用户问题
Step 2: Agent 判断需要先了解表结构 → 调用 get_table_schema()
        → 返回 products 和 orders 表的完整结构
Step 3: Agent 根据表结构生成 SQL:
        SELECT p.name, SUM(o.quantity) AS total_sales
        FROM orders o
        JOIN products p ON o.product_id = p.id
        GROUP BY p.name
        ORDER BY total_sales DESC
        LIMIT 5
Step 4: Agent 调用 execute_sql_query(sql)
        → db.execute_query() 执行 SQL，返回 5 条字典记录
Step 5: Agent 将结果格式化为中文回复:
        "销量排名前5的商品是：
         1. 苹果手机 (6台)
         2. 耐克运动鞋 (5台)
         ..."
```

---

## 七、自定义与扩展

### 7.1 更换数据库

修改 `DBManager` 实例化的参数：

```python
db = DBManager(
    username="your_user",
    password="your_password",
    host="your_host",
    port=3306,
    database="your_database"
)
```

### 7.2 更换大模型

修改 `ChatTongyi` 的 model 参数，或替换为其他 LangChain 兼容的模型：

```python
from langchain_openai import ChatOpenAI

agent = create_agent(
    model=ChatOpenAI(model="gpt-4"),
    tools=[...],
    system_prompt=[...]
)
```

### 7.3 添加新工具

在 `db_tools.py` 中新增一个 `@tool` 装饰的函数，并将其加入 `tools` 列表：

```python
@tool
def my_custom_tool(param: str) -> str:
    """工具的文档字符串会被传递给 LLM 作为工具说明"""
    ...

agent = create_agent(
    model=...,
    tools=[get_table_names, get_table_schema, execute_sql_query, my_custom_tool],
    ...
)
```

### 7.4 修改系统提示词

在 `system_prompt` 中调整 Agent 的行为规则，例如允许写入操作、添加特定业务逻辑等。

---

## 八、注意事项

1. **安全性**: 系统提示词中限制了只能使用 SELECT 查询，但 `execute_query` 本身不做强校验。如需生产环境使用，应在 `db_manager.py` 的 `execute_query` 中添加 SQL 语法白名单检查（如正则匹配 `^SELECT\s`）。
2. **密码安全**: 数据库密码硬编码在代码中，建议改为环境变量或配置文件读取。
3. **并发**: `DBManager` 使用 SQLAlchemy 连接池，支持多线程并发查询。
4. **LangChain 版本**: 代码使用 `langchain_community` 的旧版 API（`create_agent`），注意与你安装的 LangChain 版本兼容。
