# """Casos de uso do serviço de busca.

# Não importam FastAPI, `pathlib.Path.rglob` real, nem BeautifulSoup — só a
# porta `RepositorioFavoritos`. Isso permite testar o caso de uso com um fake
# em memória, sem tocar disco.
# """

# from __future__ import annotations

# from dataclasses import dataclass
# from pathlib import Path

# from dominio.entidades import Bookmark
# from dominio.excecoes import PastaInvalidaError

# from busca_api.aplicacao.portas import RepositorioFavoritos


# @dataclass(frozen=True, slots=True)
# class ResultadoBusca:
#     """Resultado agregado de uma busca: bookmarks encontrados e arquivos de origem."""

#     bookmarks: list[Bookmark]
#     arquivos_processados: list[str]


# class BuscarBookmarks:
#     """Caso de uso: localizar e ler bookmarks em uma pasta, via uma `RepositorioFavoritos`."""

#     def __init__(self, repositorio: RepositorioFavoritos) -> None:
#         self._repositorio = repositorio

#     def executar(self, pasta: Path) -> ResultadoBusca:
#         """Executa a busca. Lança `PastaInvalidaError` se `pasta` não existir ou não for diretório."""
#         pasta_valida = self._validar_pasta(pasta)
#         arquivos = self._repositorio.descobrir_arquivos(pasta_valida)
#         bookmarks: list[Bookmark] = []
#         for arquivo in arquivos:
#             bookmarks.extend(self._repositorio.ler_bookmarks(arquivo))
#         return ResultadoBusca(
#             bookmarks=bookmarks,
#             arquivos_processados=[str(a) for a in arquivos],
#         )

#     @staticmethod
#     def _validar_pasta(pasta: Path) -> Path:
#         """Resolve `pasta` para caminho absoluto e garante que é um diretório existente."""
#         pasta_absoluta = pasta.expanduser().resolve()
#         if not pasta_absoluta.is_dir():
#             raise PastaInvalidaError(f"Pasta inválida ou inexistente: {pasta_absoluta}")
#         return pasta_absoluta
