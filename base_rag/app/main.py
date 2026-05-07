from fastapi import FastAPI
import app.rag.apis as ragapis
import app.auth.apis as authapis
from contextlib import asynccontextmanager
from app.logger import logger
from app.auth.dbfuncs import BDfuncs
import uvicorn 

@asynccontextmanager
async def lifespawn(app: FastAPI):
    logger.debug("="*30)
    logger.info("Запускаю RAG сервис")
    try:
        logger.debug("Удаляю и поднимаю БД, запускаю API")
        await BDfuncs.create_tables()
        logger.info("БД успено пересоздана")
        logger.info("Инициализирую векторное хранилище и модель..")
        from app.rag.config import qdrant_client, embedding_model_bge_m3, llm, bm25_model_qdrantmb25, tokenizer_bge_m3
        logger.info("Векторное хранилище и модель инициализированы.")
        yield
    except Exception as e:
        logger.error(f"Ошибка при инициализации: {e}")
        raise

app = FastAPI(lifespan=lifespawn)

app.include_router(ragapis.router)
app.include_router(authapis.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", port=8005, reload=False)