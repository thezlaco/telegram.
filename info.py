from telegram import Update
from error import errorcake

def get_user_info(update: Update) -> dict:
    """
    Извлекает информацию о пользователе из объекта update.

    :param update: Объект Update из Telegram API.
    :return: Словарь с информацией о пользователе или пустой словарь в случае ошибки.
    """
    try:
        # Проверка на наличие необходимых данных
        if not update or not update.effective_user:
            errorcake("missing_user_info", update=update)
            return {}

        user = update.effective_user
        message = update.effective_message

        # Основное имя: сначала first_name, затем username, потом ID
        main_name = user.first_name or user.username or f"ID:{user.id}"

        # Формируем информацию о пользователе
        user_info = {
            "username": main_name,  # Приоритет: имя > юзернейм > ID
            "nickname": user.username or "N/A",  # Nickname (username или N/A, если отсутствует)
            "user_id": user.id,  # ID пользователя
            "first_name": user.first_name or "N/A",  # Имя или N/A, если отсутствует
            "last_name": user.last_name or "N/A",  # Фамилия или N/A, если отсутствует
            "language_code": user.language_code or "N/A",  # Код языка или N/A, если отсутствует
            "message_text": message.text if message else "N/A",  # Текст сообщения или N/A, если отсутствует
            "full_name": f"{user.first_name or ''} {user.last_name or ''}".strip() or "N/A",  # Полное имя или N/A, если отсутствует
        }

        return user_info

    except Exception as e:
        errorcake("get_user_info_error", exception=e, update=update)
        return {}

def get_user_info_text(user_info: dict) -> str:
    """
    Возвращает заранее сформированную строку с информацией о пользователе.

    :param user_info: Словарь с информацией о пользователе.
    :return: Строка с информацией о пользователе.
    """
    if not user_info:
        return "Информация о пользователе отсутствует."

    user_info_text = (
        f"Информация о пользователе:\n"
        f"Username: {user_info.get('username', 'N/A')}\n"
        f"Nickname: {user_info.get('nickname', 'N/A')}\n"
        f"Имя: {user_info.get('first_name', 'N/A')}\n"
        f"Фамилия: {user_info.get('last_name', 'N/A')}\n"
        f"Полное имя: {user_info.get('full_name', 'N/A')}\n"
        f"Язык: {user_info.get('language_code', 'N/A')}\n"
        f"Сообщение: {user_info.get('message_text', 'N/A')}\n"
    )
    return user_info_text