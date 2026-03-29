import asyncio
from types import MethodType

from src.services.ai_service import GeminiService


def test_gerar_apo_especialista_uses_observacao_placeholder():
    service = GeminiService.__new__(GeminiService)

    captured_prompt = {}

    async def fake_call(self, prompt: str) -> str:
        captured_prompt["value"] = prompt
        return "ok"

    service._call = MethodType(fake_call, service)

    result = asyncio.run(service.gerar_apo_especialista("umidade na parede"))

    assert result == "ok"
    assert "umidade na parede" in captured_prompt["value"]
    assert "CHECKLIST TÉCNICO DE APO" in captured_prompt["value"]
