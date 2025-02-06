from telegram.ext import Application
from config import Config
from start import logstart, setup_bot
import sys
from error import errorcake

def main():
    # Инициализация логирования и проверка конфигурации
    logger = logstart()

    try:
        # Инициализация приложения с увеличенным тайм-аутом
        logger.info("Инициализация приложения...")
        application = Application.builder().token(Config.TELEGRAM_TOKEN).read_timeout(60).write_timeout(60).build()

        # Настройка бота
        setup_bot(application, logger)

        # Запуск бота
        logger.info("Запуск бота...")
        print("Бот запущен и ожидает сообщений...")
        application.run_polling()

    except Exception as e:
        # Логирование критических ошибок через errorcake
        errorcake("main_error", exception=e)
        sys.exit(1)  # Завершение программы с кодом ошибки

if __name__ == '__main__':
    main()