from langchain_core.prompts import ChatPromptTemplate


def create_prompt_template(system_template):
    return ChatPromptTemplate.from_messages(
        [
            ("system", system_template),
            ("human", "{input}"),
        ]
    )
