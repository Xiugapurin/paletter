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
from .templates.paletter import paletter_setting_templates
from .templates.chat import (
    basic_chat_template,
    response_clue_template,
    premium_response_template,
    response_split_template,
)
from .templates.diary import diary_emotion_template
from .templates.reply import basic_reply_template


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
    paletter_code,
    paletter_name,
    days,
    chat_history_context,
    relevant_diary_context,
    today_diary_context,
    membership_level,
):
    today = datetime.now().date().isoformat()
    date_time = datetime.now().strftime("20%y/%m/%d 的 %H:%M")
    chat_history_context = (
        chat_history_context
        if chat_history_context
        else "沒有任何聊天記錄，請試著向朋友問好哦"
    )

    setting_template = paletter_setting_templates[paletter_code].format(
        user_name=user_name, days=days
    )

    if membership_level == "Basic":
        model = ChatOpenAI(model="gpt-4o-mini")
        # system_template = basic_response_template.format(
        #     date_time=date_time,
        #     user_name=user_name,
        #     chat_history_context=chat_history_context,
        # )

        system_template = basic_chat_template.format(
            settings=setting_template,
            date_time=date_time,
            paletter_name=paletter_name,
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
    if paletter_code != "Blue-1":
        responses = split_response_chain(content)
    else:
        responses = [content]

    return responses, emotion


def get_diary_reply(
    user_name, paletter_code, paletter_name, days, intimacy_level, diary_content
):

    setting_template = paletter_setting_templates[paletter_code].format(
        user_name=user_name,
        days=days,
    )

    system_template = basic_reply_template.format(
        settings=setting_template,
        paletter_name=paletter_name,
        user_name=user_name,
        intimacy_level=intimacy_level,
    )

    model = ChatOpenAI(model="gpt-4o-mini")
    prompt = create_prompt_template(system_template)
    runnable = prompt | model | StrOutputParser()
    reply = runnable.invoke({"input": diary_content})

    return reply


# def get_diary_reply(diary_content):
#     prompt = PromptTemplate(
#         template=diary_to_tag_summary_template,
#         input_variables=["query"],
#     )
#     model = ChatOpenAI(model="gpt-4o")
#     runnable = prompt | model | StrOutputParser()
#     summary = runnable.invoke({"query": diary_content})

#     return summary
