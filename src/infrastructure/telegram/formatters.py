import logging
import re

from telegram import Update, Message
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

MAX_LENGTH = 3900

# Separador visual entre partes de respostas longas
_SEPARATOR = "\n〰〰〰〰〰〰〰〰〰〰\n\n"

# Caracteres que DEVEM ser escapados no MarkdownV2 fora de entidades
_MDV2_SPECIAL = r"\_*[]()~`>#+=|{}.!-"


def escape_mdv2(text: str) -> str:
    """Escapa todos os caracteres especiais do MarkdownV2, preservando formatação básica."""
    # Escapa tudo exceto os que já estão como sintaxe intencional (*, _, `, ~)
    return re.sub(r"([\_\*\[\]\(\)\~\`\>\#\+\-\=\|\{\}\.\!])", r"\\\1", text)


def _polish_ai_text(text: str) -> str:
    """
    Pós-processa o texto vindo da IA para melhorar aparência no Telegram:
    - Converte **negrito** → *negrito* (MarkdownV2)
    - Transforma linhas de header (### ...) em linha com emoji negritado
    - Adiciona espaçamento entre seções
    - Normaliza bullets
    """
    # Remove headers markdown (###, ##, #) e converte para linha negritada
    text = re.sub(r"^#{1,3}\s*(.+)$", r"*\1*", text, flags=re.MULTILINE)

    # Converte **texto** → *texto* (bold mdv2)
    text = re.sub(r"\*\*(.+?)\*\*", r"*\1*", text)

    # Normaliza bullets: "- " e "* " no início de linha → "• "
    text = re.sub(r"^[\-\*]\s+", "• ", text, flags=re.MULTILINE)

    # Remove linha em branco excessiva (3+ → 2)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def split_long_message(texto: str, limite: int = MAX_LENGTH) -> list[str]:
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


async def send_ai_response(message: Message, texto: str) -> None:
    """Envia resposta da IA com formatação polida e fallback seguro."""
    texto_polido = _polish_ai_text(texto)
    partes = split_long_message(texto_polido)

    for i, parte in enumerate(partes):
        # Adiciona indicador visual se for mensagem multi-parte
        if len(partes) > 1 and i < len(partes) - 1:
            parte = parte + _SEPARATOR

        try:
            await message.reply_text(parte, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.warning("Falha com Markdown (%s). Enviando texto plano.", e)
            # Fallback: remove toda formatação e envia como texto puro
            texto_plain = re.sub(r"[*_`~]", "", parte)
            await message.reply_text(texto_plain)


async def send_typing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if chat is not None:
        await context.bot.send_chat_action(chat_id=chat.id, action=ChatAction.TYPING)
