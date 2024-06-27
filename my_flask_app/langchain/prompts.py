from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def create_prompt_template(system_template):
    return ChatPromptTemplate.from_messages(
        [
            ("system", system_template),
            ("human", "{input}"),
        ]
    )


def create_prompt_template_with_history(system_template):
    return ChatPromptTemplate.from_messages(
        [
            ("system", system_template),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )
