"""Funções de infraestrutura para interação com o sistema de arquivos.

Fornece utilitários para normalizar e validar caminhos de diretório e
para leitura segura de arquivos HTML com tratamento de erros amigável.
"""

import contextlib
from pathlib import Path

from dominio.excecoes import (
    ErroParseBookmarks,
    NenhumDiretorioValidoError,
)


def normalizar_e_validar(caminho_bruto: str) -> Path | None:
    """Expande ~/, resolve caminho e retorna se for diretório acessível."""
    with contextlib.suppress(OSError, RuntimeError):
        caminho: Path = Path(caminho_bruto).expanduser().resolve(strict=False)
        return caminho if caminho.is_dir() else None
    return None


def confirmar_dados_entrada(caminhos: Path) -> list[Path]:
    """Valida lista de strings, retornando apenas diretórios válidos."""
    validos: list[Path] = []
    if caminho_valido := normalizar_e_validar(caminho_bruto=str(caminhos)):
        print(f"[OK] '{caminhos}' → {caminho_valido}")
        validos.append(caminho_valido)
    else:
        print(f"[FALHA] '{caminhos}' não é um diretório acessível.")
    if not validos:
        raise NenhumDiretorioValidoError(
            mensagem="Nenhum diretório válido.",
            contexto={"caminhos_tentados": caminhos},
        )
    return validos


def ler_arquivo_html(caminho: Path) -> str:
    """Lê o conteúdo de um arquivo HTML com tratamento de erros."""
    try:
        return caminho.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ErroParseBookmarks(mensagem=f"Não foi possível ler '{caminho}': {exc}") from exc
