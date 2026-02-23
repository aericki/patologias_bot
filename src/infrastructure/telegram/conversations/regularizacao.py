import logging
from typing import Any, cast

from telegram import Update
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

from src.domain.models import (
    RegularizacaoState,
    CenarioRegularizacao,
    TipoImovel,
    Escritura,
)
from src.services.ai_service import GeminiService
from src.infrastructure.telegram.keyboards import (
    regularizacao_submenu,
    tipo_imovel_menu,
    escritura_menu,
    followup_menu,
    main_menu_markup,
)
from src.infrastructure.telegram.formatters import send_ai_response, send_typing

logger = logging.getLogger(__name__)

CHOOSE_CENARIO, CHOOSE_TIPO, CHOOSE_ESCRITURA, INPUT_CIDADE = range(4)
INPUT_TEXTO_LIVRE, FOLLOWUP, FOLLOWUP_DETALHAR, FOLLOWUP_CIDADE = range(4, 8)

# ── Helpers ─────────────────────────────────────────────────

def _get_state(context: ContextTypes.DEFAULT_TYPE) -> RegularizacaoState | None:
    ud = cast(dict[str, Any], context.user_data) if context.user_data else {}
    return ud.get("reg_state")


def _set_state(context: ContextTypes.DEFAULT_TYPE, state: RegularizacaoState) -> None:
    if context.user_data is not None:
        cast(dict[str, Any], context.user_data)["reg_state"] = state


