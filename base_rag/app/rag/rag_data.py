import trafilatura
import httpx
import uuid
from langchain_community.document_loaders import WebBaseLoader
from langchain_core import documents
import re
from app.rag.config import qdrant_client, embedding_model_bge_m3, bm25_model_qdrantmb25, chunker_with_bge_m3, DENSE_SIZE
from app.logger import logger
from qdrant_client.models import Distance, VectorParams, SparseVectorParams, PointStruct, SparseVector, Modifier, Filter, FieldCondition, MatchValue, UpdateStatus


def user_collection_name(user_id: int) -> None:
    return f"user_{user_id}_docs"

async def ensure_collection(user_id: int) -> None:
    try:
        name = user_collection_name(user_id=user_id)
        exists = await qdrant_client.collection_exists(name)
        if not exists:
            logger.debug(f"Новый пользователь запросил создание коллекции.. {name}")
            await qdrant_client.create_collection(
                collection_name=name,
                vectors_config={
                    "dense": VectorParams(
                        size=DENSE_SIZE,
                        distance=Distance.COSINE,
                    )
                },
                sparse_vectors_config={
                    "sparse": SparseVectorParams(
                        modifier=Modifier.IDF
                    )
                },
            )
            logger.info(f"Коллекция успешно создана: {name}.")

            await qdrant_client.create_payload_index(
                collection_name=name,
                field_name="source",
                field_schema="keyword",
            )
            logger.info(f"Создан индекс на поле source для нового пользователя коллекции: {name}")

    except Exception as e:
        logger.error(f"Не удалось создать коллекцию с именем или провести индексацию: {name}. {e}")
        raise

async def web_extract(web_url: str) -> dict:
    logger.debug(f"Получена ссылка на извлечение данных {web_url}")
    try:
        async with httpx.AsyncClient(
            headers={"User-Agent": "Mozilla/5.0 (compatible; RAGbot/1.0)"},
            timeout=30,
            follow_redirects=True
        ) as client:
            logger.debug("Пробую извлечь данные..")
            response = await client.get(web_url)
            response.raise_for_status()
            html = response.text
            logger.info("Данные успешно скачаны, пробую достать текст из них..")
        
        result_text = trafilatura.bare_extraction(
            filecontent=html,
            url=web_url,
            include_comments=False,
            include_tables=True,
            favor_recall=True,
            favor_precision=False,
            include_images=False,
            include_links=False,
            no_fallback=False,
            deduplicate=True,
            max_tree_size=None,
            output_format="python",
            target_language='ru',
        )
        logger.info("Текст из html успешно получен!")

        result_text = result_text.as_dict()

        if not result_text or not result_text.get("text"):
            logger.error(f"Извлеченный текст оказался пустым из {web_url}.")
            raise ValueError(f"Не удалось извлечь контент с {web_url}")
            
        logger.info(f"Извлечено {len(result_text['text'])} символов")
        logger.info(f"Заголовок: {result_text.get('title', 'неизвестно')}")

        result_text["url"] = web_url

        return result_text
    
    except Exception as e:
        logger.error(f"Не удалось получить от ссылки ответ или извлечь контент, из преобразовать его в текст. {e}")
        raise


async def delete_dublicate_source(user_id: int, source_url: str) -> None:
    logger.debug("Проверяем есть ли дубликат..")

    try:
            
        collection_name = user_collection_name(user_id=user_id)

        exists = await qdrant_client.collection_exists(collection_name)
        if not exists:
            logger.debug("Коллекции у пользователя не было вообще, удалять нечего.")
            return
        
        result = await qdrant_client.delete(
            collection_name = collection_name,
            points_selector = Filter(
                must=[
                    FieldCondition(
                        key="source",
                        match=MatchValue(value=source_url)
                    )
                ]
            ),
            wait=True
        )

        if result.status == UpdateStatus.COMPLETED:
            logger.info(f"Дубликат был найден и удален успшено!")
        else:
            logger.info(f"Дубликата не было найдено, идем дальше. {result.status}")
    
    except Exception as e:
        logger.error(f"Не удалось удалить дубликат или подключить к БД. {e}")

async def chunk_and_embed(text: dict, user_id: int) -> int:
    try:

        splited_chunks = chunker_with_bge_m3.split_text(text=text["text"])

        chunks = [re.sub(r'\n+', ' ', chunk).strip() for chunk in splited_chunks]

        logger.info(f"Всего чанков после разделения: {len(chunks)}")

        logger.info("Пробрезаую чанки в dense и sparse вектора..")
        dense_vectors = embedding_model_bge_m3.embed_documents(chunks)
        sparse_vectors = list(bm25_model_qdrantmb25.embed(chunks))
        logger.info("Преобразование удалось!")

        logger.debug("Пробую добавить чанки в векторную БД..")

        points = []
        for idx, (chunk, dense, sparse) in enumerate(zip(chunks, dense_vectors, sparse_vectors)):
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector={
                        "dense": dense,
                        "sparse": SparseVector(
                            indices=sparse.indices.tolist(),
                            values=sparse.values.tolist(),
                        )
                    },
                    payload={
                        "user_id": user_id,
                        "text": chunk,
                        "source": text.get("url", ""),
                        "title": text.get("title", ""),
                        "chunk_idx": idx,
                    }
                )
            )

        await delete_dublicate_source(user_id=user_id, source_url=text.get("url", ""))
        await ensure_collection(user_id)
        await qdrant_client.upsert(
            collection_name=user_collection_name(user_id),
            points=points,
        )

        logger.debug("Чанки успешно векторизированы и добавлены в БД.")
        logger.info(f"Загружено {len(points)} векторов/чанков для user_id={user_id}")
    except Exception as e:
        logger.error(f"Не удалось векторизовать и загрузить эмбединги в БД {e}")


