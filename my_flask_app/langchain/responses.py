from typing import List

from datetime import datetime
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from .prompts import create_prompt_template
from .templates import (
    response_clue_template,
    response_template,
    response_emotion_template,
    diary_to_color_template,
    diary_to_tag_summary_template,
)


class MessageEmotion(BaseModel):
    emotion: str = Field(description="The emotion of the message")


class DiaryEmotion(BaseModel):
    color: str = Field(description="Emotion color based on the diary content")
    content: str = Field(description="Content of the diary representing the emotion")


class DiaryEmotionList(BaseModel):
    colors: List[DiaryEmotion]


class DiarySummary(BaseModel):
    tag: str = Field(description="The tag for the diary")
    summary: str = Field(description="Summary of the given diary content")


def get_embedding(query):
    embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")

    return embeddings_model.embed_query(query)


def get_emotion(content):
    model = ChatOpenAI(model="gpt-4o")

    parser = JsonOutputParser(pydantic_object=MessageEmotion)
    prompt = PromptTemplate(
        template=response_emotion_template,
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | model | parser
    output = chain.invoke({"query": content})

    return output["emotion"]


def split_response_chain(content):
    split_prompt = create_prompt_template(
        "請將以下聊天的內容，根據語義和情緒轉折，切分成每段長度不超過 20 字的多段文本：\n"
        "{input}"
    )
    model = ChatOpenAI(model="gpt-4o")
    runnable = split_prompt | model | StrOutputParser()
    response = runnable.invoke({"input": content})
    messages = response.split("\n")

    processed_messages = []
    for msg in messages:
        msg = msg.strip()
        if msg.endswith("。") or msg.endswith("，"):
            msg = msg[:-1].strip()
        if msg:
            processed_messages.append(msg)

    return processed_messages


def get_chat_responses(
    user_message, llm_preference, chat_history_context, diary_context
):
    model = ChatOpenAI(model="gpt-4o")
    today = datetime.now().date().isoformat()
    clue_prompt = PromptTemplate(
        template=response_clue_template,
        input_variables=["query"],
        partial_variables={"diary_context": diary_context, "date": today},
    )
    runnable = clue_prompt | model | StrOutputParser()
    clue = runnable.invoke({"query": user_message})

    system_template = response_template.format(
        llm_preference=llm_preference,
        chat_history_context=chat_history_context,
        clue=clue,
        date=today,
    )
    print(system_template)
    prompt = create_prompt_template(system_template)
    runnable = prompt | model | StrOutputParser()
    content = runnable.invoke({"input": user_message})

    emotion = get_emotion(content)
    responses = split_response_chain(content)

    return responses, emotion


def convert_diary_to_colors(diary_content):
    parser = JsonOutputParser(pydantic_object=DiaryEmotionList)
    prompt = PromptTemplate(
        template=diary_to_color_template,
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    model = ChatOpenAI(model="gpt-4o")
    chain = prompt | model | parser
    output = chain.invoke({"query": diary_content})

    unique_colors = []
    seen_colors = set()

    for color_obj in output["colors"]:
        if color_obj["color"] not in seen_colors:
            seen_colors.add(color_obj["color"])
            unique_colors.append(color_obj)
        if len(unique_colors) >= 2:
            break

    return unique_colors


def convert_diary_to_summary(diary_content):
    parser = JsonOutputParser(pydantic_object=DiarySummary)
    prompt = PromptTemplate(
        template=diary_to_tag_summary_template,
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    model = ChatOpenAI(model="gpt-4o")
    runnable = prompt | model | parser
    summary_item = runnable.invoke({"query": diary_content})

    summary_item["summary_embedding"] = get_embedding(summary_item["summary"])

    return summary_item
