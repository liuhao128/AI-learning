import logging
from typing import List, Optional

from langchain_community.chat_models import ChatTongyi
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage

from querying.query_prompt import REWRITE_PROMPT

logger = logging.getLogger(__name__)


class QueryRewriter:
    """ 查询改写器：消除指代，生成独立检索查询 """

    # 需要改写的关键词（存在这些词时触发改写）
    REFERENCE_KEYWORDS = ["那篇", "刚才", "它", "这个", "该", "那", "这", "其"]

    def __init__(self, llm: ChatTongyi) -> None:
        """
        初始化查询改写器
        :param llm: 大语言模型实例
        """
        self._llm = llm
        self._prompt = ChatPromptTemplate.from_messages([
            ("system", REWRITE_PROMPT),
            MessagesPlaceholder("chat_history"),
            ("human", "用户问题：{question}\n改写后的查询：")
        ])
        self._chain = self._prompt | llm | StrOutputParser()

    def rewrite(self,
                question: str,
                chat_history: List[BaseMessage]) -> str:
        """
        改写查询
        :param question: 用户原始问题
        :param chat_history: 对话历史
        :return: 改写后的查询
        """
        # 1. 参数校验
        question = (question or "").strip()
        if not question:
            return question

        # 2. 判断是否需要改写（短问题或无指代词的问题跳过）
        if not self._needs_rewrite(question):
            return question

        # 3. 执行改写
        try:
            chat_history = chat_history or []
            rewrite = self._chain.invoke({
                "question": question,
                "chat_history": chat_history
            })
            return rewrite
        except:
            return question

    def _needs_rewrite(self, question: str) -> bool:
        """
        判断问题是否需要改写
        :param question: 问题字符串
        :return: 是否需要改写
        """
        # 问题太短（少于5个字）或包含指代词
        if len(question) < 5:
            return False

        return any(kw in question for kw in self.REFERENCE_KEYWORDS)
