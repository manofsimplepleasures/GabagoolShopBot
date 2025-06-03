# GabagoolBot - Telegram Bot for Ozon Poster Store

GabagoolBot is a Telegram bot for an Ozon-based poster store, built with Python. It integrates with the Ozon Seller API to display real-time product availability, images, and prices, and allows users to browse products and visit the Ozon store.

## Features

- **Product Catalog**: View available po sters with stock status using the `/catalog` command.
- **Product Details**: See detailed information (name, price, stock, image, Ozon link) for each poster.
- **Store Link**: Access the Ozon store via the `/store` command.
- **Error Handling**: Gracefully handles API errors and network issues.
- **Caching**: Reduces Ozon API calls with in-memory caching.

## Tech Stack

- **Python**: Core language.
- **python-telegram-bot**: For Telegram bot functionality.
- **requests**: For Ozon API integration.
- **python-dotenv**: For secure environment variable management.

## Setup

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/yourusername/GabagoolBot.git
   cd GabagoolBot
   ```
2. **Create a Virtual Environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```
4. **Set Up Environment Variables**: Create a `.env` file in the project root:

   ```env
   TELEGRAM_TOKEN=your_telegram_token
   OZON_CLIENT_ID=your_client_id
   OZON_API_KEY=your_api_key
   ```
5. **Run the Bot**:

   ```bash
   python main.py
   ```

## Deployment

To deploy the bot on Heroku:

1. Install Heroku CLI and log in.
2. Create a `Procfile`:

   ```text
   web: python main.py
   ```
3. Deploy:

   ```bash
   heroku create gabagool-bot
   heroku config:set TELEGRAM_TOKEN=your_token OZON_CLIENT_ID=your_id OZON_API_KEY=your_key
   git push heroku main
   heroku ps:scale web=1
   ```

## Usage

- `/start`: Welcome message with bot instructions.
- `/catalog`: Browse posters with inline buttons.
- `/store`: Link to the Ozon store.
- `/help`: List available commands.

## Future Improvements

- Add pagination for large catalogs.
- Implement order collection in Telegram with admin notifications.
- Use SQLite or Redis for persistent caching.

## License

MIT License

---

Built as a pet project to demonstrate Python, API integration, and bot development skills.
