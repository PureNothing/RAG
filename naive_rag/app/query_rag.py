from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from config import model, RAG_PROMPT
from langchain_chroma import Chroma

embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3",
                                   model_kwargs={"device": "cpu"},
                                   encode_kwargs={"normalize_embeddings": True},
                                   )

vector_store = Chroma(
    collection_name="lenta-articles",
    embedding_function=embeddings,
    persist_directory="./chroma_db",
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", RAG_PROMPT),
        ("system", "Документы для ответа: {context}"),
        ("human", "Вопрос: {question}")
    ]
)

llm = model

question = "Какие фильмы точно заставят меня понервничать и поплакать? И объясни почему."

retriver_docs = vector_store.similarity_search(question, k=10)

docs_content = "\n".join([doc.page_content for doc in retriver_docs])

message = prompt.invoke({"question": question, "context": docs_content})

answer = llm.invoke(message)

print("Ответ:\n",answer.content)