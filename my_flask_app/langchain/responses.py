from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from .prompts import create_prompt_template


def split_response_chain(content):
    split_prompt = create_prompt_template(
        "請將以下聊天的內容，根據語義和情緒轉折，切分成每段長度不超過 20 字的多段文本：\n"
        "{input}"
    )
    model = ChatOpenAI(model="gpt-3.5-turbo-0125")
    runnable = split_prompt | model | StrOutputParser()
    response = runnable.invoke({"input": content})
    messages = response.split("\n")

    return [msg.strip() for msg in messages if msg.strip()]


def get_chat_responses(user_message, llm_preference, context):
    system_template = (
        "以下對話請以繁體中文與使用者應答，"
        "回答的長度請不要超過 100 字。\n"
        "你現在必須扮演一隻來自魔法國度的精靈，"
        "作為使用者的夥伴，請不要透露自己AI的身份。\n"
        "注意：你是一隻虛擬世界的精靈，你無法和使用者在真實世界見面。\n"
        "精靈的個性設定如下：\n"
        "{llm_preference}\n\n"
        "請根據先前的聊天紀錄，決定如何與使用者對話。以下是先前的聊天紀錄上下文：\n"
        "{context}\n"
    ).format(llm_preference=llm_preference, context=context)
    prompt = create_prompt_template(system_template)
    model = ChatOpenAI(model="gpt-3.5-turbo-0125")
    runnable = prompt | model | StrOutputParser()
    content = runnable.invoke({"input": user_message})
    responses = split_response_chain(content)

    return responses
