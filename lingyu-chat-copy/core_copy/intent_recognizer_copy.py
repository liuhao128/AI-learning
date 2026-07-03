import json
import re
from typing import Any
from dataclasses import dataclass
from langchain_community.chat_models import ChatTongyi
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from .prompt_copy import INTENT_RECOGNIZE_PROMPT


@dataclass(frozen=True)
class IntentResult:
    intents: list[str]
    slots: dict[str, Any]
    confidence: float


class IntentRecognizer:

    def __init__(self, llm: ChatTongyi) -> None:
        """
        初始化意图识别
        :param llm: 大语言模型
        """
        self.__prompt = ChatPromptTemplate.from_messages([
            ("system", INTENT_RECOGNIZE_PROMPT),
            ("ai", "上下文内容：{chat_history}"),
            ("human", "用户输入：{user_input}")
        ])
        self.__llm = llm
        self.__chain = self.__prompt | self.__llm | StrOutputParser()


    def recognize(self, user_input: str, chat_history: str | None = None) -> IntentResult:
        """
        识别用户输入的意图
        :param chat_history:上下文内容
        :param user_input:用户输入的文本
        :return:意图识别结果
        """
        chat_history = chat_history if chat_history else ""
        result = self.__chain.invoke(input={"chat_history": chat_history, "user_input": user_input})

        data = self.__parse_str_to_json(result)

        intents = data.get("intents")
        if not isinstance(intents, list):
            intent = data.get("intent")
            intents = [intent] if isinstance(intent, str) else []
        slot = data.get("slots") if isinstance(data.get("slots"), dict) else {}
        try:
            confidence = float(data.get("confidence"))
        except ValueError:
            confidence = 0.0
        confidence = max(0.0, min(1.0, confidence))
        return IntentResult(intents, slot, confidence)


    def __parse_str_to_json(self, text: str) -> dict[str, Any]:
        """
        将text解析为dict字典类型
        :param text: 待解析的字符串
        :return: 解析后的dict字典
        """
        if not text and not text.strip():
            return {"intents": ["general"], "slots": {}, "confidence": 0.0}
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        find_text = re.search(r"{{.*?}}", text, re.DOTALL)
        if find_text:
            try:
                return json.loads(find_text.group(0))
            except json.JSONDecodeError:
                pass

        return {"intents": ["general"], "slots": {}, "confidence": 0.0}





