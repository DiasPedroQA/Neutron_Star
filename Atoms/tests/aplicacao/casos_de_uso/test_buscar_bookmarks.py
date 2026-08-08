# """
# Testes para o módulo `buscar_bookmarks.py` do pacote `aplicacao.casos_de_uso`.

# Verifica a busca de arquivos HTML de bookmarks, o identificamento de metadados
# e a geração de relatórios, incluindo casos de sucesso e falha.
# """

# from __future__ import annotations

# from collections.abc import Generator
# from pathlib import Path

# import pytest

# from src.aplicacao.casos_de_uso.buscar_bookmarks import (
#     buscar_arquivos_html,
#     gerar_relatorio,
#     identificar_arquivo,
# )


# @pytest.fixture
# def estrutura_teste(tmp_path: Path) -> Path:
#     """
#     Cria uma estrutura de diretórios temporária com:
#     - arquivos HTML válidos e inválidos
#     - pastas ocultas (.) que devem ser ignoradas
#     """
#     base: Path = tmp_path / "home"
#     base.mkdir()

#     (base / "bookmarks.html").write_text(data="<DL><DT><A HREF='x'>X</A></DL>")
#     (base / "favoritos.html").write_text(data="<DL><DT><A HREF='y'>Y</A></DL>")
#     (base / "favorite_export.html").write_text(data="<DL></DL>")
#     (base / "index.html").write_text(data="<html></html>")
#     (base / "readme.txt").write_text(data="txt")

#     sub: Path = base / "sub"
#     sub.mkdir()
#     (sub / "bookmarks_2025.html").write_text(data="<DL><DT><A HREF='z'>Z</A></DL>")

#     oculta: Path = base / ".git"
#     oculta.mkdir()
#     (oculta / "bookmarks_secret.html").write_text(data="<DL></DL>")

#     return base


# @pytest.fixture
# def arquivo_valido(tmp_path: Path) -> Generator[Path, None, None]:
#     """Cria um arquivo HTML de bookmark válido com um link."""
#     content = "<DL><DT><A HREF='https://test.com'>Teste</A></DL>"
#     path: Path = tmp_path / "bookmark_test.html"
#     path.write_text(data=content, encoding="utf-8")
#     yield path


# @pytest.fixture
# def arquivo_sem_dl(tmp_path: Path) -> Generator[Path, None, None]:
#     """Cria um arquivo HTML sem a tag <DL> (inválido para bookmarks)."""
#     path: Path = tmp_path / "no_dl.html"
#     path.write_text(data="<html><body>Sem DL</body></html>", encoding="utf-8")
#     yield path


# # ---------------------------------------------------------------------------
# # Testes de busca de arquivos
# # ---------------------------------------------------------------------------


# def test_buscar_arquivos_html_encontra(estrutura_teste: Path) -> None:
#     """Deve encontrar arquivos HTML cujos nomes contenham 'bookmark' ou 'favorito'."""
#     resultados: list[Path] = buscar_arquivos_html(origem=estrutura_teste)
#     nomes: set[str] = {p.name for p in resultados}
#     assert "bookmarks.html" in nomes
#     assert "favoritos.html" in nomes
#     assert "favorite_export.html" in nomes
#     assert "bookmarks_2025.html" in nomes


# def test_buscar_arquivos_html_ignora_ocultos(estrutura_teste: Path) -> None:
#     """Não deve incluir arquivos em pastas cujo nome começa com '.'."""
#     resultados: list[Path] = buscar_arquivos_html(origem=estrutura_teste)
#     for p in resultados:
#         assert ".git" not in p.parts


# def test_buscar_arquivos_html_ignora_nao_bookmarks(estrutura_teste: Path) -> None:
#     """Não deve incluir arquivos HTML que não se pareçam com bookmarks."""
#     resultados: list[Path] = buscar_arquivos_html(origem=estrutura_teste)
#     nomes: set[str] = {p.name for p in resultados}
#     assert "index.html" not in nomes
#     assert "readme.txt" not in nomes


# def test_buscar_arquivos_html_vazio(tmp_path: Path) -> None:
#     """Retorna lista vazia quando não há arquivos correspondentes."""
#     assert buscar_arquivos_html(origem=tmp_path) == []


# # ---------------------------------------------------------------------------
# # Testes de identificar_arquivo
# # ---------------------------------------------------------------------------


# def test_identificar_arquivo_sucesso(arquivo_valido: Path) -> None:
#     """Identifica um arquivo HTML com um link e retorna metadados de sucesso."""
#     meta: dict[str, str | int | None] = identificar_arquivo(arquivo=arquivo_valido)
#     assert meta["status"] == "sucesso"
#     assert meta["nome"] == arquivo_valido.name
#     assert meta["erro"] is None
#     tamanho: str | int | None = meta["tamanho"]
#     if tamanho is not None:
#         assert isinstance(tamanho, int), "Tamanho deve ser um inteiro"
#         assert tamanho > 0, "Tamanho do arquivo deve ser positivo"


# def test_identificar_arquivo_sem_dl(arquivo_sem_dl: Path) -> None:
#     """Retorna erro quando a tag <DL> não é encontrada no HTML."""
#     meta: dict[str, str | int | None] = identificar_arquivo(arquivo=arquivo_sem_dl)
#     assert meta["status"] == "erro"
#     assert meta["erro"] == "Tag <DL> raiz não encontrada"


# def test_identificar_arquivo_inexistente() -> None:
#     """Levanta FileNotFoundError para caminho inexistente."""
#     with pytest.raises(FileNotFoundError):
#         identificar_arquivo(arquivo=Path("/nao/existe.html"))


# def test_identificar_arquivo_encoding_fallback(tmp_path: Path) -> None:
#     """Garante que o fallback de encoding funciona ao identificar."""
#     path: Path = tmp_path / "latin1.html"
#     content = "<DL><DT><A HREF='café'>Café</A></DL>"
#     path.write_text(data=content, encoding="latin-1")
#     meta: dict[str, str | int | None] = identificar_arquivo(arquivo=path)
#     assert meta["status"] == "sucesso"


# # ---------------------------------------------------------------------------
# # Testes do relatório
# # ---------------------------------------------------------------------------


# def test_gerar_relatorio_com_arquivos(estrutura_teste: Path) -> None:
#     """Gera relatório com múltiplos arquivos e verifica contagem de sucessos."""
#     metadados: list[dict[str, str | int | None]] = gerar_relatorio(pasta_entrada=estrutura_teste)
#     assert len(metadados) >= 3
#     sucessos: list[dict[str, str | int | None]] = [m for m in metadados if m["status"] == "sucesso"]
#     assert len(sucessos) >= 3


# def test_gerar_relatorio_sem_arquivos(tmp_path: Path) -> None:
#     """Retorna lista vazia quando não há bookmarks na pasta."""
#     assert gerar_relatorio(pasta_entrada=tmp_path) == []
