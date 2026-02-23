import logging

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from src.config import Settings
from src.services.ai_service import GeminiService
from src.infrastructure.telegram.keyboards import main_menu_markup
from src.infrastructure.telegram.error_handler import error_handler
from src.infrastructure.telegram.conversations import (
    patologia,
    regularizacao,
    apo,
)

logger = logging.getLogger(__name__)


# ── Comandos globais ────────────────────────────────────────

async def _start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if message is None:
        return

    await message.reply_text(
        "Olá, colega! Sou seu *Assistente Técnico de Engenharia Civil*. "
        "Fui feito para ajudar engenheiros e arquitetos recém-formados "
        "no dia a dia profissional.\n\n"
        "📸 *Patologias* — envie foto da vistoria para orientação de diagnóstico\n"
        "📋 *Regularização* — roteiro prático para conduzir legalização e aprovação\n"
        "🏢 *APO* — Avaliação Pós-Ocupação: visão do morador e do especialista (NBR 15575)\n\n"
        "Escolha uma opção abaixo:",
        reply_markup=main_menu_markup(),
        parse_mode="Markdown",
    )


async def _help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if message is None:
        return

    await message.reply_text(
        "*Dicas para fotos de vistoria:*\n"
        "1. Boa iluminação natural ou artificial direta.\n"
        "2. Foco nítido na patologia (evite zoom digital).\n"
        "3. Inclua escala métrica (trena, régua) — facilita o laudo.\n"
        "4. Fotografe também o entorno para contexto.\n"
        "5. Se possível, registre data/hora na foto.",
        parse_mode="Markdown",
    )


async def _about(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if message is None:
        return

    await message.reply_text(
        "📚 *Sobre o Projeto*\n\n"
        "Assistente técnico para *engenheiros e arquitetos* — protótipo "
        "acadêmico com IA (Gemini).\n\n"
        "🔬 *TCC — Patologias Construtivas*\n"
        "Apoio ao diagnóstico de campo: o profissional envia a foto da "
        "vistoria e recebe orientação técnica para compor seu laudo "
        "(NBR 9575, 15575, 13752).\n\n"
        "🏢 *Projeto Integrador II — Avaliação Pós-Ocupação (APO)*\n"
        "Análise de desempenho habitacional sob duas óticas: percepção "
        "do morador e checklist técnico do especialista (NBR 15575).\n\n"
        "📋 *Projeto Integrador III — Ambiente Regulatório*\n"
        "Roteiro prático para conduzir regularizações e aprovações de "
        "projetos em prefeituras — como se um colega sênior estivesse "
        "te orientando.\n"
        "Base legal: Lei 13.465/2017 (Reurb), Lei 6.766/79, Códigos de Obras.\n\n"
        "🎯 _Problemática:_ Quais são os principais entraves na aprovação de "
        "projetos residenciais na prefeitura e como mitigá-los?\n\n"
        "⚠️ Ferramenta de apoio acadêmico — não substitui a análise "
        "técnica presencial do profissional responsável.",
        parse_mode="Markdown",
    )


async def _fallback_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    if message is None:
        return

    text = message.text or ""

    if text == "📸 Dicas de Foto":
        await _help(update, context)
    elif text in ("ℹ️ Sobre o TCC", "ℹ️ Sobre o Projeto"):
        await _about(update, context)
    else:
        await _start(update, context)


# ── Bootstrap ───────────────────────────────────────────────

def create_application(settings: Settings):
    app = ApplicationBuilder().token(settings.telegram_token).build()

    ai_service = GeminiService(
        api_key=settings.google_api_key,
        model_name=settings.gemini_model,
    )
    app.bot_data["ai_service"] = ai_service

    app.add_handler(CommandHandler("start", _start))
    app.add_handler(CommandHandler("ajuda", _help))

    app.add_handler(patologia.create_handler())
    app.add_handler(regularizacao.create_handler())
    app.add_handler(apo.create_handler())

    app.add_handler(MessageHandler(filters.PHOTO, _photo_outside_conv))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _fallback_text))

    app.add_error_handler(error_handler)

    logger.info("Bot configurado com %d handlers", len(app.handlers.get(0, [])))
    return app


async def _photo_outside_conv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fotos recebidas fora do fluxo de patologia são tratadas diretamente."""
    import os
    import uuid
    from src.infrastructure.telegram.formatters import send_ai_response, send_typing

    message = update.effective_message
    telegram_message = update.message
    if message is None or telegram_message is None or not telegram_message.photo:
        return

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
