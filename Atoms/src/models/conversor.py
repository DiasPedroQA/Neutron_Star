# Atoms/src/models/conversor.py
# pylint: disable=too-few-public-methods, broad-exception-caught, too-many-locals

"""Módulo de negócio para conversão e validação em lote de favoritos."""

from collections.abc import Generator
from pathlib import Path

from ..utils.leitor import LeitorLocal
from ..utils.parser import ParserBeautifulSoup
from .buscador import BuscadorLocal, GerenciadorSistemaLocal
from .entidades import (
    ArquivoConvertido,
    ErroConversao,
    FavoritoDict,
    InfoSistema,
    ResultadoEscaneamento,
    StatusConversao,
)
from .escritores import EscritorLocal
from .excecoes import (
    DiretorioInexistenteError,
    ExtensaoInvalidaError,
    PathInseguroError,
)


class ConversorService:
    """Serviço de negócio que coordena o fluxo de varredura e conversão."""

    def __init__(
        self,
        gerenciador: GerenciadorSistemaLocal | None = None,
        buscador: BuscadorLocal | None = None,
        leitor: LeitorLocal | None = None,
        parser: ParserBeautifulSoup | None = None,
        escritor: EscritorLocal | None = None,
    ) -> None:
        """Recebe colaboradores opcionais para manter o domínio testável."""
        self.gerenciador = gerenciador or GerenciadorSistemaLocal()
        self.buscador = buscador or BuscadorLocal()
        self.leitor = leitor or LeitorLocal()
        self.parser = parser or ParserBeautifulSoup()
        self.escritor = escritor or EscritorLocal()

    def validar_seguranca_caminho(self, caminho: Path) -> Path:
        """Garante que o caminho está contido na pasta Home (contra Path Traversal)."""
        caminho_resolvido: Path = caminho.expanduser().resolve()
        home: Path = Path.home().resolve()
        try:
            caminho_resolvido.relative_to(home)
        except ValueError as erro:
            raise PathInseguroError(caminho=str(caminho)) from erro
        return caminho_resolvido

    def obter_info_sistema(self) -> InfoSistema:
        """Obtém informações do ambiente e atalhos rápidos."""
        return self.gerenciador.obter_informacoes_so()

    def escanear(
        self,
        caminho_str: str = "~/",
        extensao: str = ".html",
        profundidade: int = 5,
    ) -> ResultadoEscaneamento:
        """Valida o caminho e executa a varredura."""
        caminho = Path(caminho_str)
        caminho_seguro: Path = self.validar_seguranca_caminho(caminho=caminho)

        if not self.buscador.validar_pasta(caminho=caminho_seguro):
            raise DiretorioInexistenteError(caminho=caminho_str)

        return self.buscador.escanear(
            caminho=caminho_seguro,
            extensao=extensao,
            profundidade=profundidade,
        )

    def converter_com_progresso(
        self,
        arquivos_selecionados: list[str],
        extensao_destino: str,
        pasta_saida: str | None = None,
    ) -> Generator[StatusConversao, None, None]:
        """Executa a conversão em lote emitindo eventos de progresso."""
        formato: str = extensao_destino.lower().lstrip(".")
        if formato not in self.escritor.FORMATADORES:
            raise ExtensaoInvalidaError(f"Formato '{extensao_destino}' não suportado.")

        total_arquivos: int = len(arquivos_selecionados)
        if not total_arquivos:
            yield {
                "progresso": 100,
                "arquivo_atual": "",
                "arquivos_convertidos": [],
                "erros": [],
                "concluido": True,
                "sucesso": True,
            }
            return

        arquivos_convertidos: list[ArquivoConvertido] = []
        erros: list[ErroConversao] = []
        pasta_saida_path: Path | None = (
            self.validar_seguranca_caminho(caminho=Path(pasta_saida)) if pasta_saida else None
        )
        destinos_gerados: set[Path] = set()

        for indice, arq_str in enumerate(arquivos_selecionados, start=1):
            progresso_atual: int = int((indice - 1) / total_arquivos * 100)
            yield {
                "progresso": progresso_atual,
                "arquivo_atual": Path(arq_str).name,
                "arquivos_convertidos": list(arquivos_convertidos),
                "erros": list(erros),
                "concluido": False,
                "sucesso": True,
            }

            try:
                caminho_seguro: Path = self.validar_seguranca_caminho(caminho=Path(arq_str))
                destino: Path = self.escritor.gerar_caminho_destino(
                    caminho_original=caminho_seguro,
                    extensao=formato,
                    pasta_saida=pasta_saida_path,
                )
                if destino in destinos_gerados:
                    raise FileExistsError(f"Destino repetido no lote: {destino}")
                conteudo: str = self.leitor.ler_arquivo(caminho=caminho_seguro)
                favoritos: list[dict[str, str]] = self.parser.extrair_favoritos(
                    html_conteudo=conteudo
                )

                dados_dict: list[FavoritoDict] = []
                for fav in favoritos:
                    item_fav: FavoritoDict = {
                        "titulo": fav.get("titulo", "**Sem título**"),
                        "url": fav.get("url", "**Sem URL**"),
                        "pasta": fav.get("pasta", "**Sem pasta**"),
                        "data_adicao": fav.get("data_adicao", "**Sem data**"),
                    }
                    dados_dict.append(item_fav)

                destino_str: str = self.escritor.salvar_lote(
                    caminho_original=caminho_seguro,
                    dados=dados_dict,
                    extensao=formato,
                    pasta_saida=pasta_saida_path,
                )
                destinos_gerados.add(destino)

                item_convertido: ArquivoConvertido = {
                    "arquivo_origem": str(caminho_seguro),
                    "arquivo_destino": destino_str,
                    "total_links": len(favoritos),
                }
                arquivos_convertidos.append(item_convertido)

            except Exception as erro:
                item_erro: ErroConversao = {
                    "arquivo": arq_str,
                    "erro": str(erro),
                }
                erros.append(item_erro)

        yield {
            "progresso": 100,
            "arquivo_atual": "",
            "arquivos_convertidos": arquivos_convertidos,
            "erros": erros,
            "concluido": True,
            "sucesso": not erros,
        }
