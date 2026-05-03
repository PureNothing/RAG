from langchain_huggingface import HuggingFaceEmbeddings
from transformers import AutoTokenizer 
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from qdrant_client import AsyncQdrantClient
from fastembed import SparseTextEmbedding
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
import os

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL")

QDRANT_URL = os.getenv("QDRANT_URL")

QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

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

llm = init_chat_model(
    model="openai/gpt-oss-120b",
    model_provider="groq",
    temperature=0.3,
    api_key=os.getenv("GROQ_API_KEY"),
)


embedding_model_bge_m3 = HuggingFaceEmbeddings(model_name="BAAI/bge-m3",
                                   model_kwargs={"device": "cpu"},
                                   encode_kwargs={"normalize_embeddings": True,
                                                  "batch_size": 32},
                                   )

qdrant_client = AsyncQdrantClient(
    url=QDRANT_URL,
    timeout=30,
    api_key=QDRANT_API_KEY
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
