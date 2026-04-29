from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv
load_dotenv()

model = init_chat_model(
    model_provider="groq",
    model="openai/gpt-oss-120b",
    temperature=0.3,
    api_key=os.getenv("GROQ_API_KEY"),)


RAG_PROMPT = """
Ты - помощник, который отвечает на вопросы, используя информацию из предоставленных документов.
Если ты не знаешь ответа, скажи, что не знаешь.
Отвечай только на основании предоставленных документов, не добавляй никакой дополнительной информации.
Если в документах нет ответа на вопрос скажи что не знаешь.
Отвечай без markdown разметки.
Отвечай на русском языке.
"""