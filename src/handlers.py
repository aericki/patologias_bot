import os
import uuid
from typing import Any, cast
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.constants import ChatAction
from telegram.ext import ContextTypes
from src.ai_service import (
    analyze_image,
    gerar_checklist_regularizacao,
    gerar_checklist_aprovacao_projeto,
    gerar_followup_regularizacao,
)


def _user_data(context: ContextTypes.DEFAULT_TYPE) -> dict[str, Any]:
    if context.user_data is None:
        return {}
    return cast(dict[str, Any], context.user_data)


# ── Helpers de teclado ──────────────────────────────────────

def main_menu_markup() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([
        [KeyboardButton("📸 Analisar Patologia"), KeyboardButton("📋 Checklist Regularização")],
        [KeyboardButton("ℹ️ Sobre o Projeto")],
    ], resize_keyboard=True)


def regularizacao_submenu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Regularizar imóvel existente", callback_data="reg_existente")],
        [InlineKeyboardButton("📐 Aprovar projeto novo", callback_data="reg_projeto_novo")],
        [InlineKeyboardButton("📄 Consulta livre", callback_data="reg_consulta_livre")],
    ])


def tipo_imovel_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Casa", callback_data="tipo_casa"),
         InlineKeyboardButton("🏢 Apto", callback_data="tipo_apartamento")],
        [InlineKeyboardButton("🏪 Comércio", callback_data="tipo_comercio"),
         InlineKeyboardButton("🔀 Misto", callback_data="tipo_misto")],
    ])


def escritura_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Sim", callback_data="esc_sim"),
         InlineKeyboardButton("❌ Não", callback_data="esc_nao"),
         InlineKeyboardButton("📝 Só contrato", callback_data="esc_contrato")],
    ])


def followup_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Detalhar um item", callback_data="followup_detalhar")],
        [InlineKeyboardButton("📍 Informar minha cidade", callback_data="followup_cidade")],
        [InlineKeyboardButton("🏠 Menu principal", callback_data="followup_menu")],
    ])


# ── Comandos ────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if message is None:
        return

    user_data = _user_data(context)
    user_data.pop('regularizacao_state', None)
    user_data.pop('ultimo_checklist', None)

    await message.reply_text(
        "Olá, colega! Sou seu *Assistente Técnico de Engenharia Civil*. "
        "Fui feito para ajudar engenheiros e arquitetos recém-formados "
        "no dia a dia profissional.\n\n"
        "📸 *Patologias* — envie foto da vistoria para orientação de diagnóstico\n"
        "📋 *Regularização* — roteiro prático para conduzir legalização e aprovação\n\n"
        "Escolha uma opção abaixo:",
        reply_markup=main_menu_markup(),
        parse_mode='Markdown',
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        parse_mode='Markdown',
    )


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        "📋 *Projeto Integrador — Ambiente Regulatório*\n"
        "Roteiro prático para conduzir regularizações e aprovações de "
        "projetos em prefeituras — como se um colega sênior estivesse "
        "te orientando.\n"
        "Base legal: Lei 13.465/2017 (Reurb), Lei 6.766/79, Códigos de Obras.\n\n"
        "🎯 _Problemática:_ Quais são os principais entraves na aprovação de "
        "projetos residenciais na prefeitura e como mitigá-los?\n\n"
        "⚠️ Ferramenta de apoio acadêmico — não substitui a análise "
        "técnica presencial do profissional responsável.",
        parse_mode='Markdown',
    )


async def regularizar_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if message is None:
        return

    await message.reply_text(
        "📋 *Guia de Regularização de Imóveis*\n\nSelecione o tipo de consulta:",
        reply_markup=regularizacao_submenu(),
        parse_mode='Markdown',
    )


