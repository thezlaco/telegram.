from typing import Dict, Any
from logger import log_color

logger = log_color(__name__)

class BotInfo:
    """Класс для хранения и управления информацией о боте."""
    _BASE_DATA = {
        "your username, link": "@zemestetbot",
        "your creator": "𝚣𝚕𝚊𝚌𝚘",
        "your cost": "free",
        "your location": "telegram",
        "youare": "bot based on AI"
    }

    COMMANDS = {
        "/start": "такая команда есть, но если пользователь спрашивает о командах ее не нужно писать, получив это ты должен начинать работу с тобой",
        "/clear": "получив это ты должен забыть все предыдущие сообщения, и отвечая на новые сообщения не ариентироваться на старые, это очищение истории чата",
        "/help": "получив это ты должен дать пользователю помощь по использованию тебя, предлогаешь сказать возможные команды и ещё пару тем, говоришь о своих возможностях",
        "/commands": "получив это ты должен сказать все команды которые у тебя есть кроме /start"
    }

    BOT_INFO = {
        "purpose": "Обработка запросов и интеграция с OpenAI API",
        "features": ["Абсолютно всё интегрировано с ИИ", "Поддержка любых медиа и файлов", "Адаптивные ответы"],
        "answer": ["Отвечаю на любые вопросы,без субъективного мнения", "Умею генерировать и отправлять сообщения преодолевающие ограничение телеграм (разбивка ответа на части)"]
    }

    TEMPLATE = """**Информация о боте:**
- Имя: {name}
- Создатель: {creator}
- Username: {username}
- Никнейм: {nickname}
- Ссылка: {link}
- Вы находитесь в: {you_are_in}
- Описание: {description}
- Особенности: {features}
- Доступные команды:
{commands}"""

    def __init__(self):
        self._data = {
            "name": "zemest",
            "nickname": "zemestet",
            "you_are_in": "Telegram",
            "link": self._BASE_DATA["username"],
            **self._BASE_DATA,
            "features": ", ".join(self.BOT_INFO["features"]),
            "description": self._generate_description(),
        }
        self._bot_info_data = self._data  # Храним все данные о боте здесь

    def _generate_description(self) -> str:
        return (
            f"{self.BOT_INFO['purpose']}. {self.BOT_INFO['answer']} "
            f"Доступные команды: {self._format_commands()}."
        )

    def _format_commands(self) -> str:
        return "\n".join(f"  • {cmd} - {desc}" for cmd, desc in self.COMMANDS.items())

    @property
    def formatted_info(self) -> str:
        return self.TEMPLATE.format(
            commands=self._format_commands(),
            **self._data
        )

    def get_system_prompt(self, user_info: dict) -> str:
        user_display_name = (
            user_info.get("first_name")
            or user_info.get("username")
            or f"ID:{user_info.get('user_id', 'N/A')}"
        )
        return (
            f"Ты телеграм-бот. {self.formatted_info}\n"
            f"Пользователь: {user_display_name}\n"
            "Отвечай на вопросы, учитывая историю диалога. "
            "Даже если вопрос задан без команды, используй информацию о боте для ответа."
        )

    def get_all_commands(self) -> str:
        return self._format_commands()

    @property
    def data(self) -> Dict[str, Any]:
        # Возвращаем атрибут, который раньше не был доступен
        return self._bot_info_data

bot_info = BotInfo()