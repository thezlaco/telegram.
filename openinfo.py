from typing import Dict, Any 
from logger import log_color 
from botinfo import bot_info 
from error import errorcake

logger = log_color(__name__)

def _format_user_info(user_info: Dict[str, Any]) -> str:
    """Форматирует информацию о пользователе."""
    fields = {
        'Имя': user_info.get('first_name', 'N/A'),
        'Username': f"@{user_info.get('username', 'N/A')}",
        'ID': user_info.get('user_id', 'N/A'),
        'Фамилия': user_info.get('last_name', 'N/A'),
        'Язык': user_info.get('language_code', 'N/A')
    }
    formatted_info = "\n".join([f"{key}: {value}" for key, value in fields.items()])
    logger.debug("Форматированная информация о пользователе:\n%s", formatted_info)  # Логирование
    return formatted_info

def get_full_info(update: Any) -> Dict[str, Any]:
    """Получает полную информацию о пользователе и боте."""
    result_template = {
        "user_info": {},
        "bot_info": bot_info.data,
        "error": None
    }

    try:
        from info import get_user_info
        user_data = get_user_info(update)
        result_template["user_info"] = _format_user_info(user_data)
        logger.debug("Данные пользователя получены: %s", user_data)  # Логирование

        result_template["bot_info"] = {
            "commands": "\n".join([f"{cmd} - {desc}" for cmd, desc in bot_info.COMMANDS.items()]),
            "description": bot_info.formatted_info
        }

        logger.info(
            "Полная информация о пользователе и боте:\n%s\n%s",
            f"Информация о пользователе:\n{result_template['user_info']}",
            f"Информация боту:\n{result_template['bot_info']['description']}"
        )

    except Exception as e:
        handle_get_user_info_error(e, update)
        result_template["error"] = str(e)
        logger.error(f"Ошибка: {str(e)}")

    return result_template

def get_bot_info_text() -> str:
    """Возвращает описание бота."""
    return bot_info.formatted_info