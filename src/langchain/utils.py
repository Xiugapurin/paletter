from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings


def create_prompt_template(system_template):
    return ChatPromptTemplate.from_messages(
        [
            ("system", system_template),
            ("human", "{input}"),
        ]
    )


def split_text_to_list(time_stamp, content):
    text_splitter = CharacterTextSplitter(
        separator="\n\n",
        chunk_size=100,
        chunk_overlap=50,
        length_function=len,
        is_separator_regex=False,
    )

    content_list = text_splitter.split_text(content)

    return [f"{time_stamp} - {content}" for content in content_list]


def get_embedding(query):
    embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")

    return embeddings_model.embed_query(query)
