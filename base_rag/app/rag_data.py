import bs4
from langchain_community.document_loaders import WebBaseLoader
from langchain_core import documents
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re
from config import vector_store
from logger import logger

async def web_extract(web_url: str) -> list:
    bs4_strainer = bs4.SoupStrainer("div", id=lambda x: x and x.startswith("articleBody_"))

    loader = WebBaseLoader(
        web_path=web_url,
        bs_kwargs={"parse_only": bs4_strainer}
)
    try:
        logger.debug("Начинаю процесс извлечения даннных с веб-страницы...")
        docs = await loader.load()
        logger.debug("Данные успешно извлечены.")
    except Exception as e:
        logger.error(f"Ошибка при извлеченни данных с веб-страницы: {e}.")
        raise

    for doc in docs:
        doc.page_content = re.sub(r'\n+', ' ', doc.page_content).strip()

    logger.info(f"Всего символов после извлечения: {len(docs[0].page_content)}")

    return docs

async def chunk_and_embed(docs: list) -> list:
    chunker = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)

    splited_chunks = chunker.split_documents(docs)

    logger.info(f"Всего чанков после разделения: {len(splited_chunks)}")

    try:
        logger.debug("Пробую добавить чанки в векторную БД..")
        added_chunks = await vector_store.add_documents(splited_chunks)
        logger.debug("Чанки успешно векторизированы и добавлены в БД.")
    except Exception as e:
        logger.error(f"Не удалось векторизовать и загрузить эмбединги в БД {e}")


    logger.info(f"Добавлено чанков в векторное хранилище - {len(added_chunks)}")
    logger.info(f"Всего векторов в базе {vector_store._collection.count()}")
