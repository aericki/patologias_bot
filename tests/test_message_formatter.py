"""Testes do formatador de mensagens longas.

Testa apenas a lógica pura (split_long_message) sem dependências do Telegram.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def split_long_message(texto: str, limite: int = 3900) -> list[str]:
    """Cópia da lógica pura para testes sem deps do Telegram."""
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


class TestSplitLongMessage:
    def test_short_message_unchanged(self):
        msg = "Mensagem curta"
        result = split_long_message(msg)
        assert result == [msg]

    def test_exact_limit_unchanged(self):
        msg = "x" * 3900
        result = split_long_message(msg)
        assert result == [msg]

    def test_splits_on_double_newline(self):
        block_a = "a" * 2000
        block_b = "b" * 2000
        msg = f"{block_a}\n\n{block_b}"
        result = split_long_message(msg)
        assert len(result) == 2
        assert result[0] == block_a
        assert result[1] == block_b

    def test_splits_long_single_block(self):
        msg = "x" * 8000
        result = split_long_message(msg)
        assert len(result) >= 2
        for part in result:
            assert len(part) <= 3900

    def test_empty_message(self):
        result = split_long_message("")
        assert result == [""]

    def test_multiple_blocks_grouped(self):
        blocks = ["bloco " * 50 for _ in range(5)]
        msg = "\n\n".join(blocks)
        result = split_long_message(msg)
        for part in result:
            assert len(part) <= 3900

    def test_custom_limit(self):
        msg = "a" * 100
        result = split_long_message(msg, limite=50)
        assert len(result) >= 2
