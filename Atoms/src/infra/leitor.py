# Atoms/src/infra/leitor.py
# pylint: disable=too-few-public-methods

"""Adaptador de infraestrutura para leitura física de arquivos HTML com fallback de encodings."""

from pathlib import Path

from aplicacao.portas import LeitorHTMLPort


class LeitorLocal(LeitorHTMLPort):
    """Implementação concreta de leitura de arquivos com cascata de decodificação resiliente."""

    def ler_arquivo(self, caminho: Path) -> str:
        """Lê o conteúdo textual de um arquivo aplicando cascata de encodings:

        1. UTF-8 (padrão web moderno)
        2. CP1252 (Windows ANSI com suporte a aspas curvas, travessões e símbolo do Euro)
        3. Latin-1 / ISO-8859-1 (fallback legado para qualquer byte de 0 a 255)
        4. UTF-8 com errors='replace' (garantia de nunca quebrar com arquivos binários/corrompidos)

        Raises:
            FileNotFoundError: Se o arquivo físico não existir no disco.
        """
        if not caminho.is_file():
            raise FileNotFoundError(f"Arquivo não encontrado no disco: {caminho}")

        conteudo_bytes: bytes = caminho.read_bytes()

        # Cascata de decodificação priorizando UTF-8 e CP1252 antes do Latin-1
        for codificacao in ("utf-8", "cp1252", "latin-1"):
            try:
                return conteudo_bytes.decode(encoding=codificacao)
            except UnicodeDecodeError:
                continue

        # Fallback de segurança máxima caso todos os decoders estritos falhem
        return conteudo_bytes.decode(encoding="utf-8", errors="replace")
