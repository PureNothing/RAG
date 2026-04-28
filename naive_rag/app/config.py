from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv
load_dotenv(".env")

model = init_chat_model(
    model_provider="groq",
    model="openai/gpt-oss-120b",
    temperature=0.3,
    api_key=os.getenv("GROQ_API_KEY"),)