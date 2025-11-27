import os
import uuid
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
from src.ai_service import analyze_image

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("📸 Dicas de Foto"), KeyboardButton("ℹ️ Sobre o TCC")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "Olá! Sou o Bot de Patologias (TCC).\n"
        "Envie uma foto para análise ou use o menu abaixo.",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "**Dicas para melhor análise:**\n"
        "1. Boa iluminação.\n"
        "2. Foco nítido na patologia.\n"
        "3. Use um objeto (moeda/caneta) para escala."
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "**Sobre o Projeto:**\n"
        "Este bot faz parte de um TCC de Engenharia Civil.\n"
        "Objetivo: Uso de IA para identificação preliminar de patologias construtivas.\n"
        "Baseado nas normas NBR 9575, 15575 e 13752."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📸 Dicas de Foto":
        await help_command(update, context)
    elif text == "ℹ️ Sobre o TCC":
        await about_command(update, context)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    
    await update.message.reply_text("Recebi! Analisando...")
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    
    try:
        # Download da imagem
        file_path = f"temp_{uuid.uuid4()}.jpg"
        await photo_file.download_to_drive(file_path)
        
        # Chamada ao serviço de IA
        analysis_result = await analyze_image(file_path)
        
        # Enviar resultado
        await update.message.reply_text(analysis_result, parse_mode='Markdown')
        
        # Limpeza (opcional, mas boa prática)
        if os.path.exists(file_path):
            os.remove(file_path)
            
    except Exception as e:
        await update.message.reply_text(f"Ocorreu um erro ao processar a imagem: {e}")
