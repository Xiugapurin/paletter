from typing import List
from enum import Enum

from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.schema.runnable import RunnableParallel
from langchain_core.output_parsers import (
    PydanticOutputParser,
    StrOutputParser,
    JsonOutputParser,
)
from pydantic import BaseModel, Field
from .utils import create_prompt_template
from .templates.paletter import paletter_setting_templates
from .templates.chat import (
    basic_chat_template,
    response_clue_template,
    premium_chat_template,
    response_split_template,
)
from .templates.diary import diary_emotion_template, diary_title_template
from .templates.reply import basic_reply_template, stranger_reply_template
from .templates.report import basic_report_template


class MessageContent(BaseModel):
    content: str = Field(description="The content of the message")


class MessageList(BaseModel):
    messages: List[MessageContent]


class EmotionEnum(str, Enum):
    angry_agitated_irritable = "Red"
    excited_surprised_joyous = "Orange"
    happy_content_joyful = "Yellow"
    calm_relaxed_easygoing = "Green"
    tired_weary_sleepy = "Blue"
    sad_depressed_dismal = "Indigo"
    frustrated_annoyed_distressed = "Purple"
    tense_scared_terrified = "Pink"
    unclassified = "White"


class DiaryEntryEmotion(BaseModel):
    emotion: EmotionEnum = Field(description="The emotion of the diary entry")


def get_diary_emotion(
    diary_content,
):
    if len(diary_content) <= 10:
        return "White"

    parser = PydanticOutputParser(pydantic_object=DiaryEntryEmotion)
    model = ChatOpenAI(model="gpt-4o-mini")

    diary_emotion_prompt = PromptTemplate(
        template=diary_emotion_template,
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    runnable = diary_emotion_prompt | model | parser
    output = runnable.invoke({"query": diary_content})
    emotion = output.emotion.value

    return emotion


def get_diary_title_and_emotion(
    diary_content,
):
    timestamp = datetime.now().strftime("%H:%M")
    if len(diary_content) <= 10:
        return "心情小記", "White"

    parser = PydanticOutputParser(pydantic_object=DiaryEntryEmotion)
    model = ChatOpenAI(model="gpt-4o-mini")

    emotion_prompt = PromptTemplate(
        template=diary_emotion_template,
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    emotion_chain = emotion_prompt | model | parser

    system_template = diary_title_template.format(timestamp=timestamp)
    title_prompt = create_prompt_template(system_template)
    title_chain = title_prompt | model | StrOutputParser()

    parallel_chain = RunnableParallel(emotion=emotion_chain, title=title_chain)
    output = parallel_chain.invoke({"query": diary_content, "input": diary_content})

    return output["title"], output["emotion"].emotion.value


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
    relevant_context,
    today_diary_context,
    membership_level,
):
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

        system_template = basic_chat_template.format(
            settings=setting_template,
            date_time=date_time,
            paletter_name=paletter_name,
            user_name=user_name,
            chat_history_context=chat_history_context,
        )

    if membership_level == "Premium":
        model = ChatOpenAI(model="gpt-4o-mini")

        clue_template = response_clue_template.format(
            date_time=date_time,
            message=user_message,
            relevant_context=relevant_context,
            chat_history_context=chat_history_context,
            today_diary_context=today_diary_context,
        )
        clue_prompt = create_prompt_template(clue_template)
        clue_runnable = clue_prompt | model | StrOutputParser()
        clues = clue_runnable.invoke({"input": user_message})

        print("CLUE:\n" + clue_template)

        system_template = premium_chat_template.format(
            settings=setting_template,
            date_time=date_time,
            paletter_name=paletter_name,
            user_name=user_name,
            clues=clues,
            chat_history_context=chat_history_context,
            today_diary_context=today_diary_context,
        )

    print(system_template)
    prompt = create_prompt_template(system_template)
    runnable = prompt | model | StrOutputParser()
    content = runnable.invoke({"input": user_message})

    responses = split_response_chain(content)

    return responses


def get_diary_reply(
    user_name, paletter_code, paletter_name, days, intimacy_level, diary_content
):

    setting_template = paletter_setting_templates[paletter_code].format(
        user_name=user_name,
        days=days,
    )

    if intimacy_level == "0":
        system_template = stranger_reply_template.format(
            settings=setting_template, paletter_name=paletter_name
        )
    else:
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


def get_weekly_report(user_name, days, entry_contents, message_contents):
    setting_template = paletter_setting_templates["Pal-1"].format(
        user_name=user_name,
        days=days,
    )

    system_template = basic_report_template.format(
        settings=setting_template,
        user_name=user_name,
        diary_contents=entry_contents,
        message_contents=message_contents,
    )

    print(system_template)
    requirement = "請給我一篇能夠根據我過去一週的表現，以喵喵視角客製化的個人報告。"

    model = ChatOpenAI(model="gpt-4o-mini", max_tokens=1000)
    prompt = create_prompt_template(system_template)
    runnable = prompt | model | StrOutputParser()
    report = runnable.invoke({"input": requirement})

    return report
