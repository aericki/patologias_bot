import logging

import google.generativeai as genai
from PIL import Image

from src.domain.prompts import (
    PROMPT_PATOLOGIA,
    PROMPT_REGULARIZACAO,
    PROMPT_APROVACAO_PROJETO,
    PROMPT_FOLLOWUP,
    PROMPT_APO_USUARIO,
    PROMPT_APO_ESPECIALISTA,
)

logger = logging.getLogger(__name__)


class GeminiService:
    """Encapsula todas as chamadas à API do Google Gemini."""

    def __init__(self, api_key: str, model_name: str = "gemini-flash-latest"):
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model_name)
        logger.info("GeminiService inicializado (model=%s)", model_name)

    async def _call(self, prompt: str) -> str:
        try:
            response = await self._model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            logger.exception("Erro na chamada ao Gemini")
            return f"Erro na IA: {e}"

    async def _call_with_image(self, prompt: str, image_path: str) -> str:
        try:
            img = Image.open(image_path)
            response = await self._model.generate_content_async([prompt, img])
            return response.text
        except Exception as e:
            logger.exception("Erro na análise de imagem")
            return f"Erro na análise da IA: {e}"

    # ── Patologia ───────────────────────────────────────────

    async def analyze_image(self, image_path: str) -> str:
        return await self._call_with_image(PROMPT_PATOLOGIA, image_path)

    # ── Regularização ───────────────────────────────────────

    async def gerar_checklist_regularizacao(self, descricao: str) -> str:
        prompt = PROMPT_REGULARIZACAO.format(descricao=descricao)
        return await self._call(prompt)

    async def gerar_checklist_aprovacao_projeto(
        self, tipo: str, escritura: str, cidade: str,
    ) -> str:
        prompt = PROMPT_APROVACAO_PROJETO.format(
            tipo=tipo, escritura=escritura, cidade=cidade,
        )
        return await self._call(prompt)

    async def gerar_followup_regularizacao(
        self, checklist_anterior: str, pergunta: str,
    ) -> str:
        prompt = PROMPT_FOLLOWUP.format(
            checklist_anterior=checklist_anterior, pergunta=pergunta,
        )
        return await self._call(prompt)

    # ── APO ─────────────────────────────────────────────────

    async def gerar_apo_usuario(self, relato: str) -> str:
        prompt = PROMPT_APO_USUARIO.format(relato=relato)
        return await self._call(prompt)

    async def gerar_apo_especialista(self, observacao: str) -> str:
        prompt = PROMPT_APO_ESPECIALISTA.format(observacao=observacao)
        return await self._call(prompt)
