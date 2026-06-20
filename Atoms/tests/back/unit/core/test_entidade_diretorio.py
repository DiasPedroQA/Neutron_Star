# Atoms/tests/back/unit/core/test_entidade_diretorio.py

"""Testes para a entidade ModeloPasta."""

from pathlib import Path
import pytest

from backend.core.entidades.entidade_arquivo import ModeloArquivo
from backend.core.entidades.entidade_diretorio import ModeloPasta


class TestModeloPasta:
    """Testes para o comportamento da entidade ModeloPasta ao representar diretórios.
    Verifica a criação de instâncias, o relacionamento entre pastas pai e filhas, o gerenciamento de arquivos e a validação de erros."""

    @pytest.fixture
    def pasta_raiz(self, tmp_path: Path) -> Path:
        """Cria uma pasta real temporária com estrutura."""
        raiz: Path = tmp_path / "raiz"
        raiz.mkdir()
        (raiz / "file.html").write_text(data="<html>")
        (raiz / "sub").mkdir()
        return raiz

    def test_criacao_valida(self, tmp_path: Path) -> None:
        """Testa a criação básica de uma instância de ModeloPasta.
        Verifica se os atributos de nome e coleções de subpastas e arquivos são inicializados corretamente."""
        pasta = ModeloPasta(nome_pasta="test", caminho_absoluto=tmp_path / "test")
        assert pasta.nome_pasta == "test"
        assert not pasta.subpastas
        assert not pasta.subarquivos

    def test_adicionar_subpasta(self, tmp_path: Path) -> None:
        """Testa a adição de uma subpasta a uma pasta pai.
        Verifica se a subpasta é registrada na coleção de subpastas e se a referência de pasta_pai é configurada corretamente."""
        pai = ModeloPasta(nome_pasta="pai", caminho_absoluto=tmp_path / "pai")
        filho = ModeloPasta(
            nome_pasta="filho", caminho_absoluto=tmp_path / "pai" / "filho"
        )
        pai.adicionar_subpasta(nova_sub_pasta=filho)
        assert len(pai.subpastas) == 1
        assert filho.pasta_pai is pai

    def test_adicionar_arquivo(self, tmp_path: Path) -> None:
        """Testa a adição de um arquivo a uma pasta.
        Verifica se o arquivo é incluído na coleção de subarquivos da pasta."""
        pasta = ModeloPasta(nome_pasta="p", caminho_absoluto=tmp_path / "p")
        arq = ModeloArquivo(
            nome_arquivo="f.html",
            caminho_arquivo=tmp_path / "p" / "f.html",
            eh_html=True,
        )
        pasta.adicionar_arquivo(sub_arquivo=arq)
        assert len(pasta.subarquivos) == 1

    def test_pasta_pai_invalida_levanta_valueerror(self, tmp_path: Path) -> None:
        """Testa a validação de consistência da referência de pasta_pai em subpastas.
        Verifica se tentar adicionar uma subpasta que já aponta para outro pai resulta em um ValueError adequado."""
        pai = ModeloPasta(nome_pasta="pai", caminho_absoluto=tmp_path / "pai")
        outro = ModeloPasta(nome_pasta="outro", caminho_absoluto=tmp_path / "outro")
        filho = ModeloPasta(
            nome_pasta="filho", caminho_absoluto=tmp_path / "pai" / "filho"
        )
        # Força o filho a ter outro pai e tenta adicionar
        filho._validar_e_ajustar_subpastas = lambda: None  # hack para burlar validação
        filho.pasta_pai = outro
        with pytest.raises(
            expected_exception=ValueError, match="Subpasta já pertence a outro pai."
        ):
            pai.adicionar_subpasta(nova_sub_pasta=filho)

    def test_nome_duplicado_subpasta(self, tmp_path: Path) -> None:
        """Testa a validação de nomes duplicados entre subpastas de uma mesma pasta.
        Verifica se a tentativa de adicionar uma segunda subpasta com o mesmo nome gera um ValueError apropriado."""
        pai = ModeloPasta(nome_pasta="pai", caminho_absoluto=tmp_path / "pai")
        f1 = ModeloPasta(nome_pasta="dup", caminho_absoluto=tmp_path / "pai" / "dup")
        f2 = ModeloPasta(nome_pasta="dup", caminho_absoluto=tmp_path / "pai" / "dup2")
        pai.adicionar_subpasta(nova_sub_pasta=f1)
        with pytest.raises(expected_exception=ValueError, match="nome duplicado"):
            pai.adicionar_subpasta(nova_sub_pasta=f2)
