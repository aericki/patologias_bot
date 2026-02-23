"""Testes do formatador de mensagens — lógica pura sem dependência do Telegram."""
import re
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ── Cópia local das funções puras (evita import do telegram) ──────────────────

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


def _polish_ai_text(text: str) -> str:
    text = re.sub(r"^#{1,3}\s*(.+)$", r"*\1*", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.+?)\*\*", r"*\1*", text)
    text = re.sub(r"^[\-\*]\s+", "• ", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ── Testes: split_long_message ────────────────────────────────────────────────

class TestSplitLongMessage:
    def test_short_message_unchanged(self):
        msg = "Mensagem curta"
        assert split_long_message(msg) == [msg]

    def test_empty_string(self):
        assert split_long_message("") == [""]

    def test_exactly_at_limit(self):
        msg = "x" * MAX_LENGTH
        result = split_long_message(msg, limite=MAX_LENGTH)
        assert result == [msg]

    def test_exceeds_limit_splits(self):
        msg = ("A" * 2000 + "\n\n") * 3
        result = split_long_message(msg, limite=MAX_LENGTH)
        assert len(result) > 1
        for parte in result:
            assert len(parte) <= MAX_LENGTH

    def test_custom_limit(self):
        result = split_long_message("abc\n\ndef", limite=5)
        assert all(len(p) <= 5 for p in result)


# ── Testes: _polish_ai_text ───────────────────────────────────────────────────

class TestPolishAiText:
    def test_headers_converted_to_bold(self):
        result = _polish_ai_text("### Diagnóstico")
        assert result == "*Diagnóstico*"

    def test_double_asterisk_to_single(self):
        result = _polish_ai_text("**texto importante**")
        assert result == "*texto importante*"

    def test_dash_bullet_normalized(self):
        result = _polish_ai_text("- item um\n- item dois")
        assert "• item um" in result
        assert "• item dois" in result

    def test_asterisk_bullet_normalized(self):
        result = _polish_ai_text("* item um")
        assert "• item um" in result

    def test_excessive_blank_lines_reduced(self):
        result = _polish_ai_text("a\n\n\n\nb")
        assert "\n\n\n" not in result

    def test_strips_whitespace(self):
        result = _polish_ai_text("  texto  \n")
        assert result == "texto"
