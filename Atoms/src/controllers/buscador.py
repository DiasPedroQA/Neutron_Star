"""Buscador de arquivos no sistema de arquivos usando rglob e metadados.

Fornece uma classe para buscar arquivos recursivamente com filtros
baseados em padrões glob, regex e atributos.
"""

from collections.abc import Iterable
from logging import Logger
from pathlib import Path
from re import Pattern

from src.models.arquivo import Arquivo, Permissoes
from src.utils.logger import get_logger
from src.utils.system_tools import (
    MetadadosArquivo,
    _caminhos_visiveis,
    _compilar_regex,
    _verificar_oculto,
    metadados_simples,
)

# Logger específico para este módulo
logger: Logger = get_logger(nome=__name__)


class Buscador:
    """Buscador de arquivos com prefixo obrigatório e data opcional."""

    def __init__(
        self,
        prefixo: str | Iterable[str],
        data: str | None = None,
    ) -> None:
        """Inicializa o buscador.

        `prefixo` aceita uma string única ou um iterável de aliases
        equivalentes (ex.: `["favoritos", "bookmarks"]`), permitindo buscar
        pelo mesmo padrão lógico em pt-BR e en-US simultaneamente.
        """
        self.prefixo: str | Iterable[str] = prefixo
        self.data: str | None = data
        self.raiz: Path = Path.home()

        logger.info("Buscador inicializado com prefixo='%s', data='%s'", prefixo, data)
        logger.debug("Raiz da busca: %s", self.raiz)

        self.regex_buscador: Pattern[str] = _compilar_regex(
            prefixo=self.prefixo,
            data=self.data,
            case_sensitive=True,
        )
        logger.debug("Regex compilada: %s", self.regex_buscador.pattern)

    def _validar_caminho(self, caminho: Path) -> bool:
        """Valida se o caminho é um arquivo válido, não oculto e com nome compatível."""
        logger.debug("Validando caminho: %s", caminho)

        # Verifica se é arquivo
        if not caminho.is_file():
            logger.debug("  ✗ Não é um arquivo (ou não existe)")
            return False

        # Verifica se é oculto
        if _verificar_oculto(caminho=caminho, raiz_busca=self.raiz):
            logger.debug("  ✗ É oculto (ignorado)")
            return False

        # Verifica regex
        if self.regex_buscador.match(caminho.name) is None:
            logger.debug("  ✗ Nome não corresponde à regex")
            return False

        logger.debug("  ✓ Passou em todas as validações")
        return True

    def _dict_para_arquivo(self, dados: MetadadosArquivo | None) -> Arquivo | None:
        """Converte um dicionário de metadados (MetadadosArquivo) para um objeto Arquivo."""
        if dados is None:
            logger.warning("Dados vazios para conversão")
            return None

        try:
            permissoes = Permissoes(
                legivel=dados["permissoes"]["legivel"],
                gravavel=dados["permissoes"]["gravavel"],
                executavel=dados["permissoes"]["executavel"],
            )

            arquivo = Arquivo(
                caminho=dados["caminho"],
                tamanho=dados["tamanho"],
                modificado=dados["modificado"],
                permissoes=permissoes,
                oculto=dados["oculto"],
                tipo_mime=dados.get("tipo_mime"),
                hash_checksum=dados.get("hash_checksum"),
            )

            logger.debug("  ✓ Arquivo convertido: %s", arquivo.caminho.name)
            return arquivo

        except KeyError as e:
            logger.error("Erro ao converter dict para Arquivo: chave ausente %s", e)
            return None
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Erro inesperado na conversão: %s", e, exc_info=True)
            return None

    def buscar_arquivos(self) -> list[Arquivo]:
        """Executa a busca e retorna uma lista de objetos Arquivo."""
        logger.info("Iniciando busca a partir de: %s", self.raiz)

        # Percorre a árvore podando diretórios ocultos ANTES de descer
        # neles (ver system_tools._caminhos_visiveis). A extensão é
        # filtrada depois, pela regex, que já é a fonte única de verdade
        # sobre quais extensões são aceitas.
        todos_caminhos: list[Path] = list(_caminhos_visiveis(raiz=self.raiz))
        logger.info("Total de caminhos visíveis encontrados: %d", len(todos_caminhos))

        # Aplica os filtros
        caminhos_validos: list[Path] = list(filter(self._validar_caminho, todos_caminhos))
        logger.info("Caminhos após validações: %d", len(caminhos_validos))

        if not caminhos_validos:
            logger.warning(
                "Nenhum caminho válido encontrado. Verifique:\n  - Prefixo: %s\n  - Data: %s\n  - Raiz: %s",
                self.prefixo,
                self.data,
                self.raiz,
            )
            return []

        # Extrai metadados e converte para Arquivo
        resultados: list[Arquivo] = []
        total_arquivos: int = len(caminhos_validos)

        for idx, caminho in enumerate(caminhos_validos, 1):
            logger.debug("Processando [%d/%d]: %s", idx, total_arquivos, caminho.name)

            dados: MetadadosArquivo | None = metadados_simples(caminho=caminho)
            if dados is not None:
                arquivo: Arquivo | None = self._dict_para_arquivo(dados=dados)
                if arquivo is not None:
                    resultados.append(arquivo)
                    logger.debug("  ✓ Adicionado à lista de resultados")
            else:
                logger.warning("  ✗ Falha ao extrair metadados de: %s", caminho)

        logger.info("Busca concluída. Total de arquivos encontrados: %d", len(resultados))
        return resultados
