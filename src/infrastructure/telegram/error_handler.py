import html
import json
import logging
import traceback

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)

    if not isinstance(update, Update) or update.effective_message is None:
        return

    tb_list = traceback.format_exception(
        None, context.error, context.error.__traceback__ if context.error else None,
    )
    tb_string = "".join(tb_list)

    error_msg = (
        "⚠️ Ocorreu um erro interno. Tente novamente ou envie /start "
        "para reiniciar."
    )
    try:
        await update.effective_message.reply_text(error_msg)
    except Exception:
        logger.exception("Falha ao enviar mensagem de erro ao usuário")

    logger.error(
        "Update %s caused error:\n%s",
        json.dumps(update.to_dict(), indent=2, ensure_ascii=False)[:500],
        tb_string[:1500],
    )
