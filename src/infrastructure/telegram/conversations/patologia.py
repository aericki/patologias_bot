import logging
import os
import uuid

from telegram import Update
from telegram.ext import (
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from src.services.ai_service import GeminiService
from src.infrastructure.telegram.formatters import send_ai_response, send_typing

logger = logging.getLogger(__name__)

AWAITING_PHOTO = 0


async def _entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.effective_message
    if message is None:
        return ConversationHandler.END

    await message.reply_text(
        "Envie a foto da vistoria (trinca, fissura, infiltração) "
        "que eu te oriento no diagnóstico e na composição do laudo."
    )
    return AWAITING_PHOTO


async def _handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.effective_message
    telegram_message = update.message
    if message is None or telegram_message is None or not telegram_message.photo:
        return ConversationHandler.END

    photo_file = await telegram_message.photo[-1].get_file()
    await message.reply_text("Recebi! Analisando...")
    await send_typing(update, context)

    file_path = f"temp_{uuid.uuid4()}.jpg"
    try:
        await photo_file.download_to_drive(file_path)
        ai: GeminiService = context.bot_data["ai_service"]
        result = await ai.analyze_image(file_path)
        await send_ai_response(message, result)
    except Exception as e:
        logger.exception("Erro ao processar imagem")
        await message.reply_text(f"Ocorreu um erro ao processar a imagem: {e}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

    return ConversationHandler.END


def create_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^📸 Analisar Patologia$"), _entry),
        ],
        states={
            AWAITING_PHOTO: [
                MessageHandler(filters.PHOTO, _handle_photo),
            ],
        },
        fallbacks=[
            MessageHandler(filters.PHOTO & ~filters.COMMAND, _handle_photo),
        ],
        name="patologia",
        allow_reentry=True,
    )