# ── Callback de botões inline ───────────────────────────────

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query is None:
        return

    await query.answer()
    data = query.data or ""
    user_data = _user_data(context)

    if data in ("reg_existente", "reg_projeto_novo"):
        cenario = "existente" if data == "reg_existente" else "projeto_novo"
        user_data['regularizacao_state'] = {
            'cenario': cenario,
            'etapa': 'tipo_imovel',
            'dados': {},
        }
        titulo = (
            "🏠 Regularizar imóvel existente"
            if cenario == "existente"
            else "📐 Aprovar projeto novo"
        )
        await query.edit_message_text(
            f"{titulo}\n\nQual o tipo do imóvel?",
            reply_markup=tipo_imovel_menu(),
        )
        return

    if data == "reg_consulta_livre":
        user_data['regularizacao_state'] = {
            'cenario': 'consulta_livre',
            'etapa': 'aguardando_texto',
            'dados': {},
        }
        await query.edit_message_text(
            "📄 *Consulta livre*\n\n"
            "Descreva a situação do imóvel com o máximo de detalhes.\n"
            "Exemplo: _'Construí uma casa de 50m² em Peruíbe, "
            "não tenho escritura, só contrato de compra e venda.'_\n\n"
            "Pode escrever abaixo:",
            parse_mode='Markdown',
        )
        return

    if data.startswith("tipo_"):
        state = cast(dict[str, Any], user_data.get('regularizacao_state', {}))
        tipo_map = {
            'tipo_casa': 'Casa',
            'tipo_apartamento': 'Apartamento',
            'tipo_comercio': 'Comércio',
            'tipo_misto': 'Misto',
        }
        dados = cast(dict[str, Any], state.setdefault('dados', {}))
        dados['tipo_imovel'] = tipo_map.get(data, data)
        state['etapa'] = 'escritura'
        user_data['regularizacao_state'] = state

        await query.edit_message_text(
            f"Tipo: *{dados['tipo_imovel']}* ✓\n\n"
            "O imóvel possui escritura ou matrícula no cartório?",
            reply_markup=escritura_menu(),
            parse_mode='Markdown',
        )
        return

    if data.startswith("esc_"):
        state = cast(dict[str, Any], user_data.get('regularizacao_state', {}))
        esc_map = {
            'esc_sim': 'Sim',
            'esc_nao': 'Não',
            'esc_contrato': 'Só contrato de compra e venda',
        }
        dados = cast(dict[str, Any], state.setdefault('dados', {}))
        dados['escritura'] = esc_map.get(data, data)
        state['etapa'] = 'cidade'
        user_data['regularizacao_state'] = state

        await query.edit_message_text(
            f"Tipo: *{dados.get('tipo_imovel', 'N/I')}* ✓\n"
            f"Escritura: *{dados.get('escritura', 'N/I')}* ✓\n\n"
            "Em qual *cidade e estado* fica o imóvel?\n"
            "Exemplo: _Peruíbe - SP_",
            parse_mode='Markdown',
        )
        return

    if data == "followup_detalhar":
        state = cast(dict[str, Any], user_data.get('regularizacao_state', {}))
        state['etapa'] = 'followup_detalhar'
        user_data['regularizacao_state'] = state
        await query.edit_message_text(
            "Qual item do checklist deseja detalhar?\n"
            "Escreva abaixo (ex: _Habite-se_, _ART_, _Matrícula_):",
            parse_mode='Markdown',
        )
        return

    if data == "followup_cidade":
        state = cast(dict[str, Any], user_data.get('regularizacao_state', {}))
        state['etapa'] = 'followup_cidade'
        user_data['regularizacao_state'] = state
        await query.edit_message_text(
            "📍 Informe a cidade e estado para refinar o checklist:\n"
            "Exemplo: _São Paulo - SP_",
            parse_mode='Markdown',
        )
        return

    if data == "followup_menu":
        user_data.pop('regularizacao_state', None)
        user_data.pop('ultimo_checklist', None)
        await query.edit_message_text("Voltando ao menu principal…")

        message = update.effective_message
        if message is not None:
            await message.reply_text("Escolha uma opção:", reply_markup=main_menu_markup())


# ── Mensagens de texto ──────────────────────────────────────

def _split_long_message(texto: str, limite: int = 3900) -> list[str]:
    if len(texto) <= limite:
        return [texto]

    partes: list[str] = []
    blocos = texto.split("\n\n")
    atual = ""

    for bloco in blocos:
        candidato = bloco if not atual else f"{atual}\n\n{bloco}"
        if len(candidato) <= limite:
            atual = candidato
            continue

        if atual:
            partes.append(atual)
            atual = ""

        if len(bloco) <= limite:
            atual = bloco
            continue

        linhas = bloco.split("\n")
        acumulado = ""
        for linha in linhas:
            candidato_linha = linha if not acumulado else f"{acumulado}\n{linha}"
            if len(candidato_linha) <= limite:
                acumulado = candidato_linha
            else:
                if acumulado:
                    partes.append(acumulado)
                while len(linha) > limite:
                    partes.append(linha[:limite])
                    linha = linha[limite:]
                acumulado = linha
        if acumulado:
            atual = acumulado

    if atual:
        partes.append(atual)

    return partes


async def _enviar_resposta_ia(message, texto: str):
    partes = _split_long_message(texto)

    if len(partes) == 1:
        try:
            await message.reply_text(partes[0], parse_mode='Markdown')
            return
        except Exception:
            await message.reply_text(partes[0])
            return

    for parte in partes:
        try:
            await message.reply_text(parte, parse_mode='Markdown')
        except Exception:
            await message.reply_text(parte)

