
from core_copy.intent_recognizer_copy import IntentRecognizer

if __name__ == '__main__':
    from langchain_community.chat_models import ChatTongyi
    # llm = ChatTongyi(model="qwen3-max")
    llm = ChatTongyi(model="qwen-flash")
    #
    recognize = IntentRecognizer(llm)

    print("意图识别结果：==============")

    result = recognize.recognize("我的订单号是06715421bjfab412")

    print(result)