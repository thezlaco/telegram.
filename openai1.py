from telegram import Update
from telegram.ext import MessageHandler, filters, CallbackContext, Application, CommandHandler
import aiohttp
import asyncio
from config import Config
from error import errorcake
from botinfo import bot_info
from info import get_user_info
from openinfo import get_full_info
from logger import log_color

logger = log_color(__name__)

class RequestManager:
    """Менеджер для отслеживания активных запросов пользователей."""
    def __init__(self):
        self.active_tasks = {}
        self.lock = asyncio.Lock()

    async def add_task(self, user_id: int) -> asyncio.Event:
        async with self.lock:
            self.active_tasks[user_id] = asyncio.Event()
            return self.active_tasks[user_id]

    async def remove_task(self, user_id: int) -> None:
        async with self.lock:
            if user_id in self.active_tasks:
                self.active_tasks[user_id].set()
                del self.active_tasks[user_id]

    async def is_processing(self, user_id: int) -> bool:
        async with self.lock:
            return user_id in self.active_tasks

request_manager = RequestManager()

async def generate_ai_response(messages: list, user_info: dict = None) -> str:
    """Генерирует ответ через OpenAI API с учетом контекста."""
    try:
        if not messages:
            system_prompt = bot_info.get_system_prompt(user_info or {"user_id": "new_user"})
            messages = [{"role": "system", "content": system_prompt}]
        async with aiohttp.ClientSession(
            timeout=Config.get_timeout(),
            headers={
                "Authorization": f"Bearer {Config.API_KEY}",
                "Content-Type": "application/json"
            }
        ) as session:
            async with session.post(
                Config.API_URL,
                json=Config.get_ai_request_data(messages)
            ) as response:
                if response.status != 200:
                    error_body = await response.text()
                    errorcake.handle_error("apierror", exception=None, context={"status": response.status, "response": error_body})
                    return None
                result = await response.json()
                return result["choices"][0]["message"]["content"] if result.get("choices") else None
    except Exception as e:
        errorcake.handle_error("openairequest", exception=e)
        return None

async def _process_request(user_input: str, context: CallbackContext, update: Update, is_command: bool = False, done_event: asyncio.Event = None) -> None:
    """Универсальная обработка запросов через ИИ."""
    user = update.effective_user
    try:
        full_info = get_full_info(update)
        messages = context.user_data.get("message_history", [])

        # Обновляем системный промпт с актуальной информацией
        system_prompt = bot_info.get_system_prompt(get_user_info(update))
        messages = [msg for msg in messages if msg["role"] != "system"]
        messages.insert(0, {"role": "system", "content": system_prompt})

        # Добавляем пользовательский ввод с контекстом
        user_message = f"{user_input}\n\nКонтекст:\n{full_info}"
        messages.append({"role": "user", "content": user_message})

        response = await generate_ai_response(messages, get_user_info(update))
        if not response:
            errorcake.handle_error("airesponse", exception=None, update=update)
            return

        # Обновляем историю и отправляем ответ
        context.user_data["message_history"] = messages[-9:] + [
            {"role": "assistant", "content": response}
        ]
        for chunk in Config.split_response(response):
            await update.message.reply_text(chunk)

        if done_event:
            done_event.set()
    except Exception as e:
        logger.error(f"Ошибка обработки: {str(e)}")
        await update.message.reply_text((await generate_ai_response(
            [{"role": "system", "content": "Сгенерируй сообщение об ошибке обработки запроса"}],
            get_user_info(user)
        )) or "Произошла ошибка")

async def _monitor_progress(user_id: int, update: Update, done_event: asyncio.Event) -> None:
    """Отправляет статус обработки через ИИ."""
    try:
        await asyncio.sleep(5)
        while not done_event.is_set():
            status_prompt = [{"role": "system", "content": "Сгенерируй креативное сообщение о задержке обработки"}]
            status_msg = await generate_ai_response(status_prompt) or "Операция выполняется..."
            await update.message.reply_text(status_msg)
            await asyncio.sleep(15)
    except Exception as e:
        logger.debug(f"Мониторинг прерван: {str(e)}")

async def handle_message(update: Update, context: CallbackContext) -> None:
    """Обработчик текстовых сообщений."""
    user = update.effective_user
    user_input = update.message.text.strip()
    
    if await request_manager.is_processing(user.id):
        status_prompt = [{"role": "system", "content": "Пользователь повторно отправил запрос. Вежливо сообщи о процессе обработки"}]
        await update.message.reply_text(await generate_ai_response(status_prompt) or "Ваш запрос в процессе обработки...")
        return

    done_event = await request_manager.add_task(user.id)
    try:
        await asyncio.gather(
            _process_request(user_input, context, update, done_event=done_event),
            _monitor_progress(user.id, update, done_event)
        )
    finally:
        await request_manager.remove_task(user.id)

async def handle_command_response(command: str, update: Update, context: CallbackContext) -> None:
    """Генерирует ответ на команду через ИИ."""
    user = update.effective_user
    try:
        system_prompt = f"""
        Пользователь ввел команду: {command}
        Информация о доступных командах:
        {bot_info.get_all_commands()}
        
        Сгенерируй подходящий ответ используя информацию о боте. 
        Для служебных команд (/start, /clear и т.д.) выполни требуемое действие.
        """
        
        response = await generate_ai_response([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": command}
        ])
        
        if response:
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("Не удалось обработать команду")
    except Exception as e:
        errorcake.handle_error("handlemessage", exception=e, update=update)
        logger.error(f"Ошибка обработки команды {command}: {str(e)}")

async def commands_list(update: Update, context: CallbackContext) -> None:
    """Обработчик для команды /commands."""
    commands = "\n".join([f"{cmd} - {desc}" for cmd, desc in bot_info.COMMANDS.items()])
    await update.message.reply_text(f"Доступные команды:\n{commands}")
    logger.debug(f"Список команд отправлен {update.effective_user.id}")

async def handle_command(update: Update, context: CallbackContext) -> None:
    """Обработчик команд через ИИ."""
    user = update.effective_user
    command = update.message.text.strip().lower()
    
    if await request_manager.is_processing(user.id):
        await update.message.reply_text("Ваш запрос уже в обработке...")
        return
    
    done_event = await request_manager.add_task(user.id)
    try:
        if command == "/commands":
            await commands_list(update, context)
        else:
            await handle_command_response(command, update, context)
    except Exception as e:
        errorcake.handle_error("commandprocessing", exception=e, update=update)
    finally:
        await request_manager.remove_task(user.id)

def register_handlers(application: Application) -> None:
    """Регистрация обработчиков с улучшенной логикой."""
    for cmd in bot_info.COMMANDS:
        application.add_handler(CommandHandler(cmd.strip('/'), handle_command))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Система обработки запросов активирована")