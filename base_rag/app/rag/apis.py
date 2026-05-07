from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.rag.rag_data import chunk_and_embed
from app.rag.loaders.web_loader_rag import web_extract
from app.rag.rag_query import rag_answer
from app.auth.authfuncs import UserFuncs
from app.logger import logger
from app.rag.apischemas import Url, Question
from app.rag.funcs import check_url

router = APIRouter()

@router.post("/upload_url")
async def upload_url(web_url: Url, user_id: int = Depends(UserFuncs.get_current_user)):
    logger.debug(f"Получен url для индексации.")
    try:
        check_url(url=web_url.url)
    except Exception as e:
        logger.warning(f"Прислали недопстимый url. {e}")
        raise HTTPException(status_code=400, detail="Недопустимый url.")
    try:
        logger.debug("Начинаю индексацию url...")
        content= await web_extract(web_url=web_url.url)
        logger.debug("Конент извлечен, начинаю процесс чанкинга и эмбеддинга...")
    except Exception as e:
        logger.error(f"Ошибка при изввлечении контента: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при извлечении контента: {e}")
    try:
        await chunk_and_embed(text=content, user_id=user_id)
        logger.debug("Чанкинг и эмбеддинг успешно завершены.")
        return JSONResponse(status_code=200,content={"message": "Конент успешно прошел есь пайплайн. Пробуйте задать вопрос."})
    except Exception as e:
        logger.error(f"Ошибка при чанкинге и эмбеддинге: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при чанкинге и эмбеддинге: {e}")
    
@router.post("/rag_answer")
async def rag_answer_get(question: Question, user_id: int = Depends(UserFuncs.get_current_user)):
    logger.debug(f"Получен вопрос для RAG: {question.question}")
    try:
        logger.debug("Начинаю процесс ответа..")
        answer = await rag_answer(question=question.question, session_id=str(user_id), user_id=int(user_id))
        logger.debug("Ответ успешно получен.")
        return answer
    except Exception as e:
        logger.error(f"Ошибка при попытке получить ответ: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при попытке получить ответ: {e}")
    
