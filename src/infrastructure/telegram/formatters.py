import logging

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

MAX_LENGTH = 3900


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


async def send_ai_response(message, texto: str) -> None:
    partes = split_long_message(texto)
    for parte in partes:
        try:
            await message.reply_text(parte, parse_mode="Markdown")
        except Exception:
            logger.warning("Fallback: enviando sem Markdown parse")
            await message.reply_text(parte)


async def send_typing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if chat is not None:
        await context.bot.send_chat_action(chat_id=chat.id, action=ChatAction.TYPING)
