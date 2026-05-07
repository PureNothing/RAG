import trafilatura
import httpx
from app.logger import logger

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