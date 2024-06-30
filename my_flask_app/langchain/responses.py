from typing import List

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from .prompts import create_prompt_template


class EmotionAnalysis(BaseModel):
    color: str = Field(description="Emotion color based on the diary content")
    content: str = Field(description="Content of the diary representing the emotion")


class EmotionAnalysisList(BaseModel):
    colors: List[EmotionAnalysis]


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


def convert_diary_to_colors(diary_content):
    parser = JsonOutputParser(pydantic_object=EmotionAnalysisList)
    prompt = PromptTemplate(
        template="""你是一個專業的心理學家，你擅長分析日記中所包含的情緒。 \
                    你需要根據使用者的日記內容分析其情緒，並挑選其代表的顏色以及對應的內容段落。 \
                    注意：每個段落不要超過 100 字，同時不要回傳日記以外的內容。 \
                    限制：你最少需要挑選一個顏色，並且最多挑選不超過兩個顏色，請挑選日記中最具有代表性的段落。 \
                    以下是 8 種不同的情緒所對應的顏色: \
                    1. 憤怒暴躁: Red \
                    2. 快樂喜悅: Yellow \
                    3. 悲傷難過: Blue \
                    4. 恐懼害怕: Purple \
                    5. 焦慮不安: Orange \
                    6. 厭惡煩躁: Green \
                    7. 平靜祥和: Indigo \
                    8. 其他 (當日記不包含任何情緒或是沒有內容時): Gray \

                    {format_instructions}

                    {query}
                """,
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    model = ChatOpenAI(model="gpt-3.5-turbo-0125")
    chain = prompt | model | parser
    output = chain.invoke({"query": diary_content})

    print(output)
    return output["colors"][:2]
