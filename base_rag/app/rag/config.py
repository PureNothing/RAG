from langchain_huggingface import HuggingFaceEmbeddings
from transformers import AutoTokenizer 
from langchain_openai import ChatOpenAI
from qdrant_client import AsyncQdrantClient
from fastembed import SparseTextEmbedding
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    REDIS_URL: str
    
    QDRANT_URL: str
    QDRANT_API_KEY: str

    GROQ_API_KEY: str
    OPEN_ROUTER_API_KEY: str
    POLZAAI_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()

DENSE_SIZE = 1024

tokenizer_bge_m3 = AutoTokenizer.from_pretrained("BAAI/bge-m3")

bm25_model_qdrantmb25 = SparseTextEmbedding(model_name="Qdrant/bm25")

chunker_with_bge_m3 = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=50,
    length_function=lambda text: len(tokenizer_bge_m3.encode(text)),
    separators=["\n\n", "\n", ". ", " ", ""]
)

reranker_bge_v2_m3 = HuggingFaceCrossEncoder(
    model_name="BAAI/bge-reranker-v2-m3",
    model_kwargs={"device": "cpu"}
)

llm = ChatOpenAI(
    model="openai/gpt-4o-mini",
    temperature=0.3,
    api_key=settings.POLZAAI_API_KEY,
    base_url="https://polza.ai/api/v1"
)


embedding_model_bge_m3 = HuggingFaceEmbeddings(model_name="BAAI/bge-m3",
                                   model_kwargs={"device": "cpu"},
                                   encode_kwargs={"normalize_embeddings": True,
                                                  "batch_size": 32},
                                   )

qdrant_client = AsyncQdrantClient(
    url=settings.QDRANT_URL,
    timeout=30,
    api_key=settings.QDRANT_API_KEY
)

RAG_PROMPT = """
    Ты - помощник, который отвечает на вопросы, используя информацию из предоставленных документов.
    Если ты не знаешь ответа, скажи, что не знаешь.
    Отвечай только на основании предоставленных документов, не добавляй никакой дополнительной информации.
    Если в документах нет ответа на вопрос скажи что не знаешь.
    Так же ты можешь отвечать на вопросы ответы на которые у тебя уже есть в истории сообщений.
    Отвечай без markdown разметки.
    Отвечай на русском языке.
    В конце ответа указывай источник: [Источник: URL]
    """
