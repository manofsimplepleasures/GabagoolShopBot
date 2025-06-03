import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OZON_CLIENT_ID = os.getenv('OZON_CLIENT_ID')
OZON_API_KEY = os.getenv('OZON_API_KEY')

# Проверка наличия необходимых переменных окружения
if not all([TELEGRAM_TOKEN, OZON_CLIENT_ID, OZON_API_KEY]):
    logger.error("Отсутствуют необходимые переменные окружения")
    raise ValueError("Необходимо установить TELEGRAM_TOKEN, OZON_CLIENT_ID и OZON_API_KEY")

# Константы
OZON_API_URL = "https://api-seller.ozon.ru"
STORE_URL = "https://www.ozon.ru/seller/gabagool"
ITEMS_PER_PAGE = 5
PORT = int(os.getenv('PORT', 10000))

# ... existing code ...

def main() -> None:
    """Запуск бота"""
    try:
        application = Application.builder().token(TELEGRAM_TOKEN).build()

        # Регистрация обработчиков команд
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("store", store))
        application.add_handler(CommandHandler("catalog", catalog))
        
        # Регистрация обработчика кнопок
        application.add_handler(CallbackQueryHandler(button_callback))

        # Запуск бота
        if os.getenv('RENDER'):  # Проверка, запущен ли код на Render
            application.run_webhook(
                listen='0.0.0.0',
                port=PORT,
                url_path=TELEGRAM_TOKEN,
                webhook_url=f'https://gabagoolshopbot.onrender.com/{TELEGRAM_TOKEN}'
            )
        else:
            application.run_polling()

    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        raise

if __name__ == '__main__':
    main()
