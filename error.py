import logging
from typing import Optional, Dict, Any, ClassVar
from dataclasses import dataclass
from telegram.error import NetworkError
from telegram import Update
import asyncio
import traceback

# Настройка логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

@dataclass(frozen=True)
class ErrorDetails:
    """Контейнер для деталей об ошибке"""
    level: int
    description: str
    notify_admin: bool = False

class errorcake:
    """Класс для обработки и логирования ошибок"""
    
    ERROR_REGISTRY: ClassVar[Dict[str, ErrorDetails]] = {
        # Информационные события
        "apiresponse": ErrorDetails(logging.INFO, "Ответ от API"),
        
        # Предупреждения
        "userinfo": ErrorDetails(logging.WARNING, "Ошибка при получении информации о пользователе"),
        "openaireply": ErrorDetails(logging.WARNING, "Пустой ответ OpenAI API"),
        "missinguserinfo": ErrorDetails(logging.WARNING, "Отсутствуют данные пользователя"),
        "emptymessage": ErrorDetails(logging.WARNING, "Пустое сообщение"),
        
        # Ошибки
        "commandprocessing": ErrorDetails(logging.ERROR, "Ошибка обработки команды", True),
        "apierror": ErrorDetails(logging.ERROR, "Ошибка API: некорректный запрос", True),
        "timeout": ErrorDetails(logging.ERROR, "Таймаут запроса к API", True),
        "spliterror": ErrorDetails(logging.ERROR, "Ошибка разделения ответа", True),
        "externalapi": ErrorDetails(logging.ERROR, "Ошибка запроса к внешнему API", True),
        "openairequest": ErrorDetails(logging.ERROR, "Ошибка запроса к OpenAI API", True),
        "starterror": ErrorDetails(logging.ERROR, "Ошибка обработки /start", True),
        "messageerror": ErrorDetails(logging.ERROR, "Ошибка обработки сообщения", True),
        "usernameerror": ErrorDetails(logging.ERROR, "Ошибка получения юзернейма", True),
        "configerror": ErrorDetails(logging.ERROR, "Ошибка конфигурации", True),
        "updateerror": ErrorDetails(logging.ERROR, "Ошибка получения обновлений", True),
        "senderror": ErrorDetails(logging.ERROR, "Ошибка отправки сообщения", True),
        "airesponse": ErrorDetails(logging.ERROR, "Ошибка запроса к ИИ API", True),
        "handlemessage": ErrorDetails(logging.ERROR, "Ошибка обработки сообщений", True),
        "jsonformat": ErrorDetails(logging.ERROR, "Неожиданный JSON формат", True),
        "htmlresponse": ErrorDetails(logging.ERROR, "Неожиданный HTML ответ", True),
        "responseformat": ErrorDetails(logging.ERROR, "Неожиданный формат ответа", True),
        "openaireqerror": ErrorDetails(logging.ERROR, "Ошибка запроса OpenAI", True),
        "htmlreceived": ErrorDetails(logging.ERROR, "HTML ответ от API", True),
        "openairesponse": ErrorDetails(logging.ERROR, "Ошибка ответа OpenAI", True),
        "unexpectedresponse": ErrorDetails(logging.ERROR, "Неожиданный формат ответа", True),
        "invalidjson": ErrorDetails(logging.ERROR, "Неожиданный JSON", True),
        "networkerror": ErrorDetails(logging.ERROR, "Сетевая/API ошибка", True),
        "unknownerror": ErrorDetails(logging.ERROR, "Неизвестная ошибка", True),
        "commanderror": ErrorDetails(logging.ERROR, "Ошибка обработки команды", True),
        "userdataerror": ErrorDetails(logging.ERROR, "Ошибка получения данных пользователя", True),
        "logerror": ErrorDetails(logging.ERROR, "Ошибка логирования данных", True),
        "processmessage": ErrorDetails(logging.ERROR, "Ошибка обработки сообщения", True),
        "updateprocess": ErrorDetails(logging.ERROR, "Ошибка обработки update", True),
        "invalidurl": ErrorDetails(logging.ERROR, "Некорректный URL API", True),
        
        # Критические ошибки
        "notokens": ErrorDetails(logging.CRITICAL, "Отсутствуют токены", True),
        "envvariables": ErrorDetails(logging.CRITICAL, "Не заданы переменные окружения", True),
        "criticalerror": ErrorDetails(logging.CRITICAL, "Критическая ошибка запуска бота", True),
    }
    
    @classmethod
    def _get_user_info(cls, update: Optional[Update]) -> str:
        """Извлекает информацию о пользователе из Update"""
        try:
            if update and update.effective_user:
                user = update.effective_user
                return (
                    f"{user.id} (@{user.username})" 
                    if user.username else str(user.id)
                )
            return "N/A"
        except Exception as e:
            logger.warning(f"Ошибка получения информации о пользователе: {e}")
            return "N/A"
    
    @classmethod
    def handle_error(
        cls,
        error_type: str,
        exception: Optional[Exception] = None,
        update: Optional[Update] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Универсальный обработчик ошибок
        
        Args:
            error_type: Ключ ошибки из ERROR_REGISTRY
            exception: Объект исключения (опционально)
            update: Объект Update Telegram (опционально)
            context: Дополнительный контекст для лога
        """
        try:
            details = cls.ERROR_REGISTRY.get(
                error_type,
                ErrorDetails(logging.ERROR, "Неизвестная ошибка", True)
            )
            user_info = cls._get_user_info(update)
            context_info = f" | Context: {context}" if context else ""
            exception_info = f" | Exception: {repr(exception)}" if exception else ""
            traceback_info = ""
            if exception and details.level >= logging.ERROR:
                traceback_info = (
                    f"\nTraceback:\n{''.join(traceback.format_exception(exception))}"
                )
            log_message = (
                f"[{error_type}] {details.description} | "
                f"User: {user_info}"
                f"{context_info}"
                f"{exception_info}"
                f"{traceback_info}"
            )
            logger.log(
                details.level,
                log_message,
                extra={'notify_admin': details.notify_admin}
            )
            if details.level == logging.CRITICAL:
                logger.critical("ТРЕБУЕТСЯ НЕМЕДЛЕННОЕ ВМЕШАТЕЛЬСТВО!")
        except Exception as inner_exc:
            logger.critical(
                f"Ошибка в обработчике ошибок: {inner_exc}",
                exc_info=True
            )

    @classmethod
    async def safe_request(cls, update: Optional[Update] = None, context: Optional[Dict[str, Any]] = None):
        """
        Асинхронная функция для безопасного выполнения запросов с повторными попытками.

        Args:
            update: Объект Update Telegram (опционально)
            context: Дополнительный контекст для лога
        """
        while True:
            try:
                # Здесь код запроса к Telegram API
                print("Отправка запроса к Telegram API...")
                # Если запрос выполнен успешно, выходим из цикла
                break
            except NetworkError as e:
                cls.handle_error(
                    error_type="networkerror",
                    exception=e,
                    update=update,
                    context=context
                )
                print(f"Ошибка сети: {e}, повтор через 0.5 секунды...")
                await asyncio.sleep(0.5)  # Ждем 0.5 секунды перед повтором

# Пример использования
if __name__ == "__main__":
    async def main():
        try:
            await errorcake.safe_request(
                context={
                    "endpoint": "api.example.com",
                    "params": {"user_id": 123},
                    "source": "main_module"
                }
            )
        except Exception as e:
            errorcake.handle_error(
                error_type="criticalerror",
                exception=e,
                context={
                    "endpoint": "api.example.com",
                    "params": {"user_id": 123},
                    "source": "main_module"
                }
            )

    asyncio.run(main())