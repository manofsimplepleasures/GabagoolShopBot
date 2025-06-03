GabagoolBot - Telegram-бот для магазина постеров на Ozon

GabagoolBot - это Telegram-бот для магазина постеров на маркетплейсе Ozon, разработанный на Python. Бот интегрируется с Ozon Seller API для отображения актуальной информации о наличии товаров, ценах и изображениях, а также позволяет просматривать каталог и переходить в магазин на Ozon.

Возможности
Каталог товаров: Просмотр доступных постеров с информацией о наличии через команду /catalog.
Детали товара: Отображение названия, цены, остатка, изображения и ссылки на Ozon для каждого постера.
Ссылка на магазин: Переход в магазин Ozon через команду /store.
Обработка ошибок: Корректная обработка ошибок API и сетевых сбоев.
Кэширование: Снижение нагрузки на API Ozon за счет кэширования данных в памяти.

Технологии
Python: Основной язык программирования.
python-telegram-bot: Для работы с Telegram Bot API.
requests: Для интеграции с Ozon Seller API.
python-dotenv: Для безопасного управления переменными окружения.

Установка
Клонируйте репозиторий:

git clone https://github.com/yourusername/GabagoolBot.git
cd GabagoolBot

Создайте виртуальное окружение:
python -m venv venv
source venv/bin/activate  # Для Windows: venv\Scripts\activate

Установите зависимости:
pip install -r requirements.txt

Настройте переменные окружения: Создайте файл .env в корне проекта:
TELEGRAM_TOKEN=ваш_токен_бота
OZON_CLIENT_ID=ваш_client_id
OZON_API_KEY=ваш_api_key

Запустите бота:
python main.py

Деплой
Для деплоя бота на Heroku:
Установите Heroku CLI и авторизуйтесь.

Создайте файл Procfile:
web: python main.py

Выполните деплой:
heroku create gabagool-bot
heroku config:set TELEGRAM_TOKEN=ваш_токен OZON_CLIENT_ID=ваш_id OZON_API_KEY=ваш_ключ
git push heroku main
heroku ps:scale web=1

Использование
/start: Приветственное сообщение с инструкциями.
/catalog: Просмотр каталога постеров с инлайн-кнопками.
/store: Ссылка на магазин Ozon.
/help: Список доступных команд.

Возможные улучшения
Добавить пагинацию для больших каталогов.
Реализовать сбор данных о заказах в Telegram с уведомлениями для администратора.
Использовать SQLite или Redis для постоянного кэширования.

Лицензия
MIT License

Проект создан как демонстрация навыков работы с Python, интеграции с API и разработки Telegram-ботов для портфолио.
