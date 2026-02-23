import logging
from typing import Any, cast

from telegram import Update
from telegram.ext import (
    ConversationHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

from src.domain.models import ReusoState
from src.services.ai_service import GeminiService
from src.infrastructure.telegram.formatters import send_ai_response, send_typing
from src.infrastructure.telegram.keyboards import reuso_post_menu, main_menu_markup

logger = logging.getLogger(__name__)

INPUT_CIDADE, INPUT_AREA, INPUT_MORADORES = range(3)

# Constantes do dimensionamento (Método Azevedo Netto / NBR 15527)
RUNOFF = 0.80          # coeficiente de escoamento superficial para telhado comum
PLUVIO_PADRAO = 100.0  # mm/mês (fallback; a IA ajusta pelo município)
CONSUMO_NAO_POTAVEL_L_DIA = 53.0  # litros/pessoa/dia (descargas + piso + jardim)


# ── Helpers ─────────────────────────────────────────────────

def _get_state(context: ContextTypes.DEFAULT_TYPE) -> ReusoState:
    """Retorna (e cria se necessário) o ReusoState persistido em user_data."""
    ud: dict[str, Any] = context.user_data  # type: ignore[assignment]
    if "reuso_state" not in ud:
        ud["reuso_state"] = ReusoState()
    return ud["reuso_state"]  # type: ignore[return-value]


def _clear_state(context: ContextTypes.DEFAULT_TYPE) -> None:
    ud: dict[str, Any] = context.user_data  # type: ignore[assignment]
    ud.pop("reuso_state", None)


def _calcular_reuso(area_m2: float, moradores: int) -> dict:
    """Calcula os valores preliminares usando o Método Azevedo Netto."""
    # Volume mensal captável: V = A x P x C  (m² x m x adimensional → m³ → L)
    vol_mensal_l = area_m2 * (PLUVIO_PADRAO / 1000) * RUNOFF * 1000  # em litros
    # Demanda mensal não potável
    demanda_mensal_l = CONSUMO_NAO_POTAVEL_L_DIA * moradores * 30
    # Volume da cisterna: C = V / 12 (Azevedo Netto)
    cisterna_l = (area_m2 * 1.0 * RUNOFF * 1000) / 12
    # Economia percentual
    economia_pct = min((vol_mensal_l / demanda_mensal_l) * 100, 100)
    return {
        "area": area_m2,
        "moradores": moradores,
        "vol_mensal_l": round(vol_mensal_l, 1),
        "demanda_mensal_l": round(demanda_mensal_l, 1),
        "cisterna_l": round(cisterna_l, 1),
        "economia_pct": round(economia_pct, 1),
    }


def _formatar_calculo(c: dict) -> str:
    return (
        f"• Área de captação: {c['area']} m²\n"
        f"• Moradores: {c['moradores']}\n"
        f"• Runoff: {RUNOFF} (telhado comum)\n"
        f"• Pluviometria usada (fallback): {PLUVIO_PADRAO} mm/mês\n\n"
        f"*Volume mensal captável (Método Azevedo Netto):*\n"
        f"  V = A × P × C = {c['area']} × {PLUVIO_PADRAO/1000} × {RUNOFF} × 1.000 L\n"
        f"  V = {c['vol_mensal_l']} L/mês\n\n"
        f"*Demanda mensal não potável (descargas, piso, jardim):*\n"
        f"  D = {CONSUMO_NAO_POTAVEL_L_DIA} L/pessoa/dia × {c['moradores']} × 30 dias\n"
        f"  D = {c['demanda_mensal_l']} L/mês\n\n"
        f"*Volume da cisterna estimado (C = V/12):*\n"
        f"  C = {c['cisterna_l']} L (~{c['cisterna_l']/1000:.2f} m³)\n\n"
        f"*Economia estimada:* {c['economia_pct']}%"
    )


# ── Entry ───────────────────────────────────────────────────

async def _entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.effective_message
    if message is None:
        return ConversationHandler.END

    _clear_state(context)
    await message.reply_text(
        "🌱 *Edifício Sustentável — Reuso de Água (NBR 15527)*\n\n"
        "Vamos dimensionar um sistema de captação de água pluvial!\n\n"
        "Primeiro: qual é a *Cidade e Estado* do projeto?\n"
        "_(Ex: Peruíbe - SP)_",
        parse_mode="Markdown",
    )
    return INPUT_CIDADE


async def _handle_restart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    if query is None:
        return ConversationHandler.END
    await query.answer()
    _clear_state(context)
    await query.edit_message_text(
        "🌱 Novo dimensionamento!\nQual é a *Cidade e Estado* do projeto?",
        parse_mode="Markdown",
    )
    return INPUT_CIDADE


# ── Cidade ──────────────────────────────────────────────────

async def _handle_cidade(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.effective_message
    if message is None or message.text is None:
        return ConversationHandler.END

    _get_state(context).cidade = message.text.strip()
    await message.reply_text(
        "Ótimo! Agora me informe a *Área de Cobertura do Telhado* em m²:\n"
        "_(Ex: 80)_",
        parse_mode="Markdown",
    )
    return INPUT_AREA


# ── Área ────────────────────────────────────────────────────

async def _handle_area(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.effective_message
    if message is None or message.text is None:
        return ConversationHandler.END

    text = message.text.strip().replace(",", ".").split()[0]  # "80 m²" → "80"
    try:
        float(text)
    except ValueError:
        await message.reply_text("Digite apenas o número da área em m². _(Ex: 80)_", parse_mode="Markdown")
        return INPUT_AREA

    _get_state(context).area = text
    await message.reply_text(
        "Perfeito! Por último, quantos *moradores* terá a residência?\n"
        "_(Ex: 3)_",
        parse_mode="Markdown",
    )
    return INPUT_MORADORES


# ── Moradores + Cálculo + IA ────────────────────────────────

async def _handle_moradores(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    message = update.effective_message
    if message is None or message.text is None:
        return ConversationHandler.END

    text = message.text.strip().split()[0]
    try:
        moradores = int(text)
    except ValueError:
        await message.reply_text("Digite apenas o número de moradores. _(Ex: 3)_", parse_mode="Markdown")
        return INPUT_MORADORES

    state = _get_state(context)
    state.moradores = text

    try:
        area_m2 = float(state.area or "0")
    except ValueError:
        area_m2 = 0.0

    # ── Cálculo local ──────────────────────────────────────
    calculo = _calcular_reuso(area_m2, moradores)
    resumo = _formatar_calculo(calculo)

    await message.reply_text(
        "📐 *Cálculo Preliminar (Azevedo Netto)*\n\n" + resumo,
        parse_mode="Markdown",
    )
    await message.reply_text("Consultando a IA para validação e análise de viabilidade… ⏳")
    await send_typing(update, context)

    # ── IA valida e complementa ────────────────────────────
    ai: GeminiService = context.bot_data["ai_service"]
    resposta = await ai.gerar_relatorio_reuso_agua(
        cidade=state.cidade or "Não informado",
        calculo_preliminar=resumo,
    )
    await send_ai_response(message, resposta)
    await message.reply_text(
        "Deseja calcular novamente ou voltar ao menu?",
        reply_markup=reuso_post_menu(),
    )
    return ConversationHandler.END


# ── Fallback ────────────────────────────────────────────────

async def _back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    if query is None:
        return ConversationHandler.END
    await query.answer()
    await query.edit_message_text("Voltando ao menu principal…")
    _clear_state(context)
    return ConversationHandler.END


# ── Handler Factory ─────────────────────────────────────────

def create_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^🌱 Edifício Sustentável \\(Reuso\\)$"), _entry),
            CallbackQueryHandler(_handle_restart_callback, pattern="^reuso_novo$"),
        ],
        states={
            INPUT_CIDADE: [MessageHandler(filters.TEXT & ~filters.COMMAND, _handle_cidade)],
            INPUT_AREA:   [MessageHandler(filters.TEXT & ~filters.COMMAND, _handle_area)],
            INPUT_MORADORES: [MessageHandler(filters.TEXT & ~filters.COMMAND, _handle_moradores)],
        },
        fallbacks=[
            CallbackQueryHandler(_back_to_menu, pattern="^reuso_menu$"),
        ],
        name="reuso",
        allow_reentry=True,
    )
