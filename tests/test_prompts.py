"""Testes dos prompts — garante que as constantes contêm keywords obrigatórias."""

from src.domain.prompts.patologia import PROMPT_PATOLOGIA
from src.domain.prompts.regularizacao import (
    PROMPT_REGULARIZACAO,
    PROMPT_APROVACAO_PROJETO,
    PROMPT_FOLLOWUP,
)
from src.domain.prompts.apo import PROMPT_APO_USUARIO, PROMPT_APO_ESPECIALISTA
from src.domain.prompts.reuso import PROMPT_REUSO_AGUA


class TestPromptPatologia:
    def test_contains_nbr_references(self):
        assert "NBR" in PROMPT_PATOLOGIA
        assert "9575" in PROMPT_PATOLOGIA
        assert "15575" in PROMPT_PATOLOGIA

    def test_contains_classification_keywords(self):
        for keyword in ("FISSURA", "TRINCA", "RACHADURA", "INFILTRAÇÃO"):
            assert keyword in PROMPT_PATOLOGIA

    def test_contains_response_structure(self):
        for section in ("Diagnóstico", "Causa Provável", "Reparo Recomendado"):
            assert section in PROMPT_PATOLOGIA


class TestPromptRegularizacao:
    def test_contains_legal_references(self):
        assert "13.465/2017" in PROMPT_REGULARIZACAO
        assert "6.766/79" in PROMPT_REGULARIZACAO

    def test_has_placeholder(self):
        assert "{descricao}" in PROMPT_REGULARIZACAO

    def test_format_works(self):
        result = PROMPT_REGULARIZACAO.format(descricao="Teste")
        assert "Teste" in result


class TestPromptAprovacao:
    def test_has_placeholders(self):
        assert "{tipo}" in PROMPT_APROVACAO_PROJETO
        assert "{escritura}" in PROMPT_APROVACAO_PROJETO
        assert "{cidade}" in PROMPT_APROVACAO_PROJETO

    def test_format_works(self):
        result = PROMPT_APROVACAO_PROJETO.format(
            tipo="Casa", escritura="Sim", cidade="SP",
        )
        assert "Casa" in result


class TestPromptFollowup:
    def test_has_placeholders(self):
        assert "{checklist_anterior}" in PROMPT_FOLLOWUP
        assert "{pergunta}" in PROMPT_FOLLOWUP


class TestPromptAPOUsuario:
    def test_contains_apo_keywords(self):
        assert "Avaliação Pós-Ocupação" in PROMPT_APO_USUARIO
        assert "Conforto Ambiental" in PROMPT_APO_USUARIO

    def test_has_placeholder(self):
        assert "{relato}" in PROMPT_APO_USUARIO


class TestPromptAPOEspecialista:
    def test_contains_nbr_15575(self):
        assert "NBR 15575" in PROMPT_APO_ESPECIALISTA
        assert "Walkthrough" in PROMPT_APO_ESPECIALISTA

    def test_has_placeholder(self):
        assert "{observacao}" in PROMPT_APO_ESPECIALISTA


class TestPromptReuso:
    def test_has_placeholder(self):
        assert "{cidade}" in PROMPT_REUSO_AGUA
        assert "{calculo_preliminar}" in PROMPT_REUSO_AGUA

    def test_has_keywords(self):
        assert "NBR 15527" in PROMPT_REUSO_AGUA
        assert "Azevedo Netto" in PROMPT_REUSO_AGUA
        assert "Telegram" in PROMPT_REUSO_AGUA
