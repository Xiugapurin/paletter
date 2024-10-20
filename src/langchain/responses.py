from typing import List
from enum import Enum

from datetime import datetime
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import (
    PydanticOutputParser,
    StrOutputParser,
    JsonOutputParser,
)
from pydantic import BaseModel, Field
from .prompts import create_prompt_template
from .templates.paletter import (
    response_clue_template,
    basic_response_template,
    premium_response_template,
    response_split_template,
    response_emotion_template,
    diary_html_to_text_template,
    diary_to_color_template,
    diary_to_tag_summary_template,
)
from .templates.diary import diary_emotion_template


class MessageEmotion(BaseModel):
    emotion: str = Field(description="The emotion of the message")


class MessageContent(BaseModel):
    content: str = Field(description="The content of the message")


class MessageList(BaseModel):
    messages: List[MessageContent]


class DiaryEmotion(BaseModel):
    color: str = Field(description="Emotion color based on the diary content")
    content: str = Field(description="Content of the diary representing the emotion")


class DiaryEmotionList(BaseModel):
    colors: List[DiaryEmotion]


class DiarySummary(BaseModel):
    tag: str = Field(description="The tag for the diary")
    summary: str = Field(description="Summary of the given diary content")


class EmotionEnum(str, Enum):
    angry_irritable = "Red"
    happy_joyful = "Yellow"
    sad_upset = "Blue"
    fearful_afraid = "Purple"
    anxious_worried = "Orange"
    disgusted_annoyed = "Green"
    calm_peaceful = "Indigo"
    helpless_wronged = "Gray"
    unclassified = "White"


class DiaryEntryEmotion(BaseModel):
    emotion: EmotionEnum = Field(description="The emotion of the diary entry")


def get_embedding(query):
    embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")

    return embeddings_model.embed_query(query)


def get_emotion(content):
    model = ChatOpenAI(model="gpt-4o-mini")

    parser = JsonOutputParser(pydantic_object=MessageEmotion)
    prompt = PromptTemplate(
        template=response_emotion_template,
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain = prompt | model | parser
    output = chain.invoke({"query": content})

    return output["emotion"]


def get_diary_emotion(
    diary_content,
):
    if len(diary_content) <= 10:
        return "White"
    parser = PydanticOutputParser(pydantic_object=DiaryEntryEmotion)
    model = ChatOpenAI(model="gpt-4o-mini")

    prompt = PromptTemplate(
        template=diary_emotion_template,
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    runnable = prompt | model | parser

    output = runnable.invoke({"query": diary_content})

    emotion = output.emotion.value

    return emotion


def split_response_chain(content):
    parser = JsonOutputParser(pydantic_object=MessageList)
    prompt = PromptTemplate(
        template=response_split_template,
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    model = ChatOpenAI(model="gpt-4o-mini")
    chain = prompt | model | parser

    output = chain.invoke({"query": content})

    processed_messages = []
    for msg in output["messages"]:
        msg = msg["content"]
        if msg.endswith("。") or msg.endswith("，"):
            msg = msg[:-1]
        if msg:
            processed_messages.append(msg.strip())

    return processed_messages


def get_chat_responses(
    user_message,
    user_name,
    llm_preference,
    chat_history_context,
    relevant_diary_context,
    today_diary_context,
    membership_level,
):
    today = datetime.now().date().isoformat()
    date_time = datetime.now().strftime("%y/%m/%d 的 %H:%M")
    llm_preference = llm_preference if llm_preference else "友善體貼且幽默"
    chat_history_context = (
        chat_history_context
        if chat_history_context
        else "沒有任何聊天記錄，請試著向朋友問好哦"
    )

    if membership_level == "Basic":
        model = ChatOpenAI(model="gpt-4o-mini")

        # system_template = basic_response_template.format(
        #     llm_preference=llm_preference,
        #     chat_history_context=chat_history_context,
        # )

        system_template = basic_response_template.format(
            date_time=date_time,
            user_name=user_name,
            chat_history_context=chat_history_context,
        )

    if membership_level == "Premium":
        model = ChatOpenAI(model="gpt-4o")

        clue_prompt = PromptTemplate(
            template=response_clue_template,
            input_variables=["query"],
            partial_variables={
                "relevant_diary_context": relevant_diary_context,
                "today_diary_context": today_diary_context,
                "date": today,
            },
        )
        runnable = clue_prompt | model | StrOutputParser()
        clue = runnable.invoke({"query": user_message})

        system_template = premium_response_template.format(
            llm_preference=llm_preference,
            chat_history_context=chat_history_context,
            clue=clue,
            date=today,
        )

    print(system_template)
    prompt = create_prompt_template(system_template)
    runnable = prompt | model | StrOutputParser()
    content = runnable.invoke({"input": user_message})

    # emotion = get_emotion(content)
    emotion = "None"
    responses = split_response_chain(content)

    return responses, emotion


def convert_diary_html_to_text(diary_html):
    prompt = PromptTemplate(
        template=diary_html_to_text_template,
        input_variables=["query"],
    )
    model = ChatOpenAI(model="gpt-4o")
    runnable = prompt | model | StrOutputParser()
    text = runnable.invoke({"query": diary_html})

    return text


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
