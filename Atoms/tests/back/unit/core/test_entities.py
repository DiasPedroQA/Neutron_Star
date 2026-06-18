# pylint: disable=redefined-outer-name, unused-argument

"""Testes unitários — Camada 1: entities (Atoms/backend/core/entidades).

Filosofia TDD aplicada aqui:
    - Cada teste cobre UM comportamento observável.
    - Zero I/O, zero disco, zero mocks — entidades puras.
    - Nome do teste = documentação viva do comportamento esperado.
    - Ordem de execução: ModeloArquivo → ModeloPasta → ModeloSistemaOperacional.

Ciclo Red-Green-Blue:
    Red   → rodar este arquivo antes de implementar e ver falhar pelo motivo certo.
    Green → implementar o mínimo nas entities para cada teste passar.
    Blue  → refatorar sem quebrar nenhum teste verde.

Avisos de tipagem intencionais:
    Alguns testes passam tipos errados propositalmente para verificar que a entity
    rejeita entradas inválidas. Esses casos usam `# type: ignore[arg-type]` para
    silenciar o mypy sem esconder o comportamento testado.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from backend.core.entidades.entidade_arquivo import ModeloArquivo
from backend.core.entidades.entidade_diretorio import ModeloPasta
from backend.core.entidades.entidade_processamento import (
    EstatisticasProcessamento,
    ResultadoProcessamento,
)
from backend.core.entidades.entidade_sistema_operacional import (
    ModeloSistemaOperacional,
)

# ===========================================================================
# Fixtures compartilhadas neste módulo
# ===========================================================================


@pytest.fixture()
def pasta_raiz(tmp_path: Path) -> ModeloPasta:
    """Retorna um ModeloPasta raiz sem pai para uso nos testes."""
    return ModeloPasta(nome_pasta="home", caminho_absoluto=tmp_path, pasta_pai=None)


@pytest.fixture()
def caminho_arquivo_html(tmp_path: Path) -> Path:
    """Retorna um caminho temporário para um arquivo HTML fictício."""
    return tmp_path / "bookmarks.html"


# ===========================================================================
# ModeloArquivo
# ===========================================================================


class TestModeloArquivoCreation:
    """Testes de criação de instâncias de ModeloArquivo.

    Verifica que arquivos válidos são construídos corretamente e que
    configurações básicas de campos são aceitas.
    """

    def test_cria_com_campos_validos(self, caminho_arquivo_html: Path) -> None:
        """Garante que um ModeloArquivo é criado com todos os campos válidos.

        Este teste verifica que os atributos principais são preservados
        exatamente como fornecidos no construtor.
        """
        arq = ModeloArquivo(
            nome_arquivo="bookmarks.html",
            caminho_arquivo=caminho_arquivo_html,
            tamanho_arquivo_bytes=512,
            file_is_html=True,
        )
        assert arq.nome_arquivo == "bookmarks.html"
        assert arq.caminho_arquivo == caminho_arquivo_html
        assert arq.tamanho_arquivo_bytes == 512
        assert arq.file_is_html is True

    def test_cria_arquivo_nao_html(self, tmp_path: Path) -> None:
        """Garante que o modelo aceita arquivos marcados como não HTML.

        Verifica que a flag file_is_html pode ser falsa mesmo para
        caminhos com extensões arbitrárias.
        """
        arq = ModeloArquivo(
            nome_arquivo="dados.csv",
            caminho_arquivo=tmp_path / "dados.csv",
            tamanho_arquivo_bytes=256,
            file_is_html=False,
        )
        assert arq.file_is_html is False

    def test_tamanho_zero_e_valido(self, tmp_path: Path) -> None:
        """Garante que arquivos com tamanho zero são considerados válidos.

        Verifica que o campo de tamanho aceita o valor zero sem levantar exceções.
        """
        arq = ModeloArquivo(
            nome_arquivo="vazio.html",
            caminho_arquivo=tmp_path / "vazio.html",
            tamanho_arquivo_bytes=0,
            file_is_html=True,
        )
        assert arq.tamanho_arquivo_bytes == 0


class TestModeloArquivoValidation:
    """Testes de validação de campos do ModeloArquivo.

    Assegura que nomes, caminhos e tamanhos inválidos sejam rejeitados
    com os erros apropriados.
    """

    def test_nome_vazio_levanta_value_error(self, caminho_arquivo_html: Path) -> None:
        """Garante que nomes de arquivo vazios são rejeitados.

        Verifica se a criação com nome vazio dispara ValueError com mensagem adequada.
        """
        with pytest.raises(expected_exception=ValueError, match="nome"):
            ModeloArquivo(
                nome_arquivo="",
                caminho_arquivo=caminho_arquivo_html,
                tamanho_arquivo_bytes=100,
                file_is_html=True,
            )

    def test_nome_apenas_espacos_levanta_value_error(
        self, caminho_arquivo_html: Path
    ) -> None:
        """Garante que nomes contendo apenas espaços em branco são rejeitados.

        Verifica se o construtor dispara ValueError quando o nome do arquivo
        não contém caracteres visíveis.
        """
        with pytest.raises(expected_exception=ValueError, match="nome"):
            ModeloArquivo(
                nome_arquivo="   ",
                caminho_arquivo=caminho_arquivo_html,
                tamanho_arquivo_bytes=100,
                file_is_html=True,
            )

    def test_nome_inconsistente_com_caminho_levanta_value_error(
        self, tmp_path: Path
    ) -> None:
        """Garante que o nome informado deve ser consistente com o caminho do arquivo.

        Verifica se o modelo rejeita combinações em que o nome do arquivo
        não corresponde ao último componente do caminho.
        """
        with pytest.raises(expected_exception=ValueError, match="nome"):
            ModeloArquivo(
                nome_arquivo="outro_nome.html",
                caminho_arquivo=tmp_path / "bookmarks.html",
                tamanho_arquivo_bytes=100,
                file_is_html=True,
            )

    def test_tamanho_negativo_levanta_value_error(
        self, caminho_arquivo_html: Path
    ) -> None:
        """Garante que tamanhos de arquivo negativos são rejeitados.

        Verifica se o construtor dispara ValueError quando o tamanho fornecido
        é menor que zero.
        """
        with pytest.raises(expected_exception=ValueError, match="tamanho"):
            ModeloArquivo(
                nome_arquivo="bookmarks.html",
                caminho_arquivo=caminho_arquivo_html,
                tamanho_arquivo_bytes=-1,
                file_is_html=True,
            )

    def test_caminho_relativo_levanta_value_error(self) -> None:
        """Garante que caminhos relativos não são aceitos.

        Verifica se a entidade exige caminho absoluto e rejeita instâncias
        com Path relativo.
        """
        with pytest.raises(expected_exception=ValueError, match="absoluto"):
            ModeloArquivo(
                nome_arquivo="bookmarks.html",
                caminho_arquivo=Path("relative/bookmarks.html"),
                tamanho_arquivo_bytes=100,
                file_is_html=True,
            )

    def test_nome_com_barras_levanta_value_error(self, tmp_path: Path) -> None:
        """Garante que nomes de arquivo não podem conter barras.

        Verifica se o construtor dispara ValueError quando o nome contém
        separadores de diretório.
        """
        with pytest.raises(expected_exception=ValueError, match="barras"):
            ModeloArquivo(
                nome_arquivo="subdir/bookmarks.html",
                caminho_arquivo=tmp_path / "bookmarks.html",
                tamanho_arquivo_bytes=100,
                file_is_html=True,
            )

    def test_inferir_flag_html_de_suffix(self, tmp_path: Path) -> None:
        """Verifica se a flag HTML pode ser inferida pela extensão do arquivo.

        Garante que arquivos com extensão .html são marcados como HTML
        mesmo se a flag inicial for falsa.
        """
        arq = ModeloArquivo(
            nome_arquivo="bookmarks.html",
            caminho_arquivo=tmp_path / "bookmarks.html",
            tamanho_arquivo_bytes=100,
            file_is_html=False,
        )
        assert arq.file_is_html is True


class TestModeloArquivoEquality:
    """Testes de igualdade para ModeloArquivo.

    Valida que a comparação entre instâncias leva em conta o caminho do
    arquivo e distingue arquivos diferentes.
    """

    def test_igualdade_por_caminho(self, caminho_arquivo_html: Path) -> None:
        """Garante que arquivos com o mesmo caminho absoluto são considerados iguais.

        Verifica se duas instâncias com os mesmos dados compartilham a
        mesma identidade lógica.
        """
        a = ModeloArquivo(
            nome_arquivo="bookmarks.html",
            caminho_arquivo=caminho_arquivo_html,
            tamanho_arquivo_bytes=100,
            file_is_html=True,
        )
        b = ModeloArquivo(
            nome_arquivo="bookmarks.html",
            caminho_arquivo=caminho_arquivo_html,
            tamanho_arquivo_bytes=100,
            file_is_html=True,
        )
        assert a == b

    def test_desigualdade_por_caminho_diferente(self, tmp_path: Path) -> None:
        """Garante que arquivos com caminhos diferentes não são iguais.

        Verifica se a desigualdade é detectada quando os caminhos absolutos
        divergem, mesmo com campos semelhantes.
        """
        a = ModeloArquivo(
            nome_arquivo="a.html",
            caminho_arquivo=tmp_path / "a.html",
            tamanho_arquivo_bytes=100,
            file_is_html=True,
        )
        b = ModeloArquivo(
            nome_arquivo="b.html",
            caminho_arquivo=tmp_path / "b.html",
            tamanho_arquivo_bytes=100,
            file_is_html=True,
        )
        assert a != b


# ===========================================================================
# ModeloPasta
# ===========================================================================


class TestModeloPastaCreation:
    """Testes de criação de instâncias de ModeloPasta.

    Verifica que pastas raiz e filhas são criadas corretamente e que
    combinações inconsistentes são rejeitadas.
    """

    def test_cria_pasta_raiz_sem_pai(self, pasta_raiz: ModeloPasta) -> None:
        """Garante que uma pasta raiz pode ser criada sem referência a pasta pai.

        Verifica se os campos básicos de uma pasta raiz são inicializados
        com valores coerentes.
        """
        assert pasta_raiz.nome_pasta == "home"
        assert pasta_raiz.caminho_absoluto.is_absolute()
        assert pasta_raiz.pasta_pai is None
        assert pasta_raiz.subpastas == []
        assert pasta_raiz.subarquivos == []

    def test_cria_pasta_com_pai_inconsistente_levanta_value_error(
        self, tmp_path: Path
    ) -> None:
        """Garante que pastas com caminhos incompatíveis com o pai são rejeitadas.

        Verifica se a entidade detecta pastas filhas cujo caminho não está
        contido no caminho do pai.
        """
        pai = ModeloPasta(
            nome_pasta="home", caminho_absoluto=tmp_path / "home", pasta_pai=None
        )
        with pytest.raises(
            expected_exception=ValueError, match="Pasta pai inconsistente"
        ):
            ModeloPasta(
                nome_pasta="intruso",
                caminho_absoluto=tmp_path / "outro_lugar" / "intruso",
                pasta_pai=pai,
            )

    def test_nome_relativo_levanta_value_error(self) -> None:
        """Garante que o caminho absoluto da pasta não pode ser relativo.

        Verifica se o construtor dispara ValueError quando recebe um Path relativo.
        """
        with pytest.raises(expected_exception=ValueError, match="absoluto"):
            ModeloPasta(
                nome_pasta="home",
                caminho_absoluto=Path("relative/home"),
            )

    def test_nome_com_barras_levanta_value_error(self, tmp_path: Path) -> None:
        """Garante que o nome da pasta não pode conter barras.

        Verifica se nomes com separadores de diretório são rejeitados no construtor.
        """
        with pytest.raises(expected_exception=ValueError, match="barras"):
            ModeloPasta(
                nome_pasta="sub/dir",
                caminho_absoluto=tmp_path / "sub",
            )

    def test_pasta_pai_invalido_levanta_type_error(self, tmp_path: Path) -> None:
        """Garante que apenas objetos ModeloPasta podem ser usados como pasta pai.

        Verifica se tipos incorretos em pasta_pai resultam em TypeError.
        """
        with pytest.raises(expected_exception=TypeError, match="pasta_pai"):
            ModeloPasta(
                nome_pasta="home",
                caminho_absoluto=tmp_path,
                pasta_pai="not-a-pasta",  # type: ignore[arg-type]
            )


class TestModeloPastaSubpastas:
    """Testes relacionados à gestão de subpastas em ModeloPasta.

    Verifica a adição, rejeição e validação de relacionamentos entre
    pastas pai e filhas.
    """

    def test_adiciona_subpasta_valida(
        self, pasta_raiz: ModeloPasta, tmp_path: Path
    ) -> None:
        """Garante que uma subpasta válida pode ser adicionada à pasta raiz.

        Verifica se a referência ao pai é atualizada e se a subpasta
        passa a compor a lista de subpastas.
        """
        sub = ModeloPasta(
            nome_pasta="Downloads",
            caminho_absoluto=tmp_path / "Downloads",
            pasta_pai=None,
        )
        pasta_raiz.adicionar_subpasta(sub_pasta=sub)
        assert sub in pasta_raiz.subpastas
        assert sub.pasta_pai is pasta_raiz

    def test_adicionar_subpasta_duplicata_pelo_caminho_ignorada(
        self, pasta_raiz: ModeloPasta, tmp_path: Path
    ) -> None:
        """Garante que subpastas duplicadas pelo mesmo caminho são ignoradas.

        Verifica se a lista de subpastas não acumula referências repetidas
        à mesma instância.
        """
        sub = ModeloPasta(
            nome_pasta="Downloads",
            caminho_absoluto=tmp_path / "Downloads",
            pasta_pai=None,
        )
        pasta_raiz.adicionar_subpasta(sub_pasta=sub)
        pasta_raiz.adicionar_subpasta(sub_pasta=sub)
        assert pasta_raiz.subpastas.count(sub) == 1

    def test_subpasta_nao_pode_ser_si_mesma(self, pasta_raiz: ModeloPasta) -> None:
        """Garante que uma pasta não pode ser adicionada como subpasta de si mesma.

        Verifica se a entidade protege contra ciclos triviais na hierarquia
        de diretórios.
        """
        with pytest.raises(expected_exception=ValueError, match="si mesma"):
            pasta_raiz.adicionar_subpasta(sub_pasta=pasta_raiz)

    def test_subpasta_com_outro_pai_levanta_value_error(
        self, pasta_raiz: ModeloPasta, tmp_path: Path
    ) -> None:
        """Garante que uma subpasta já vinculada a outro pai não pode ser reassociada.

        Verifica se a tentativa de reaproveitar uma subpasta com pasta_pai
        diferente resulta em ValueError.
        """
        outro_pai = ModeloPasta(
            nome_pasta="outro", caminho_absoluto=tmp_path / "outro", pasta_pai=None
        )
        sub = ModeloPasta(
            nome_pasta="sub",
            caminho_absoluto=tmp_path / "outro" / "sub",
            pasta_pai=outro_pai,
        )
        with pytest.raises(expected_exception=ValueError, match="outro pai"):
            pasta_raiz.adicionar_subpasta(sub_pasta=sub)

    def test_subpasta_com_nome_duplicado_levanta_value_error(
        self, pasta_raiz: ModeloPasta, tmp_path: Path
    ) -> None:
        """Garante que duas subpastas com o mesmo nome não podem coexistir sob o mesmo pai.

        Verifica se a entidade detecta duplicação de nomes mesmo quando os
        caminhos absolutos são distintos.
        """
        sub_a = ModeloPasta(
            nome_pasta="Downloads",
            caminho_absoluto=tmp_path / "Downloads",
            pasta_pai=pasta_raiz,
        )
        sub_b = ModeloPasta(
            nome_pasta="Downloads",
            caminho_absoluto=tmp_path / "Downloads_2",
            pasta_pai=None,
        )
        pasta_raiz.adicionar_subpasta(sub_pasta=sub_a)
        with pytest.raises(expected_exception=ValueError, match="duplicado"):
            pasta_raiz.adicionar_subpasta(sub_pasta=sub_b)


class TestModeloPastaArquivos:
    """Testes relacionados à gestão de arquivos em ModeloPasta.

    Verifica a adição de arquivos, a prevenção de duplicatas e a
    validação de caminhos e tipos.
    """

    def test_adiciona_arquivo_valido(
        self, pasta_raiz: ModeloPasta, caminho_arquivo_html: Path
    ) -> None:
        """Garante que um arquivo válido pode ser associado à pasta.

        Verifica se o arquivo passa a constar na lista de arquivos da pasta
        após a adição.
        """
        arquivo = ModeloArquivo(
            nome_arquivo="bookmarks.html",
            caminho_arquivo=caminho_arquivo_html,
            tamanho_arquivo_bytes=128,
            file_is_html=True,
        )
        pasta_raiz.adicionar_arquivo(sub_arquivo=arquivo)
        assert arquivo in pasta_raiz.subarquivos

    def test_adiciona_arquivo_duplicado_pelo_caminho_ignorado(
        self, pasta_raiz: ModeloPasta, caminho_arquivo_html: Path
    ) -> None:
        """Garante que um mesmo arquivo não é adicionado mais de uma vez.

        Verifica se tentativas repetidas de registrar o mesmo arquivo não
        criam duplicatas na lista.
        """
        arquivo = ModeloArquivo(
            nome_arquivo="bookmarks.html",
            caminho_arquivo=caminho_arquivo_html,
            tamanho_arquivo_bytes=128,
            file_is_html=True,
        )
        pasta_raiz.adicionar_arquivo(sub_arquivo=arquivo)
        pasta_raiz.adicionar_arquivo(sub_arquivo=arquivo)
        assert pasta_raiz.subarquivos.count(arquivo) == 1

    def test_adicionar_arquivo_pai_inconsistente_levanta_value_error(
        self, pasta_raiz: ModeloPasta, tmp_path: Path
    ) -> None:
        """Garante que arquivos fora da árvore da pasta são rejeitados.

        Verifica se um ValueError é disparado quando o caminho do arquivo
        não está contido na pasta.
        """
        arquivo = ModeloArquivo(
            nome_arquivo="outro.html",
            caminho_arquivo=tmp_path / "other" / "outro.html",
            tamanho_arquivo_bytes=100,
            file_is_html=True,
        )
        with pytest.raises(expected_exception=ValueError, match="não está na pasta"):
            pasta_raiz.adicionar_arquivo(sub_arquivo=arquivo)

    def test_adicionar_arquivo_com_tipo_invalido_levanta_type_error(
        self, pasta_raiz: ModeloPasta
    ) -> None:
        """Garante que apenas instâncias de ModeloArquivo podem ser adicionadas.

        Verifica se tipos arbitrários ao adicionar arquivos resultam em TypeError.
        """
        with pytest.raises(expected_exception=TypeError):
            pasta_raiz.adicionar_arquivo(sub_arquivo="nao é arquivo")  # type: ignore[arg-type]


class TestModeloPastaValidationLists:
    """Testes de validação de listas passadas ao construtor de ModeloPasta.

    Assegura que as listas de subpastas e subarquivos contenham apenas
    tipos esperados.
    """

    def test_construtor_rejeita_subpasta_com_tipo_invalido(
        self, tmp_path: Path
    ) -> None:
        """Garante que o construtor rejeita subpastas com tipo inválido.

        Verifica se a lista de subpastas aceita somente instâncias de ModeloPasta.
        """
        with pytest.raises(expected_exception=TypeError, match="ModeloPasta"):
            ModeloPasta(
                nome_pasta="home",
                caminho_absoluto=tmp_path,
                subpastas=["not-a-folder"],  # type: ignore[list-item]
            )

    def test_construtor_rejeita_arquivo_com_tipo_invalido(self, tmp_path: Path) -> None:
        """Garante que o construtor rejeita arquivos com tipo inválido.

        Verifica se a lista de subarquivos aceita apenas instâncias de ModeloArquivo.
        """
        with pytest.raises(expected_exception=TypeError, match="ModeloArquivo"):
            ModeloPasta(
                nome_pasta="home",
                caminho_absoluto=tmp_path,
                subarquivos=["not-a-file"],  # type: ignore[list-item]
            )


# ===========================================================================
# ModeloSistemaOperacional
# ===========================================================================


class TestModeloSistemaOperacionalCreation:
    """Testes de criação de instâncias de ModeloSistemaOperacional.

    Verifica regras de validação para nome, versão e diretório home do usuário.
    """

    def test_cria_com_campos_validos(self, tmp_path: Path) -> None:
        """Garante que um modelo de sistema operacional válido pode ser criado.

        Verifica se os campos são armazenados corretamente quando todos os
        valores são coerentes.
        """
        so = ModeloSistemaOperacional(
            nome_sistema="linux",
            versao_sistema="5.15.0",
            user_home=tmp_path,
        )
        assert so.nome_sistema == "linux"
        assert so.versao_sistema == "5.15.0"
        assert so.user_home == tmp_path

    def test_user_home_deve_ser_absoluto(self, tmp_path: Path) -> None:
        """Garante que o diretório home deve ser representado por um caminho absoluto.

        Verifica se caminhos relativos para user_home são rejeitados com ValueError.
        """
        with pytest.raises(expected_exception=ValueError, match="absoluto"):
            ModeloSistemaOperacional(
                nome_sistema="linux",
                versao_sistema="5.15.0",
                user_home=Path("relative/home"),
            )

    def test_user_home_deve_existir(self, tmp_path: Path) -> None:
        """Garante que o diretório home informado deve existir no sistema de arquivos.

        Verifica se um caminho inexistente para user_home resulta em ValueError.
        """
        invalid_home: Path = tmp_path / "missing"
        with pytest.raises(expected_exception=ValueError, match="existente"):
            ModeloSistemaOperacional(
                nome_sistema="linux",
                versao_sistema="5.15.0",
                user_home=invalid_home,
            )

    def test_nome_sistema_com_queixa_de_newline(self, tmp_path: Path) -> None:
        """Garante que o nome do sistema operacional não aceite quebras de linha.

        Verifica se nomes contendo caracteres de nova linha são rejeitados
        com ValueError.
        """
        with pytest.raises(
            expected_exception=ValueError, match="não pode conter quebras"
        ):
            ModeloSistemaOperacional(
                nome_sistema="linux\n",
                versao_sistema="5.15.0",
                user_home=tmp_path,
            )

    def test_versao_com_barra_levanta_value_error(self, tmp_path: Path) -> None:
        """Garante que a versão do sistema não pode conter barras.

        Verifica se versões com separadores de diretório são rejeitadas
        pelo construtor.
        """
        with pytest.raises(
            expected_exception=ValueError, match="não pode conter barras"
        ):
            ModeloSistemaOperacional(
                nome_sistema="linux",
                versao_sistema="5/15",
                user_home=tmp_path,
            )

    def test_user_home_tipo_invalido_levanta_type_error(self, tmp_path: Path) -> None:
        """Garante que o diretório home deve ser um Path e não uma string arbitrária.

        Verifica se a passagem de tipos incompatíveis para user_home resulta
        em TypeError.
        """
        with pytest.raises(expected_exception=TypeError, match="Path"):
            ModeloSistemaOperacional(
                nome_sistema="linux",
                versao_sistema="5.15.0",
                user_home="/home/usuario",  # type: ignore[arg-type]
            )


class TestModeloSistemaOperacionalEquality:
    """Testes de igualdade para ModeloSistemaOperacional.

    Verifica que instâncias com os mesmos campos são iguais e que
    diferenças relevantes quebram a igualdade.
    """

    def test_instancias_iguais_sao_iguais(self, tmp_path: Path) -> None:
        """Garante que duas instâncias com os mesmos atributos são consideradas iguais.

        Verifica se a implementação de igualdade leva em conta todos os
        campos relevantes.
        """
        a = ModeloSistemaOperacional(
            nome_sistema="linux",
            versao_sistema="5.15.0",
            user_home=tmp_path,
        )
        b = ModeloSistemaOperacional(
            nome_sistema="linux",
            versao_sistema="5.15.0",
            user_home=tmp_path,
        )
        assert a == b

    def test_instancias_diferentes_nao_sao_iguais(self, tmp_path: Path) -> None:
        """Garante que instâncias com dados diferentes não são iguais.

        Verifica se uma mudança no nome do sistema é suficiente para
        quebrar a igualdade.
        """
        a = ModeloSistemaOperacional(
            nome_sistema="linux",
            versao_sistema="5.15.0",
            user_home=tmp_path,
        )
        b = ModeloSistemaOperacional(
            nome_sistema="darwin",
            versao_sistema="5.15.0",
            user_home=tmp_path,
        )
        assert a != b


# ===========================================================================
# ResultadoProcessamento
# ===========================================================================


class TestResultadoProcessamento:
    """Testes para o modelo ResultadoProcessamento.

    Verifica a estrutura de serialização e a validação do tipo do caminho raiz.
    """

    def test_to_dict_returns_expected_structure(self, tmp_path: Path) -> None:
        """Garante que o método to_dict retorna a estrutura esperada.

        Verifica se o dicionário produzido contém chaves e valores alinhados
        com o contrato público da entidade.
        """
        estatisticas = EstatisticasProcessamento(
            total_files=1,
            processed_files=1,
            failed_files=0,
            total_bookmarks=1,
        )
        resultado = ResultadoProcessamento(
            bookmarks=[],
            statistics=estatisticas,
            root_path=str(tmp_path),
        )
        expected: dict[str, str | list | dict[str, int]] = {
            "bookmarks": [],
            "estatisticas": {
                "total_arquivos": 1,
                "arquivos_processados": 1,
                "arquivos_com_falha": 0,
                "total_bookmarks": 1,
            },
            "caminho_raiz": str(tmp_path),
        }
        assert resultado.to_dict() == expected

    def test_root_path_deve_ser_string(self, tmp_path: Path) -> None:
        """Garante que o campo root_path deve ser sempre uma string.

        Verifica se a entidade rejeita caminhos raiz fornecidos como Path e
        emite um TypeError claro.
        """
        estatisticas = EstatisticasProcessamento(
            total_files=0,
            processed_files=0,
            failed_files=0,
            total_bookmarks=0,
        )
        with pytest.raises(
            expected_exception=TypeError, match="caminho_raiz deve ser str"
        ):
            ResultadoProcessamento(
                bookmarks=[],
                statistics=estatisticas,
                root_path=tmp_path,  # type: ignore[arg-type]
            )
