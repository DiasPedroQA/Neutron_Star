# Atoms/src/infra/leitor.py
# pylint: disable=too-few-public-methods

"""Implementação concreta do leitor físico de arquivos HTML do sistema."""

from pathlib import Path

from ..aplicacao.portas import LeitorHTMLPort


class LeitorHTML(LeitorHTMLPort):
    """Leitor de arquivos resiliente a variações de codificação (encoding)."""

    def ler_arquivo(self, caminho: Path) -> str:
        """Lê o arquivo HTML com encodings em cascata para evitar falhas de leitura.

        Tenta decodificar sequencialmente em UTF-8, Latin-1 e CP1252.
        Em caso de erro em todos os encodings padrão, realiza a decodificação
        em UTF-8 ignorando caracteres inválidos (failsafe de última instância).
        """
        caminho_resolvido: Path = caminho.expanduser().resolve()
        encodings_tentativas: list[str] = ["utf-8", "latin-1", "cp1252"]

        for encoding in encodings_tentativas:
            try:
                with open(file=caminho_resolvido, encoding=encoding) as arquivo:
                    return arquivo.read()
            except (UnicodeDecodeError, LookupError):
                continue

        # Fallback definitivo: abre ignorando bytes ilegíveis
        with open(file=caminho_resolvido, encoding="utf-8", errors="ignore") as arquivo:
            return arquivo.read()
