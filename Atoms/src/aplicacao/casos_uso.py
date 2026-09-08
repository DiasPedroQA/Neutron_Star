# Atoms/src/aplicacao/casos_uso.py
# pylint: disable=broad-exception-caught, too-few-public-methods, too-many-locals

"""Módulo contendo as implementações de Casos de Uso do App Neutron Star."""

import os
from pathlib import Path
from collections.abc import Generator

from ..dominio.excecoes import PathInseguroError, DiretorioInexistenteError
from .portas import (
    BuscadorPort,
    LeitorHTMLPort,
    EscritorPort,
    GerenciadorSistemaPort,
    ParserPort,
)


def _is_safe_path(caminho_input: str | Path) -> bool:
    """Verifica se o caminho está restrito estritamente à Home do usuário (~/).

    Garante que qualquer caminho manipulado esteja contido dentro do diretório
    pessoal, evitando ataques e acessos maliciosos do tipo Path Traversal.
    """
    try:
        caminho_resolvido: Path = Path(caminho_input).expanduser().resolve()
        home_resolvido: Path = Path.home().resolve()
        return caminho_resolvido == home_resolvido or caminho_resolvido.is_relative_to(
            home_resolvido
        )
    except Exception:  # noqa: BLE001
        return False


class ObterInfoSistemaUseCase:
    """Caso de Uso para coletar os metadados e atalhos de sistema do usuário."""

    def __init__(self, gerenciador_sistema: GerenciadorSistemaPort) -> None:
        """Inicializa o caso de uso com seu respectivo adaptador de porta."""
        self._gerenciador_sistema: GerenciadorSistemaPort = gerenciador_sistema

    def executar(self) -> dict:
        """Executa a coleta de informações e atalhos sugeridos do S.O."""
        return self._gerenciador_sistema.obter_informacoes_so()


class EscanearDiretorioUseCase:
    """Caso de Uso para realizar a varredura profunda de arquivos do disco."""

    def __init__(self, buscador: BuscadorPort) -> None:
        """Inicializa o caso de uso com o buscador físico configurado."""
        self._buscador: BuscadorPort = buscador

    def executar(self, caminho_str: str) -> dict:
        """Valida a segurança do caminho e executa o escaneamento do disco."""
        caminho = Path(caminho_str)

        # 🛡️ Aplicação da barreira de segurança Path Traversal
        if not _is_safe_path(caminho_input=caminho):
            raise PathInseguroError(caminho=caminho_str)

        if not self._buscador.validar_pasta(caminho):
            raise DiretorioInexistenteError(caminho=caminho_str)

        return self._buscador.escanear(caminho)


class ConverterFavoritosLoteUseCase:
    """Caso de Uso para coordenar o pipeline de conversão de múltiplos arquivos."""

    def __init__(
        self,
        leitor: LeitorHTMLPort,
        parser: ParserPort,
        escritor: EscritorPort,
    ) -> None:
        """Inicializa as portas necessárias para leitura, parse e escrita."""
        self._leitor: LeitorHTMLPort = leitor
        self._parser: ParserPort = parser
        self._escritor: EscritorPort = escritor

    def executar_com_progresso(
        self, arquivos_selecionados: list[str], extensao_destino: str
    ) -> Generator[dict, None, None]:
        """Executa a conversão arquivo por arquivo com stream de progresso real.

        Yielda pacotes de status compatíveis com Server-Sent Events (SSE).
        """
        total: int = len(arquivos_selecionados)
        arquivos_convertidos: list[dict[str, str | int]] = []
        erros: list[dict[str, str]] = []

        for index, arq_str in enumerate(arquivos_selecionados):
            caminho_original: Path = Path(arq_str)
            nome_arquivo: str = caminho_original.name

            # 🛡️ Validação de segurança individual do arquivo
            if not _is_safe_path(caminho_input=caminho_original):
                erros.append(
                    {
                        "arquivo": nome_arquivo,
                        "erro": "Acesso proibido: O arquivo está em local inseguro.",
                    }
                )
                progresso = int(((index + 1) / total) * 100)
                yield {
                    "progresso": progresso,
                    "arquivo_atual": nome_arquivo,
                    "concluido": (index + 1) == total,
                    "sucesso": len(arquivos_convertidos) > 0,
                    "arquivos_convertidos": arquivos_convertidos,
                    "erros": erros,
                }
                continue

            try:
                # 1. Lê o arquivo HTML (Camada física do disco)
                html_conteudo: str = self._leitor.ler_arquivo(caminho=caminho_original)

                if favoritos := self._parser.extrair_favoritos(html_conteudo):
                    # Serializa as entidades antes de gravar
                    dados_serializaveis: list[dict[str, str]] = [fav.to_dict() for fav in favoritos]

                    # 3. Executa a gravação física utilizando a estratégia correta
                    caminho_gravado: str = self._escritor.salvar_lote(
                        caminho_original=caminho_original,
                        dados=dados_serializaveis,
                        extensao=extensao_destino,
                    )

                    arquivos_convertidos.append(
                        {
                            "origem": nome_arquivo,
                            "destino": os.path.basename(caminho_gravado),
                            "total_links": len(favoritos),
                        }
                    )

                else:
                    erros.append(
                        {
                            "arquivo": nome_arquivo,
                            "erro": "Nenhum favorito válido foi encontrado no HTML.",
                        }
                    )
            except Exception as e:  # noqa: BLE001
                erros.append({"arquivo": nome_arquivo, "erro": f"Falha no processamento: {e!s}"})

            # Calcula e envia a atualização de progresso corrente
            progresso = int(((index + 1) / total) * 100)
            yield {
                "progresso": progresso,
                "arquivo_atual": nome_arquivo,
                "concluido": (index + 1) == total,
                "sucesso": len(arquivos_convertidos) > 0,
                "arquivos_convertidos": arquivos_convertidos,
                "erros": erros,
            }
