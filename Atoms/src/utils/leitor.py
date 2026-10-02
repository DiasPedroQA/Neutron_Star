# Atoms/src/utils/leitor.py
# pylint: disable=too-few-public-methods

"""Módulo de leitura física de arquivos HTML com suporte a múltiplos encodings."""

from pathlib import Path


class LeitorLocal:
    """Implementação de leitura com cascata de decodificação resiliente."""

    @staticmethod
    def ler_arquivo(caminho: Path) -> str:
        """Lê o conteúdo textual de um arquivo aplicando cascata de encodings.

        1. UTF-8 (padrão web moderno)
        2. CP1252 (Windows ANSI com aspas curvas, travessões e símbolo do Euro)
        3. Latin-1 / ISO-8859-1 (último recurso: mapeia os 256 valores de byte,
           portanto nunca falha e a leitura jamais quebra com arquivos binários)

        Raises:
            FileNotFoundError: Se o arquivo físico não existir no disco.
        """
        if not caminho.is_file():
            raise FileNotFoundError(f"Arquivo não encontrado no disco: {caminho}")

        conteudo_bytes: bytes = caminho.read_bytes()

        for codificacao in ("utf-8", "cp1252"):
            try:
                return conteudo_bytes.decode(encoding=codificacao)
            except UnicodeDecodeError:
                continue

        return conteudo_bytes.decode(encoding="latin-1")
