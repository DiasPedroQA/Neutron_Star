import contextlib
from pathlib import Path

from dominio.excecoes import ErroParseBookmarks, NenhumDiretorioValidoError


def normalizar_e_validar(caminho_bruto: str) -> Path | None:
    """Expande ~, resolve caminho e retorna se for diretório acessível."""
    with contextlib.suppress(OSError, RuntimeError):
        caminho: Path = Path(caminho_bruto).expanduser().resolve(strict=False)
        if caminho.is_dir():
            return caminho
    return None


def confirmar_dados_entrada(caminhos: list[str]) -> list[Path]:
    """Valida lista de strings, retornando apenas diretórios válidos."""
    validos: list[Path] = []
    for caminho_str in caminhos:
        if caminho_valido := normalizar_e_validar(caminho_bruto=caminho_str):
            print(f"[OK] '{caminho_str}' → {caminho_valido}")
            validos.append(caminho_valido)
        else:
            print(f"[FALHA] '{caminho_str}' não é um diretório acessível.")
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
        raise ErroParseBookmarks(f"Não foi possível ler '{caminho}': {exc}") from exc
