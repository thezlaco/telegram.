from typing import Dict, Any
import logging
import colorlog
from error import errorcake
from info import get_user_info, get_user_info_text

# Настройка цветного логгера
def log_color(name: str) -> logging.Logger:
    """
    Настраивает и возвращает логгер с цветным выводом.

    :param name: Имя логгера (обычно __name__).
    :return: Настроенный логгер.
    """
    # Создаем обработчик с цветным форматтером
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    ))

    # Создаем логгер и добавляем обработчик
    logger = colorlog.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Изменено с INFO на DEBUG
    logger.addHandler(handler)

    return logger

# Настройка логгера
logger = log_color(__name__)

def log_user_info(user_info: Dict[str, Any]) -> None:
    """
    Логирует информацию о пользователе.

    :param user_info: Словарь с информацией о пользователе, содержащий:
        - username: Юзернейм пользователя.
        - user_id: ID пользователя.
        - message_text: Текст сообщения пользователя.
    """
    try:
        # Используем get_user_info_text для логирования информации о пользователе
        user_info_text = get_user_info_text(user_info)
        logger.debug(  # Изменено с .info на .debug
            "Информация о пользователе:\n"
            "Username: %s\n"
            "User ID: %s\n"
            "Текст сообщения: %s",
            user_info.get('username', 'N/A'),
            user_info.get('user_id', 'N/A'),
            user_info.get('message_text', 'N/A')
        )
    except Exception as e:
        # Логируем ошибку через handle_log_user_info_error
        handle_log_user_info_error(e)

def process_user_message(message_text: str) -> None:
    """
    Обрабатывает текст сообщения пользователя.

    :param message_text: Текст сообщения пользователя.
    """
    try:
        # Проверка на пустое сообщение
        if not message_text:
            raise ValueError("Пустое сообщение")

        # Логируем обработку сообщения
        logger.debug("Обработка сообщения:\nТекст сообщения: %s", message_text)  # Изменено с .info на .debug

        # Здесь можно добавить дополнительную логику обработки сообщения

    except Exception as e:
        # Логируем ошибку через handle_process_user_message_error
        handle_process_user_message_error(e)

def process_update(update: Dict[str, Any]) -> None:
    """
    Обрабатывает объект update, извлекает информацию о пользователе и логирует её.

    :param update: Словарь с информацией о сообщении пользователя.
    """
    try:
        # Извлекаем информацию о пользователе с помощью get_user_info
        user_info = get_user_info(update)

        # Логируем информацию о пользователе
        log_user_info(user_info)

        # Обрабатываем сообщение пользователя
        process_user_message(user_info["message_text"])

    except Exception as e:
        # Логируем ошибку через handle_process_update_error
        handle_process_update_error(e, update)

# Пример использования
if __name__ == "__main__":
    # Пример объекта update (имитация сообщения от пользователя)
    example_update = {
        "message": {
            "from_user": {
                "username": "example_user",
                "id": 123456789
            },
            "text": "Привет, это тестовое сообщение!"
        }
    }

    # Обрабатываем пример update
    process_update(example_update)