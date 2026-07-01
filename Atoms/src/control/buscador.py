"""Buscador parametrizável por metadados do sistema de arquivos.

Fornece classes para definir critérios de busca e executar a varredura
recursiva de diretórios, respeitando a configuração injetada via ConfigApp.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from ..model.arquivo_info import ItemArquivo
from ..model.configuracoes import ConfigApp
from ..model.diretorio_info import ItemDiretorio
from ..model.item_neutro import ItemBase
from ..model.resultado_busca import ResultadoBusca
from ..tools.system_tools import listar_diretorio


@dataclass
class FiltroTexto:
    """Filtro para qualquer string (nome ou caminho).

    Parâmetros:
        comeca_com: str | None → o texto deve iniciar com este valor.
        termina_com: str | None → o texto deve terminar com este valor.
        contem: str | None → o texto deve conter esta substring.
        regex: str | None → expressão regular aplicada via re.search.
        case_sensitive: bool → se falso, a comparação ignora maiúsculas/minúsculas.
    """

    comeca_com: str | None = None
    termina_com: str | None = None
    contem: str | None = None
    regex: str | None = None
    case_sensitive: bool = True

    def aplica(self, texto: str) -> bool:
        """Verifica se 'texto' atende a todos os critérios definidos.

        Args:
            texto: String a ser testada (nome do item ou caminho completo).

        Returns:
            True se o texto satisfaz todos os campos não nulos.
        """
        if not self.case_sensitive:
            texto = texto.lower()
            comeca: str | None = self.comeca_com.lower() if self.comeca_com else None
            termina: str | None = self.termina_com.lower() if self.termina_com else None
            contem: str | None = self.contem.lower() if self.contem else None
            flags: re.RegexFlag | int = re.IGNORECASE
        else:
            comeca, termina, contem = self.comeca_com, self.termina_com, self.contem
            flags = 0

        if comeca is not None and not texto.startswith(comeca):
            return False
        if termina is not None and not texto.endswith(termina):
            return False
        if contem is not None and contem not in texto:
            return False
        return not (self.regex is not None and not re.search(pattern=self.regex, string=texto, flags=flags))


@dataclass
class CriteriosBusca:
    """Define os filtros aplicáveis durante uma busca.

    Atributos:
        consulta (str): atalho para filtro_nome.contem (usado se filtro_nome não definido).
        filtro_nome (FiltroTexto | None): filtro detalhado para o nome do item.
        filtro_caminho (FiltroTexto | None): filtro detalhado para o caminho completo.
        padrao_glob (str | None): padrão glob para listagem rápida (ex.: "*.pdf").
        tamanho_min (int | None): tamanho mínimo em bytes (arquivos).
        tamanho_max (int | None): tamanho máximo em bytes (arquivos).
        modificado_apos (datetime | None): data mínima de modificação.
        modificado_antes (datetime | None): data máxima de modificação.
        extensoes (list[str] | None): extensões desejadas (ex.: ['.py', '.txt']).
        tipos_mime (list[str] | None): tipos MIME aceitos.
        apenas_legiveis (bool): somente itens legíveis.
        apenas_gravaveis (bool): somente itens graváveis.
        apenas_executaveis (bool): somente itens executáveis.
        incluir_diretorios (bool): se diretórios devem aparecer nos resultados.
        incluir_arquivos (bool): se arquivos devem aparecer nos resultados.
    """

    consulta: str = ""
    filtro_nome: FiltroTexto | None = None
    filtro_caminho: FiltroTexto | None = None
    padrao_glob: str | None = None
    tamanho_min: int | None = None
    tamanho_max: int | None = None
    modificado_apos: datetime | None = None
    modificado_antes: datetime | None = None
    extensoes: list[str] | None = None
    tipos_mime: list[str] | None = None
    apenas_legiveis: bool = False
    apenas_gravaveis: bool = False
    apenas_executaveis: bool = False
    incluir_diretorios: bool = False
    incluir_arquivos: bool = True

    def __post_init__(self):
        """Garante que o atalho 'consulta' vire um FiltroTexto se nenhum filtro explícito for dado."""
        if self.consulta and self.filtro_nome is None:
            self.filtro_nome = FiltroTexto(contem=self.consulta)


class BuscadorSistemaArquivos:
    """Realiza buscas recursivas no sistema de arquivos usando metadados.

    Depende de um objeto ConfigApp para limites e comportamentos.
    A busca usa apenas os metadados já extraídos, sem abrir conteúdo de arquivos.

    Uso típico:
        config = ConfigApp(...)
        buscador = BuscadorSistemaArquivos(config)
        criterios = CriteriosBusca(...)
        resultado = buscador.buscar(Path.home(), criterios)
    """

    def __init__(self, config: ConfigApp) -> None:
        """Inicializa o buscador com a configuração fornecida.

        Args:
            config: Instância de ConfigApp com parâmetros adaptados ao SO.
        """
        self.config: ConfigApp = config
        self._raiz_busca: Path | None = None

    def buscar(self, raiz: Path, criterios: CriteriosBusca) -> ResultadoBusca:
        """Executa a busca a partir do diretório raiz.

        Args:
            raiz: Ponto de partida da varredura.
            criterios: Critérios que os itens devem satisfazer.

        Returns:
            ResultadoBusca contendo os itens encontrados e estatísticas.
        """
        inicio: float = time.time()

        # Ajusta sensibilidade de case nos filtros, se necessário
        if not self.config.case_sensitive:
            if criterios.filtro_nome is not None:
                criterios.filtro_nome.case_sensitive = False
            if criterios.filtro_caminho is not None:
                criterios.filtro_caminho.case_sensitive = False

        itens: list[ItemBase] = []
        self._raiz_busca = raiz
        self._percorrer(atual=raiz, criterios=criterios, resultados=itens, profundidade=0)
        tempo: float = time.time() - inicio

        return ResultadoBusca(
            consulta=criterios.consulta,
            itens=itens,
            total_encontrado=len(itens),
            tempo_execucao=tempo,
            raiz_busca=raiz,
            criterios=criterios,
        )

    def _percorrer(
        self,
        atual: Path,
        criterios: CriteriosBusca,
        resultados: list[ItemBase],
        profundidade: int,
    ) -> None:
        """Varre recursivamente a árvore de diretórios.

        Args:
            atual: Diretório sendo visitado.
            criterios: Critérios da busca.
            resultados: Lista onde os itens aceitos são acumulados.
            profundidade: Nível atual de profundidade.
        """
        if self.config.profundidade_maxima != -1 and profundidade > self.config.profundidade_maxima:
            return

        try:
            conteudo: list[ItemBase] = listar_diretorio(
                caminho=atual,
                raiz_busca=self._raiz_busca,
                seguir_symlinks=self.config.seguir_symlinks,
                padrao_glob=criterios.padrao_glob,
            )
        except PermissionError:
            return

        for item in conteudo:
            self._processar_item(item=item, criterios=criterios, resultados=resultados, profundidade=profundidade)

    def _processar_item(
        self,
        item: ItemBase,
        criterios: CriteriosBusca,
        resultados: list[ItemBase],
        profundidade: int,
    ) -> None:
        """Aplica filtros e encaminha o item para o resultado ou para a recursão.

        Args:
            item: Item a ser processado (arquivo ou diretório).
            criterios: Critérios da busca.
            resultados: Lista onde os itens aceitos são acumulados.
            profundidade: Nível atual de profundidade.
        """
        # Exclusão por oculto e por padrões
        if self.config.ignorar_ocultos and item.oculto:
            return
        if self._excluido(nome=item.nome):
            return

        # Verifica se o item deve ser incluído no resultado
        if isinstance(item, ItemArquivo) and criterios.incluir_arquivos:
            if self._item_atende(item=item, criterios=criterios):
                resultados.append(item)
        elif isinstance(item, ItemDiretorio):
            if criterios.incluir_diretorios and self._item_atende(item=item, criterios=criterios):
                resultados.append(item)
            # Recursão apenas se o diretório é listável
            if item.listavel:
                self._percorrer(
                    atual=item.caminho,
                    criterios=criterios,
                    resultados=resultados,
                    profundidade=profundidade + 1,
                )

    def _item_atende(self, item: ItemBase, criterios: CriteriosBusca) -> bool:
        """Verifica se um item (arquivo ou diretório) atende aos critérios comuns.

        Args:
            item: Item a ser verificado.
            criterios: Critérios da busca.

        Returns:
            True se o item satisfaz todos os critérios aplicáveis.
        """
        # Filtros de texto
        if criterios.filtro_nome is not None and not criterios.filtro_nome.aplica(item.nome):
            return False
        if criterios.filtro_caminho is not None and not criterios.filtro_caminho.aplica(str(item.caminho)):
            return False

        # Permissões comuns
        if criterios.apenas_legiveis and not item.legivel:
            return False
        if criterios.apenas_gravaveis and not item.gravavel:
            return False
        if criterios.apenas_executaveis and not self._verificar_executavel(item):
            return False

        # Critérios específicos de arquivo
        return not (isinstance(item, ItemArquivo) and not self._arquivo_atende_especifico(item, criterios))

    def _arquivo_atende_especifico(self, arquivo: ItemArquivo, criterios: CriteriosBusca) -> bool:
        """Aplica critérios exclusivos de arquivos (tamanho, data, MIME, extensão).

        Args:
            arquivo: ItemArquivo a ser avaliado.
            criterios: Critérios da busca.

        Returns:
            True se o arquivo satisfaz os critérios específicos.
        """
        if criterios.tamanho_min is not None and (arquivo.tamanho is None or arquivo.tamanho < criterios.tamanho_min):
            return False
        if criterios.tamanho_max is not None and (arquivo.tamanho is None or arquivo.tamanho > criterios.tamanho_max):
            return False
        if criterios.modificado_apos is not None and (
            arquivo.modificado is None or arquivo.modificado < criterios.modificado_apos
        ):
            return False
        if criterios.modificado_antes is not None and (
            arquivo.modificado is None or arquivo.modificado > criterios.modificado_antes
        ):
            return False
        if criterios.extensoes is not None and arquivo.sufixo.lower() not in [
            ext.lower() for ext in criterios.extensoes
        ]:
            return False
        return criterios.tipos_mime is None or arquivo.tipo_mime in criterios.tipos_mime

    def _verificar_executavel(self, item: ItemBase) -> bool:
        """Determina se um item é considerado executável conforme a configuração.

        No Linux/macOS utiliza o campo 'executavel' (permissão POSIX).
        No Windows utiliza a extensão do arquivo.

        Args:
            item: Item a ser verificado.

        Returns:
            True se o item atende à política de executabilidade.
        """
        if self.config.executavel_por_extensao:
            if isinstance(item, ItemArquivo):
                return item.sufixo.lower() in [ext.lower() for ext in self.config.extensoes_executaveis]
            # Diretórios não são executáveis por extensão
            return False
        return item.executavel

    def _excluido(self, nome: str) -> bool:
        """Verifica se o nome do item casa com algum padrão de exclusão (regex).

        Args:
            nome: Nome do arquivo/diretório.

        Returns:
            True se o nome deve ser excluído.
        """
        return any(re.search(padrao, nome) for padrao in self.config.padroes_exclusao)
