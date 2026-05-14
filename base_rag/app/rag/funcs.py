from app.rag.config import settings
from langchain_redis import RedisChatMessageHistory
from urllib.parse import urlparse
import socket
import ipaddress
from app.logger import logger

def check_url(url: str) -> bool:
    logger.debug("Проверяю url..")
    try:
        result = urlparse(url=url)
        if result.scheme not in ("https", "http"):
            raise ValueError("Не допустимая схема url (не http и не https).")
        if ipaddress.ip_address(socket.getaddrinfo(result.hostname, None)[0][4][0]).is_private:
            raise ValueError("Приватный IP adress был отклонен")
        else:
            return
    except Exception as e:
        logger.warning(f"Url не прошел проверку - {url}. {e}")
        raise 


def get_session_history(session_id: str) -> RedisChatMessageHistory:
    return RedisChatMessageHistory(
        session_id=session_id,
        redis_url=settings.REDIS_URL,
        ttl=604800,
    )

async def clear_session_history(session_id: str) -> None:
    history = get_session_history(session_id=session_id)
    history.clear()


