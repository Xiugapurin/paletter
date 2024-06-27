from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from .prompts import create_prompt_template, create_prompt_template_with_history
from .history import get_session_history


def get_llm_response(user_message, system_template, llm_preference):
    prompt = create_prompt_template(
        system_template.format(llm_preference=llm_preference)
    )
    model = ChatOpenAI(model="gpt-3.5-turbo-0125")
    runnable = prompt | model | StrOutputParser()
    response = runnable.invoke({"input": user_message})

    return response


def get_llm_response_with_history(user_message, session_id, system_template):
    prompt = create_prompt_template_with_history(system_template)
    model = ChatOpenAI(model="gpt-3.5-turbo-0125")
    runnable = prompt | model
    runnable_with_history = RunnableWithMessageHistory(
        runnable,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )
    response = runnable_with_history.invoke(
        {"input": user_message},
        config={"configurable": {"session_id": session_id}},
    )
    return response
