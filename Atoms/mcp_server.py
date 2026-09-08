"""Servidor MCP para o projeto Atoms."""

from pathlib import Path

from fastmcp import FastMCP

from file_manager import listar_arquivos, ler_arquivo

# Cria o servidor MCP com um nome descritivo
mcp = FastMCP("Atoms")


@mcp.tool()
def listar_arquivos_mcp(padrao: str = "*") -> list[str]:
    """Lista arquivos das pastas base, opcionalmente filtrando por padrão.

    Args:
        padrao: Padrão glob (ex.: "*.html", "favoritos_*.html").

    Returns:
        Lista de caminhos dos arquivos encontrados.
    """
    arquivos = listar_arquivos(padrao)
    return [str(a) for a in arquivos]


@mcp.tool()
def ler_arquivo_mcp(caminho: str) -> str:
    """Lê o conteúdo de um arquivo de texto.

    Args:
        caminho: Caminho do arquivo.

    Returns:
        Conteúdo do arquivo.
    """
    return ler_arquivo(Path(caminho))


if __name__ == "__main__":
    # Inicia o servidor usando transporte stdio (padrão para MCP)
    mcp.run()
