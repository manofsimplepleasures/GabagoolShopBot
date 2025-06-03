import os
import requests
import json
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OZON_CLIENT_ID = os.getenv("OZON_CLIENT_ID")
OZON_API_KEY = os.getenv("OZON_API_KEY")

# Базовый URL Ozon API
OZON_API_URL = "https://api-seller.ozon.ru"

# Простое кэширование данных товаров
PRODUCT_CACHE = {}
CACHE_DURATION = 3600  # Кэш на 1 час

def fetch_ozon_products():
    """
    Получение списка товаров с Ozon API с кэшированием.
    Возвращает список товаров или пустой список при ошибке.
    """
    global PRODUCT_CACHE
    current_time = time.time()
    
    # Проверка кэша
    if PRODUCT_CACHE.get("timestamp", 0) + CACHE_DURATION > current_time:
        return PRODUCT_CACHE.get("data", [])
    
    headers = {
        "Client-Id": OZON_CLIENT_ID,
        "Api-Key": OZON_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "filter": {"visibility": "ALL"},
        "page": 1,
        "page_size": 100
    }
    try:
        response = requests.post(f"{OZON_API_URL}/v2/product/info/list", json=payload, headers=headers)
        response.raise_for_status()
        products = response.json().get("result", [])
        # Обновление кэша
        PRODUCT_CACHE = {"data": products, "timestamp": current_time}
        return products
    except requests.RequestException as e:
        print(f"Ошибка при запросе к Ozon API: {e}")
        return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start. Отправляет приветственное сообщение."""
    await update.message.reply_text(
        "Добро пожаловать в Gabagool Poster Store! 🎨\n"
        "Используйте /catalog для просмотра постеров, /store для перехода в наш магазин или /help для справки."
    )

async def catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /catalog. Показывает список товаров с кнопками."""
    products = fetch_ozon_products()
    if not products:
        await update.message.reply_text("К сожалению, товары сейчас недоступны.")
        return

    keyboard = []
    for product in products:
        product_id = product.get("id")
        name = product.get("name", "Неизвестный постер")
        stock = product.get("stocks", {}).get("present", 0)
        status = "В наличии" if stock > 0 else "Нет в наличии"
        keyboard.append([InlineKeyboardButton(f"{name} ({status})", callback_data=f"product_{product_id}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите постер:", reply_markup=reply_markup)

async def product_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора товара. Показывает детали товара."""
    query = update.callback_query
    await query.answer()
    
    product_id = query.data.split("_")[1]
    headers = {
        "Client-Id": OZON_CLIENT_ID,
        "Api-Key": OZON_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {"product_id": [product_id]}
    
    try:
        response = requests.post(f"{OZON_API_URL}/v2/product/info", json=payload, headers=headers)
        response.raise_for_status()
        product = response.json().get("result", {})
        
        name = product.get("name", "Неизвестный постер")
        price = product.get("price", {}).get("price", "N/A")
        stock = product.get("stocks", {}).get("present", 0)
        image = product.get("images", [None])[0]
        ozon_link = product.get("web_url", "https://www.ozon.ru")
        
        message = f"**{name}**\nЦена: {price} ₽\nОстаток: {stock}\nСсылка: {ozon_link}"
        if image:
            await query.message.reply_photo(photo=image, caption=message)
        else:
            await query.message.reply_text(message)
    except requests.RequestException as e:
        await query.message.reply_text(f"Ошибка при получении данных о товаре: {e}")

async def store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /store. Отправляет ссылку на магазин."""
    await update.message.reply_text(
        "Посетите наш магазин на Ozon: https://www.ozon.ru/seller/gabagool",
        disable_web_page_preview=True
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help. Показывает справку."""
    await update.message.reply_text(
        "Доступные команды:\n"
        "/start - Запустить бота\n"
        "/catalog - Просмотреть каталог постеров\n"
        "/store - Перейти в наш магазин на Ozon\n"
        "/help - Показать эту справку"
    )

def main():
    """Основная функция для запуска бота."""
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("catalog", catalog))
    application.add_handler(CommandHandler("store", store))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(product_details, pattern="^product_"))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()