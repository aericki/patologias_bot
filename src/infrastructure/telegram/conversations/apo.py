import logging

from telegram import Update
from telegram.ext import (
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

from src.domain.models import ApoState, TipoAPO
from src.services.ai_service import GeminiService
from src.infrastructure.telegram.keyboards import apo_submenu, apo_post_menu, main_menu_markup
from src.infrastructure.telegram.formatters import send_ai_response, send_typing

logger = logging.getLogger(__name__)

CHOOSE_TIPO, INPUT_RELATO, INPUT_OBSERVACAO = range(3)


# ── Entry ───────────────────────────────────────────────────

async def _entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.effective_message
    if message is None:
        return ConversationHandler.END

    await message.reply_text(
        "🏢 *Avaliação Pós-Ocupação — APO*\n\n"
        "Selecione a perspectiva da análise:",
        reply_markup=apo_submenu(),
        parse_mode="Markdown",
    )
    return CHOOSE_TIPO


# ── Tipo ────────────────────────────────────────────────────

async def _choose_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    if query is None:
        return ConversationHandler.END
    await query.answer()
    await query.edit_message_text(
        "🗣️ *Relato do Morador*\n\n"
        "Peça ao morador (ou descreva você mesmo) a experiência de habitar "
        "o imóvel: conforto, funcionalidade, problemas do dia a dia.\n\n"
        "_Exemplo: 'O quarto é muito quente no verão. A janela pega sol o dia "
        "todo. O banheiro tem barulho de cano quando o vizinho usa a água.'_\n\n"
        "Pode escrever abaixo:",
        parse_mode="Markdown",
    )
    return INPUT_RELATO


async def _choose_especialista(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    if query is None:
        return ConversationHandler.END
    await query.answer()
    await query.edit_message_text(
        "👷 *Observação Técnica — Walkthrough*\n\n"
        "Descreva o que você está observando em campo. Inclua: sistema construtivo "
        "afetado, tempo de uso do imóvel, manifestação patológica visível.\n\n"
        "_Exemplo: 'Manchas de umidade ascendente na parede da sala, ~40 cm de "
        "altura, imóvel com 8 anos. Piso cerâmico com som cavo em 3 pontos próximos "
        "à janela.'_\n\n"
        "Pode escrever abaixo:",
        parse_mode="Markdown",
    )
    return INPUT_OBSERVACAO


# ── Input handlers ──────────────────────────────────────────

async def _handle_relato(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.effective_message
    if message is None or message.text is None:
        return ConversationHandler.END

    await message.reply_text("Analisando o relato do morador… ⏳")
    await send_typing(update, context)

    ai: GeminiService = context.bot_data["ai_service"]
    resposta = await ai.gerar_apo_usuario(message.text)
    await send_ai_response(message, resposta)
    await message.reply_text(
        "Deseja voltar ao menu principal?",
        reply_markup=apo_post_menu("apo_usuario"),
    )
    return CHOOSE_TIPO


async def _handle_observacao(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.effective_message
    if message is None or message.text is None:
        return ConversationHandler.END

    await message.reply_text("Gerando checklist técnico de APO… ⏳")
    await send_typing(update, context)

    ai: GeminiService = context.bot_data["ai_service"]
    resposta = await ai.gerar_apo_especialista(message.text)
    await send_ai_response(message, resposta)
    await message.reply_text(
        "Deseja voltar ao menu principal?",
        reply_markup=apo_post_menu("apo_especialista"),
    )
    return CHOOSE_TIPO


# ── Back to menu ────────────────────────────────────────────

async def _back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    if query is None:
        return ConversationHandler.END
    await query.answer()
    await query.edit_message_text("Voltando ao menu principal…")

    message = update.effective_message
    if message is not None:
        await message.reply_text("Escolha uma opção:", reply_markup=main_menu_markup())
    return ConversationHandler.END


# ── Handler factory ─────────────────────────────────────────

def create_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^🏢 Avaliação Pós-Ocupação \\(APO\\)$"), _entry),
        ],
        states={
            CHOOSE_TIPO: [
                CallbackQueryHandler(_choose_usuario, pattern="^apo_usuario$"),
                CallbackQueryHandler(_choose_especialista, pattern="^apo_especialista$"),
                CallbackQueryHandler(_back_to_menu, pattern="^apo_menu$"),
            ],
            INPUT_RELATO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, _handle_relato),
            ],
            INPUT_OBSERVACAO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, _handle_observacao),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(_back_to_menu, pattern="^apo_menu$"),
        ],
        name="apo",
        allow_reentry=True,
    )