async def _send_typing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat is not None:
        await context.bot.send_chat_action(chat_id=chat.id, action=ChatAction.TYPING)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if message is None or message.text is None:
        return

    text = message.text
    user_data = _user_data(context)
    state = cast(dict[str, Any], user_data.get('regularizacao_state', {}))

    if state.get('etapa') == 'cidade':
        dados = cast(dict[str, Any], state.setdefault('dados', {}))
        dados['cidade'] = text
        state['etapa'] = None
        user_data['regularizacao_state'] = state

        await message.reply_text("Gerando seu checklist personalizado… ⏳")
        await _send_typing(update, context)

        if state.get('cenario') == 'projeto_novo':
            resposta = await gerar_checklist_aprovacao_projeto(dados)
        else:
            descricao = (
                f"Tipo de imóvel: {dados.get('tipo_imovel', 'N/I')}. "
                f"Possui escritura/matrícula: {dados.get('escritura', 'N/I')}. "
                f"Localização: {dados.get('cidade', 'N/I')}."
            )
            resposta = await gerar_checklist_regularizacao(descricao)

        user_data['ultimo_checklist'] = resposta
        state['etapa'] = 'followup'
        user_data['regularizacao_state'] = state

        await _enviar_resposta_ia(message, resposta)
        await message.reply_text("Deseja aprofundar algum ponto?", reply_markup=followup_menu())
        return

    if state.get('etapa') == 'aguardando_texto':
        state['etapa'] = None
        user_data['regularizacao_state'] = state

        await message.reply_text("Gerando seu checklist personalizado… ⏳")
        await _send_typing(update, context)

        resposta = await gerar_checklist_regularizacao(text)
        user_data['ultimo_checklist'] = resposta
        state['etapa'] = 'followup'
        user_data['regularizacao_state'] = state

        await _enviar_resposta_ia(message, resposta)
        await message.reply_text("Deseja aprofundar algum ponto?", reply_markup=followup_menu())
        return

    if state.get('etapa') == 'followup_detalhar':
        ultimo = cast(str, user_data.get('ultimo_checklist', ''))
        state['etapa'] = 'followup'
        user_data['regularizacao_state'] = state

        await message.reply_text("Consultando detalhes… ⏳")
        await _send_typing(update, context)

        resposta = await gerar_followup_regularizacao(ultimo, text)
        await _enviar_resposta_ia(message, resposta)
        await message.reply_text("Mais alguma dúvida?", reply_markup=followup_menu())
        return

    if state.get('etapa') == 'followup_cidade':
        ultimo = cast(str, user_data.get('ultimo_checklist', ''))
        state['etapa'] = 'followup'
        user_data['regularizacao_state'] = state

        await message.reply_text("Refinando com legislação local… ⏳")
        await _send_typing(update, context)

        pergunta = (
            f"Refine o checklist para a cidade de {text}. "
            "Considere o Código de Obras municipal e exigências locais."
        )
        resposta = await gerar_followup_regularizacao(ultimo, pergunta)
        user_data['ultimo_checklist'] = resposta

        await _enviar_resposta_ia(message, resposta)
        await message.reply_text("Mais alguma dúvida?", reply_markup=followup_menu())
        return

    if text == "📸 Analisar Patologia":
        await message.reply_text(
            "Envie a foto da vistoria (trinca, fissura, infiltração) "
            "que eu te oriento no diagnóstico e na composição do laudo."
        )
    elif text == "📋 Checklist Regularização":
        await message.reply_text(
            "📋 *Guia de Regularização de Imóveis*\n\nSelecione o tipo de consulta:",
            reply_markup=regularizacao_submenu(),
            parse_mode='Markdown',
        )
    elif text == "📸 Dicas de Foto":
        await help_command(update, context)
    elif text in ("ℹ️ Sobre o TCC", "ℹ️ Sobre o Projeto"):
        await about_command(update, context)
    else:
        await start(update, context)


# ── Handler de fotos ────────────────────────────────────────

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    telegram_message = update.message
    if message is None or telegram_message is None or not telegram_message.photo:
        return

    photo_file = await telegram_message.photo[-1].get_file()

    await message.reply_text("Recebi! Analisando...")
    await _send_typing(update, context)

    try:
        file_path = f"temp_{uuid.uuid4()}.jpg"
        await photo_file.download_to_drive(file_path)

        analysis_result = await analyze_image(file_path)
        await _enviar_resposta_ia(message, analysis_result)

        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        await message.reply_text(f"Ocorreu um erro ao processar a imagem: {e}")
