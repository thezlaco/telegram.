import logging
import sys
from config import Config
from error import errorcake
from logger import log_color

def logstart():
    logger = log_color(__name__)

    try:
        logger.info("Проверка конфигурации...")
        Config.check_config()
        logger.info("Конфигурация проверена. Все переменные окружения заданы.")
    except Exception as e:
        handle_config_error(e)
        sys.exit(1)

    return logger

def setup_bot(application, logger):
    logger.info("Настройка обработчиков...")
    from openai1 import register_handlers

    try:
        register_handlers(application)
        logger.info("Все сообщения теперь обрабатываются через ИИ")
    except Exception as e:
        handle_unknown_error(e)