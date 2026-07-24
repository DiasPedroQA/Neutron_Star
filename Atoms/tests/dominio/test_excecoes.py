"""Testes da hierarquia de exceções de domínio (dominio/excecoes.py).

Cobre o bug corrigido: contexto passou a ser opcional, já que vários
pontos do código levantam essas exceções sem informá-lo.
"""

import pytest
from dominio.excecoes import (
    ErroBookmarks,
    ErroParseBookmarks,
    NenhumDiretorioValidoError,
)


class TestErroBookmarks:
    """Comportamento da exceção base do módulo."""

    def test_pode_ser_levantada_sem_contexto(self) -> None:
        """contexto é opcional: levantar sem informá-lo não deve gerar TypeError."""
        with pytest.raises(expected_exception=ErroBookmarks, match="mensagem simples"):
            raise ErroBookmarks(mensagem="mensagem simples")

    def test_contexto_ausente_vira_dicionario_vazio(self) -> None:
        """Sem contexto informado, o atributo deve ser um dict vazio, nunca None."""
        erro = ErroBookmarks(mensagem="mensagem")

        assert erro.contexto == {}

    def test_str_inclui_contexto_quando_informado(self) -> None:
        """A representação em string deve anexar os pares chave=valor do contexto."""
        erro = ErroBookmarks(mensagem="falha ao processar", contexto={"arquivo": "a.html"})

        assert "falha ao processar" in str(erro)
        assert "arquivo='a.html'" in str(erro)

    def test_str_sem_contexto_mostra_apenas_a_mensagem(self) -> None:
        """Sem contexto, a string não deve ter colchetes nem detalhes extras."""
        erro = ErroBookmarks(mensagem="falha simples")

        assert str(erro) == "falha simples"


class TestSubclasses:
    """Garante que as subclasses herdam o mesmo contrato da classe base."""

    def test_nenhum_diretorio_valido_error_aceita_contexto(self) -> None:
        """NenhumDiretorioValidoError deve aceitar contexto normalmente."""
        erro = NenhumDiretorioValidoError(mensagem="nenhum diretório válido", contexto={"caminhos_tentados": "/tmp/x"})

        assert erro.contexto == {"caminhos_tentados": "/tmp/x"}

    def test_erro_parse_bookmarks_aceita_ser_levantada_sem_contexto(self) -> None:
        """ErroParseBookmarks é o caso real usado em parse_bookmarks.py sem contexto."""
        with pytest.raises(expected_exception=ErroParseBookmarks):
            raise ErroParseBookmarks(mensagem="Elemento <DL> raiz não encontrado.")
