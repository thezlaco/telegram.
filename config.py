import os
from urllib.parse import urlparse
from typing import Dict, Any, List, Optional
import aiohttp
from dotenv import load_dotenv
from logger import log_color
from error import errorcake

logger = log_color(__name__)
load_dotenv()

class Config:
    """Конфигурация приложения и утилиты для работы с API."""
    
    # Основные настройки
    TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN")
    API_KEY: str = os.getenv("AI_API_KEY")
    API_URL: str = "https://openrouter.ai/api/v1/chat/completions"
    MAX_RESPONSE_LENGTH: int = 4096  # Лимит Telegram
    TIMEOUT: int = 60  # Таймаут для длинных запросов
    SHORT_TIMEOUT: int = 10  # Таймаут для коротких операций

    # Параметры AI-запросов
    AI_PARAMS: Dict[str, Any] = {
        "model": "openai/gpt-3.5-turbo",
        "temperature": 1.2,
        "top_p": 1.0,
        "frequency_penalty": 1.5,
        "presence_penalty": 0.8,
    }

    @staticmethod
    def get_ai_request_data(messages: List[Dict[str, str]], max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """Генерирует тело запроса для API с гарантией валидности."""
        if not messages:
            errorcake("empty_messages_request")
            raise ValueError("Список сообщений не может быть пустым")
            
        request_data = {
            **Config.AI_PARAMS,
            "messages": messages,
            "stream": False
        }
        if max_tokens is not None:
            request_data["max_tokens"] = max_tokens
        return request_data

    @staticmethod
    def get_timeout(long_request: bool = True) -> aiohttp.ClientTimeout:
        """Возвращает таймаут в зависимости от типа запроса."""
        return aiohttp.ClientTimeout(
            total=Config.TIMEOUT if long_request else Config.SHORT_TIMEOUT
        )

    @staticmethod
    def split_response(response: str) -> List[str]:
        """Оптимизированное разделение текста на части."""
        if len(response) <= Config.MAX_RESPONSE_LENGTH:
            return [response]

        parts = []
        while response:
            # Поиск оптимальной точки разделения
            split_at = Config._find_split_point(response)
            parts.append(response[:split_at].strip())
            response = response[split_at:].lstrip()
        return parts

    @staticmethod
    def _find_split_point(text: str) -> int:
        """Находит оптимальную точку для разделения текста."""
        search_end = min(len(text), Config.MAX_RESPONSE_LENGTH)
        split_points = [
            text.rfind('\n', 0, search_end),
            text.rfind('. ', 0, search_end),
            text.rfind(' ', 0, search_end),
            Config.MAX_RESPONSE_LENGTH
        ]
        return max(p for p in split_points if p != -1)

    @classmethod
    def check_config(cls) -> None:
        """Проверяет корректность конфигурации."""
        logger.info("Проверка конфигурации...")
        
        # Исправлено: проверка API_KEY вместо AI_API_KEY
        missing = [var for var in ["TELEGRAM_TOKEN", "API_KEY"] if not getattr(cls, var)]
        if missing:
            error_msg = f"Отсутствуют переменные: {', '.join(missing)}"
            errorcake("missing_env_variables", error_message=error_msg)
            raise ValueError(error_msg)

        # Валидация URL
        if not all(urlparse(cls.API_URL)[:2]):
            error_msg = f"Некорректный URL: {cls.API_URL}"
            errorcake("invalid_api_url", error_message=error_msg)
            raise ValueError(error_msg)

        # Проверка таймаутов
        for timeout in [cls.TIMEOUT, cls.SHORT_TIMEOUT]:
            if timeout <= 0:
                error_msg = "Таймаут должен быть > 0"
                errorcake("invalid_timeout", error_message=error_msg)
                raise ValueError(error_msg)

        logger.info("Конфигурация проверена успешно")

# Автоматическая проверка при импорте
Config.check_config()