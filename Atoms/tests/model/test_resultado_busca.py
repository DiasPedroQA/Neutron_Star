"""Testes para o modelo ResultadoBusca.

Verifica a criação, filtragem por tipo, serialização e manipulação
de metadados de resultados de busca.
"""

from pathlib import Path

from src.models.arquivo_info import ItemArquivo
from src.models.diretorio_info import ItemDiretorio
from src.models.resultado_busca import ResultadoBusca


class TestResultadoBusca:
    """Suite de testes para a classe ResultadoBusca."""

    def test_criacao_basica(self) -> None:
        """Verifica a criação com valores mínimos."""
        resultado = ResultadoBusca(consulta="teste")
        assert resultado.consulta == "teste"
        assert resultado.itens == []
        assert resultado.total_encontrado == 0
        assert resultado.tempo_execucao == 0.0
        assert resultado.raiz_busca is None
        assert resultado.criterios is None
        assert not resultado.metadados

    def test_criacao_com_itens(self) -> None:
        """Verifica a criação com uma lista de itens."""
        item1 = ItemArquivo(caminho=Path("/tmp/a.txt"))
        item2 = ItemDiretorio(caminho=Path("/tmp/pasta"))
        resultado = ResultadoBusca(
            consulta="arquivos",
            itens=[item1, item2],
            total_encontrado=2,
            tempo_execucao=0.5,
            raiz_busca=Path("/tmp"),
        )
        assert resultado.itens == [item1, item2]
        assert resultado.total_encontrado == 2
        assert resultado.tempo_execucao == 0.5
        assert resultado.raiz_busca == Path("/tmp")

    def test_filtrar_por_tipo_arquivo(self) -> None:
        """Filtra apenas itens do tipo ItemArquivo."""
        arquivo1 = ItemArquivo(caminho=Path("/tmp/a.txt"))
        arquivo2 = ItemArquivo(caminho=Path("/tmp/b.txt"))
        diretorio = ItemDiretorio(caminho=Path("/tmp/pasta"))
        resultado = ResultadoBusca(
            consulta="todos",
            itens=[arquivo1, diretorio, arquivo2],
            total_encontrado=3,
        )
        filtrado: ResultadoBusca = resultado.filtrar_por_tipo(tipo=ItemArquivo)
        assert filtrado.itens == [arquivo1, arquivo2]
        assert filtrado.total_encontrado == 2
        assert filtrado.consulta == "todos"
        assert filtrado.tempo_execucao == resultado.tempo_execucao

    def test_filtrar_por_tipo_diretorio(self) -> None:
        """Filtra apenas itens do tipo ItemDiretorio."""
        arquivo = ItemArquivo(caminho=Path("/tmp/a.txt"))
        diretorio1 = ItemDiretorio(caminho=Path("/tmp/pasta1"))
        diretorio2 = ItemDiretorio(caminho=Path("/tmp/pasta2"))
        resultado = ResultadoBusca(
            consulta="pastas",
            itens=[arquivo, diretorio1, diretorio2],
            total_encontrado=3,
        )
        filtrado: ResultadoBusca = resultado.filtrar_por_tipo(tipo=ItemDiretorio)
        assert filtrado.itens == [diretorio1, diretorio2]
        assert filtrado.total_encontrado == 2

    def test_filtrar_por_tipo_sem_correspondencias(self) -> None:
        """Filtra por tipo que não existe na lista, resultando em lista vazia."""
        arquivo = ItemArquivo(caminho=Path("/tmp/a.txt"))
        resultado = ResultadoBusca(consulta="vazio", itens=[arquivo])
        filtrado: ResultadoBusca = resultado.filtrar_por_tipo(tipo=ItemDiretorio)
        assert filtrado.itens == []
        assert filtrado.total_encontrado == 0

    def test_filtrar_por_tipo_preserva_metadados(self) -> None:
        """Verifica que os metadados (tempo, consulta, etc.) são preservados na cópia."""
        resultado = ResultadoBusca(
            consulta="exemplo",
            itens=[ItemArquivo(caminho=Path("/tmp/a.txt"))],
            total_encontrado=1,
            tempo_execucao=2.5,
            metadados={"extra": "info"},
        )
        filtrado: ResultadoBusca = resultado.filtrar_por_tipo(tipo=ItemArquivo)
        assert filtrado.consulta == "exemplo"
        assert filtrado.tempo_execucao == 2.5
        assert filtrado.metadados == {"extra": "info"}
        # raiz_busca e criterios são None por padrão, preservados
        assert filtrado.raiz_busca is None

    def test_para_dict(self) -> None:
        """Verifica a serialização completa do resultado."""
        arquivo = ItemArquivo(
            caminho=Path("/tmp/a.txt"),
            tamanho=100,
            legivel=True,
        )
        diretorio = ItemDiretorio(
            caminho=Path("/tmp/pasta"),
            executavel=True,
        )
        resultado = ResultadoBusca(
            consulta="teste",
            itens=[arquivo, diretorio],
            total_encontrado=2,
            tempo_execucao=1.23,
            metadados={"chave": "valor"},
        )
        dados: dict[
            str, str | list[dict[str, str | int | bool | None]] | int | float | dict[str, str | int | float]
        ] = resultado.para_dict()

        # Estrutura do dicionário
        assert dados["consulta"] == "teste"
        assert dados["total_encontrado"] == 2
        assert dados["tempo_execucao"] == 1.23
        assert dados["metadados"] == {"chave": "valor"}

        # Itens serializados (verifica alguns campos)
        itens: str | list[dict[str, str | int | bool | None]] | int | float | dict[str, str | int | float] = dados[
            "itens"
        ]
        assert len(itens) == 2
        assert itens[0]["caminho"] == "/tmp/a.txt"
        assert itens[0]["eh_diretorio"] is False
        assert itens[1]["caminho"] == "/tmp/pasta"
        assert itens[1]["eh_diretorio"] is True

    def test_metadados_personalizados(self) -> None:
        """Verifica que metadados podem ser atribuídos e mantidos."""
        resultado = ResultadoBusca(consulta="meta")
        resultado.metadados["usuario"] = "pedro"
        resultado.metadados["score"] = 0.95
        assert resultado.metadados["usuario"] == "pedro"
        assert resultado.metadados["score"] == 0.95

    def test_total_encontrado_independente_da_lista(self) -> None:
        """total_encontrado pode ser diferente de len(itens) (ex: paginação)."""
        resultado = ResultadoBusca(
            consulta="paginada",
            itens=[ItemArquivo(caminho=Path("/tmp/a.txt"))],
            total_encontrado=100,  # simula paginação
        )
        assert len(resultado.itens) == 1
        assert resultado.total_encontrado == 100

    def test_raiz_busca_e_criterios_opcionais(self) -> None:
        """raiz_busca e criterios podem ser None ou definidos."""
        resultado1 = ResultadoBusca(consulta="sem_raiz")
        assert resultado1.raiz_busca is None
        assert resultado1.criterios is None

        # Simula um objeto de critérios (qualquer)
        criterios_mock: dict[str, str] = {"filtro": "nome"}
        resultado2 = ResultadoBusca(
            consulta="com_raiz",
            raiz_busca=Path("/home"),
            criterios=criterios_mock,
        )
        assert resultado2.raiz_busca == Path("/home")
        assert resultado2.criterios == criterios_mock
