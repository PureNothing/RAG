from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import os

load_dotenv()

llm = init_chat_model(
    model="gpt-oss-120b",
    model_provider="groq",
    temperature=0.3,
    api_key=os.getenv("GROQ_API_KEY"),
)


embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-m3",
                                   model_kwargs={"device": "cpu"},
                                   encode_kwargs={"normalize_embeddings": True},
                                   )

vector_store = Chroma(
    collection_name="films",
    embedding_function=embedding_model,
    persist_directory="./chroma_db",
)

RAG_PROMPT = """
    Ты - помощник, который отвечает на вопросы, используя информацию из предоставленных документов.
    Если ты не знаешь ответа, скажи, что не знаешь.
    Отвечай только на основании предоставленных документов, не добавляй никакой дополнительной информации.
    Если в документах нет ответа на вопрос скажи что не знаешь.
    Отвечай без markdown разметки.
    Отвечай на русском языке.
    """