def _clear_state(context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data is not None:
        cast(dict[str, Any], context.user_data).pop("reg_state", None)


# ── Entry ───────────────────────────────────────────────────

async def _entry_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.effective_message
    if message is None:
        return ConversationHandler.END

    await message.reply_text(
        "📋 *Guia de Regularização de Imóveis*\n\nSelecione o tipo de consulta:",
        reply_markup=regularizacao_submenu(),
        parse_mode="Markdown",
    )
    return CHOOSE_CENARIO


async def _entry_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await _entry_menu(update, context)


# ── Cenário ─────────────────────────────────────────────────

async def _choose_cenario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    if query is None:
        return ConversationHandler.END
    await query.answer()
    data = query.data or ""

    if data in ("reg_existente", "reg_projeto_novo"):
        cenario = (
            CenarioRegularizacao.EXISTENTE
            if data == "reg_existente"
            else CenarioRegularizacao.PROJETO_NOVO
        )
        _set_state(context, RegularizacaoState(cenario=cenario))
        titulo = (
            "🏠 Regularizar imóvel existente"
            if cenario == CenarioRegularizacao.EXISTENTE
            else "📐 Aprovar projeto novo"
        )
        await query.edit_message_text(
            f"{titulo}\n\nQual o tipo do imóvel?",
            reply_markup=tipo_imovel_menu(),
        )
        return CHOOSE_TIPO

    if data == "reg_consulta_livre":
        _set_state(context, RegularizacaoState(cenario=CenarioRegularizacao.CONSULTA_LIVRE))
        await query.edit_message_text(
            "📄 *Consulta livre*\n\n"
            "Descreva a situação do imóvel com o máximo de detalhes.\n"
            "Exemplo: _'Construí uma casa de 50m² em Peruíbe, "
            "não tenho escritura, só contrato de compra e venda.'_\n\n"
            "Pode escrever abaixo:",
            parse_mode="Markdown",
        )
        return INPUT_TEXTO_LIVRE

    return ConversationHandler.END


# ── Tipo de imóvel ──────────────────────────────────────────

TIPO_MAP = {
    "tipo_casa": TipoImovel.CASA,
    "tipo_apartamento": TipoImovel.APARTAMENTO,
    "tipo_comercio": TipoImovel.COMERCIO,
    "tipo_misto": TipoImovel.MISTO,
}


async def _choose_tipo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    if query is None:
        return ConversationHandler.END
    await query.answer()

    state = _get_state(context)
    if state is None:
        return ConversationHandler.END

    tipo = TIPO_MAP.get(query.data or "")
    if tipo is None:
        return ConversationHandler.END

    state.tipo_imovel = tipo
    _set_state(context, state)

    await query.edit_message_text(
        f"Tipo: *{tipo.value}* ✓\n\n"
        "O imóvel possui escritura ou matrícula no cartório?",
        reply_markup=escritura_menu(),
        parse_mode="Markdown",
    )
    return CHOOSE_ESCRITURA


# ── Escritura ───────────────────────────────────────────────

ESC_MAP = {
    "esc_sim": Escritura.SIM,
    "esc_nao": Escritura.NAO,
    "esc_contrato": Escritura.CONTRATO,
}


async def _choose_escritura(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    if query is None:
        return ConversationHandler.END
    await query.answer()

    state = _get_state(context)
    if state is None:
        return ConversationHandler.END

    esc = ESC_MAP.get(query.data or "")
    if esc is None:
        return ConversationHandler.END

    state.escritura = esc
    _set_state(context, state)

    tipo_label = state.tipo_imovel.value if state.tipo_imovel else "N/I"
    await query.edit_message_text(
        f"Tipo: *{tipo_label}* ✓\n"
        f"Escritura: *{esc.value}* ✓\n\n"
        "Em qual *cidade e estado* fica o imóvel?\n"
        "Exemplo: _Peruíbe - SP_",
        parse_mode="Markdown",
    )
    return INPUT_CIDADE


# ── Cidade + geração de checklist ───────────────────────────

async def _input_cidade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.effective_message
    if message is None or message.text is None:
        return ConversationHandler.END

    state = _get_state(context)
    if state is None:
        return ConversationHandler.END

    state.cidade = message.text
    _set_state(context, state)

    await message.reply_text("Gerando seu checklist personalizado… ⏳")
    await send_typing(update, context)

    ai: GeminiService = context.bot_data["ai_service"]

    if state.cenario == CenarioRegularizacao.PROJETO_NOVO:
        resposta = await ai.gerar_checklist_aprovacao_projeto(
            tipo=state.tipo_imovel.value if state.tipo_imovel else "N/I",
            escritura=state.escritura.value if state.escritura else "N/I",
            cidade=state.cidade or "N/I",
        )
    else:
        resposta = await ai.gerar_checklist_regularizacao(state.resumo_dados())

    state.ultimo_checklist = resposta
    _set_state(context, state)

    await send_ai_response(message, resposta)
    await message.reply_text("Deseja aprofundar algum ponto?", reply_markup=followup_menu())
    return FOLLOWUP


# ── Consulta livre ──────────────────────────────────────────

async def _input_texto_livre(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.effective_message
    if message is None or message.text is None:
        return ConversationHandler.END

    await message.reply_text("Gerando seu checklist personalizado… ⏳")
    await send_typing(update, context)

    ai: GeminiService = context.bot_data["ai_service"]
    resposta = await ai.gerar_checklist_regularizacao(message.text)

    state = _get_state(context)
    if state:
        state.ultimo_checklist = resposta
        _set_state(context, state)

    await send_ai_response(message, resposta)
    await message.reply_text("Deseja aprofundar algum ponto?", reply_markup=followup_menu())
    return FOLLOWUP


# ── Follow-up ───────────────────────────────────────────────

async def _followup_detalhar_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    if query is None:
        return ConversationHandler.END
    await query.answer()
    await query.edit_message_text(
        "Qual item do checklist deseja detalhar?\n"
        "Escreva abaixo (ex: _Habite-se_, _ART_, _Matrícula_):",
        parse_mode="Markdown",
    )
    return FOLLOWUP_DETALHAR


async def _followup_detalhar_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.effective_message
    if message is None or message.text is None:
        return ConversationHandler.END

    state = _get_state(context)
    checklist = state.ultimo_checklist if state else ""

    await message.reply_text("Consultando detalhes… ⏳")
    await send_typing(update, context)

    ai: GeminiService = context.bot_data["ai_service"]
    resposta = await ai.gerar_followup_regularizacao(checklist, message.text)
    await send_ai_response(message, resposta)
    await message.reply_text("Mais alguma dúvida?", reply_markup=followup_menu())
    return FOLLOWUP


async def _followup_cidade_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    if query is None:
        return ConversationHandler.END
    await query.answer()
    await query.edit_message_text(
        "📍 Informe a cidade e estado para refinar o checklist:\n"
        "Exemplo: _São Paulo - SP_",
        parse_mode="Markdown",
    )
    return FOLLOWUP_CIDADE


async def _followup_cidade_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.effective_message
    if message is None or message.text is None:
        return ConversationHandler.END

    state = _get_state(context)
    checklist = state.ultimo_checklist if state else ""

    await message.reply_text("Refinando com legislação local… ⏳")
    await send_typing(update, context)

    pergunta = (
        f"Refine o checklist para a cidade de {message.text}. "
        "Considere o Código de Obras municipal e exigências locais."
    )
    ai: GeminiService = context.bot_data["ai_service"]
    resposta = await ai.gerar_followup_regularizacao(checklist, pergunta)

    if state:
        state.ultimo_checklist = resposta
        _set_state(context, state)

    await send_ai_response(message, resposta)
    await message.reply_text("Mais alguma dúvida?", reply_markup=followup_menu())
    return FOLLOWUP


async def _followup_back(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    if query is None:
        return ConversationHandler.END
    await query.answer()
    _clear_state(context)
    await query.edit_message_text("Voltando ao menu principal…")

    message = update.effective_message
    if message is not None:
        await message.reply_text("Escolha uma opção:", reply_markup=main_menu_markup())
    return ConversationHandler.END


# ── Handler factory ─────────────────────────────────────────

def create_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^📋 Checklist Regularização$"), _entry_menu),
            CommandHandler("regularizar", _entry_command),
        ],
        states={
            CHOOSE_CENARIO: [
                CallbackQueryHandler(_choose_cenario, pattern="^reg_"),
            ],
            CHOOSE_TIPO: [
                CallbackQueryHandler(_choose_tipo, pattern="^tipo_"),
            ],
            CHOOSE_ESCRITURA: [
                CallbackQueryHandler(_choose_escritura, pattern="^esc_"),
            ],
            INPUT_CIDADE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, _input_cidade),
            ],
            INPUT_TEXTO_LIVRE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, _input_texto_livre),
            ],
            FOLLOWUP: [
                CallbackQueryHandler(_followup_detalhar_entry, pattern="^followup_detalhar$"),
                CallbackQueryHandler(_followup_cidade_entry, pattern="^followup_cidade$"),
                CallbackQueryHandler(_followup_back, pattern="^followup_menu$"),
            ],
            FOLLOWUP_DETALHAR: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, _followup_detalhar_text),
            ],
            FOLLOWUP_CIDADE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, _followup_cidade_text),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(_followup_back, pattern="^followup_menu$"),
        ],
        name="regularizacao",
        allow_reentry=True,
    )
