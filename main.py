import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from src.handlers import start, help_command, handle_photo, handle_message

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logging.error(msg="Exception while handling an update:", exc_info=context.error)

def main():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        print("Erro: TELEGRAM_TOKEN não encontrado no arquivo .env")
        return

    app = ApplicationBuilder().token(token).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ajuda", help_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Error Handler
    app.add_error_handler(error_handler)

    print("Bot iniciado...")
    # poll_interval=2.0 reduz a frequência de requisições ao Telegram (GET)
    app.run_polling(poll_interval=2.0)

if __name__ == '__main__':
    main()
