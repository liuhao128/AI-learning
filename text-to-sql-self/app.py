import os
from dotenv import load_dotenv

load_dotenv()

from langchain_community.chat_models import ChatTongyi
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent

# ============================================
# 1. 连接 MySQL 数据库
# ============================================
db = SQLDatabase.from_uri(
    "mysql+pymysql://root:root@localhost:3306/demo"
)

print("✅ 数据库连接成功！")
print("📋 可用表：", db.get_usable_table_names())

# ============================================
# 2. 初始化通义千问大模型
# ============================================
llm = ChatTongyi(
    model="qwen-plus",
    temperature=0,
)

# ============================================
# 3. 创建 SQL 工具集
# ============================================
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
tools = toolkit.get_tools()

# ============================================
# 4. 定义系统提示词
# ============================================
system_message = SystemMessage(content="""你是一个专业的 SQL 数据分析师，负责根据用户的自然语言问题查询 MySQL 数据库并返回结果。

工作流程：
1. 先查看数据库中有哪些表可用
2. 根据需要查询相关表的 schema 信息，了解字段含义
3. 根据 schema 生成正确的 SELECT 查询语句并执行
4. 将结果整理为易读的中文回复

数据库表关系说明：
- users 表和 orders 表通过 users.id = orders.user_id 关联
- orders 表和 order_items 表通过 orders.id = order_items.order_id 关联
- products 表和 order_items 表通过 products.id = order_items.product_id 关联

重要规则：
- 只生成 SELECT 查询语句，禁止执行 INSERT、UPDATE、DELETE、DROP 等修改操作
- 生成的 SQL 必须符合 MySQL 语法
- 如果无法根据已有信息得到答案，请如实告知用户，不要编造答案
- 回复结果时，将数据整理为易读的格式（如表格或列表）
""")

# ============================================
# 5. 创建 ReAct Agent（LangGraph 方式）
# ============================================
agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=system_message,
)

# ============================================
# 6. 预设问题列表，批量执行
# ============================================
questions = [
    "查询所有杭州的用户",
    "查询年龄大于25岁的用户有哪些",
    "查询每个用户的订单数量",
    "查询销量最高的商品是哪个",
    "查询购买过耳机的用户姓名和城市",
    "查询每个城市的总消费金额，按金额从高到低排序",
]

for i, question in enumerate(questions, 1):
    print(f"\n{'=' * 50}")
    print(f"问题 {i}：{question}")
    print("-" * 50)

    try:
        result = agent.invoke(
            {"messages": [("user", question)]}
        )
        # 提取最后一条 AI 回复
        ai_message = result["messages"][-1].content
        print(f"AI：{ai_message}")
    except Exception as e:
        print(f"❌ 出错了：{e}")

print(f"\n{'=' * 50}")
print("✅ 所有问题执行完毕！")