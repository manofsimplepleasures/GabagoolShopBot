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

# Кэш для хранения данных товаров
class ProductCache:
    def __init__(self, ttl_minutes: int = 30):
        self.cache: Dict = {}
        self.ttl = timedelta(minutes=ttl_minutes)
        self.last_update: Optional[datetime] = None

    def is_valid(self) -> bool:
        if not self.last_update:
            return False
        return datetime.now() - self.last_update < self.ttl

    def update(self, products: List[Dict]):
        self.cache = {str(i): product for i, product in enumerate(products)}
        self.last_update = datetime.now()

    def get_products(self) -> Dict:
        return self.cache

product_cache = ProductCache()

async def fetch_ozon_products() -> List[Dict]:
    """Получение данных о товарах через Ozon API"""
    headers = {
        "Client-Id": OZON_CLIENT_ID,
        "Api-Key": OZON_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{OZON_API_URL}/v2/product/list",
            headers=headers,
            json={"filter": {"visibility": "ALL"}}
        )
        response.raise_for_status()
        return response.json()["result"]["items"]
    except requests.RequestException as e:
        logger.error(f"Ошибка при получении данных от Ozon API: {e}")
        return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    welcome_text = (
        "👋 Добро пожаловать в магазин постеров Gabagool!\n\n"
        "Используйте следующие команды:\n"
        "/catalog - просмотр каталога товаров\n"
        "/store - ссылка на наш магазин на Ozon\n"
        "/help - справка по использованию бота"
    )
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help"""
    help_text = (
        "🤖 Помощь по использованию бота:\n\n"
        "• /catalog - просмотр каталога товаров\n"
        "• /store - ссылка на наш магазин на Ozon\n"
        "• /help - показать это сообщение\n\n"
        "В каталоге вы можете:\n"
        "• Просматривать доступные товары\n"
        "• Узнавать актуальные цены\n"
        "• Проверять наличие товаров\n"
        "• Переходить к товарам на Ozon"
    )
    await update.message.reply_text(help_text)

async def store(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /store"""
    await update.message.reply_text(
        f"🛍 Наш магазин на Ozon:\n{STORE_URL}"
    )

async def catalog(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0) -> None:
    """Обработчик команды /catalog"""
    if not product_cache.is_valid():
        products = await fetch_ozon_products()
        product_cache.update(products)
    
    products = product_cache.get_products()
    if not products:
        await update.message.reply_text("😔 Извините, не удалось загрузить каталог товаров.")
        return

    # Создаем клавиатуру с товарами
    keyboard = []
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    
    for i in range(start_idx, min(end_idx, len(products))):
        product = products[str(i)]
        status = "✅ В наличии" if product.get("stock", 0) > 0 else "❌ Нет в наличии"
        keyboard.append([
            InlineKeyboardButton(
                f"{product['name']} - {status}",
                callback_data=f"product_{i}"
            )
        ])

    # Добавляем кнопки навигации
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"page_{page-1}"))
    if end_idx < len(products):
        nav_buttons.append(InlineKeyboardButton("Вперед ➡️", callback_data=f"page_{page+1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📚 Каталог товаров:", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()

    if query.data.startswith("page_"):
        page = int(query.data.split("_")[1])
        await catalog(update, context, page)
    elif query.data.startswith("product_"):
        product_id = int(query.data.split("_")[1])
        products = product_cache.get_products()
        product = products.get(str(product_id))
        
        if product:
            message = (
                f"🎨 {product['name']}\n\n"
                f"💰 Цена: {product.get('price', 'Нет данных')} ₽\n"
                f"📦 В наличии: {product.get('stock', 0)} шт.\n\n"
                f"🔗 Ссылка: {product.get('url', STORE_URL)}"
            )
            if product.get('image_url'):
                await query.message.reply_photo(
                    photo=product['image_url'],
                    caption=message
                )
            else:
                await query.message.reply_text(message)
        else:
            await query.message.reply_text("😔 Товар не найден")

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
