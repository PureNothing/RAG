from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.rag.rag_data import web_extract, chunk_and_embed
from app.rag.rag_query import rag_answer
from app.auth.authfuncs import UserFuncs
from app.logger import logger

@asynccontextmanager
async def lifespawn(router):
    logger.debug("="*30)
    logger.info("Запускаю RAG сервис")
    try:
        logger.info("Инициализирую векторное хранилище и модель..")
        from base_rag.app.rag.config import qdrant_client, embedding_model_bge_m3, llm, bm25_model_qdrantmb25, tokenizer_bge_m3
        logger.info("Векторное хранилище и модель инициализированы.")
        yield
    except Exception as e:
        logger.error(f"Ошибка при инициализации: {e}")
        raise

router = APIRouter(lifespan=lifespawn)

@router.post("/upload_url")
async def upload_url(web_url: str, user_id: int = Depends(UserFuncs.get_current_user)):
    logger.debug(f"Получен url для индексации.")
    try:
        logger.debug("Начинаю индексацию url...")
        content= await web_extract(web_url=web_url)
        logger.debug("Конент извлечен, начинаю процесс чанкинга и эмбеддинга...")
    except Exception as e:
        logger.error(f"Ошибка при изввлечении контента: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при извлечении контента: {e}")
    try:
        await chunk_and_embed(text=content, user_id=user_id)
        logger.debug("Чанкинг и эмбеддинг успешно завершены.")
        return JSONResponse(status_code=200,content={"message": "Конент успешно прошел есь пайплайн."})
    except Exception as e:
        logger.error(f"Ошибка при чанкинге и эмбеддинге: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при чанкинге и эмбеддинге: {e}")
    
@router.post("/rag_answer")
async def rag_answer_get(question: str, user_id: int = Depends(UserFuncs.get_current_user)):
    logger.debug(f"Получен вопрос для RAG: {question}")
    try:
        logger.debug("Начинаю процесс ответа..")
        answer = await rag_answer(question=question, session_id=str(user_id), user_id=int(user_id))
        logger.debug("Ответ успешно получен.")
        return answer
    except Exception as e:
        logger.error(f"Ошибка при попытке получить ответ: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при попытке получить ответ: {e}")
    
