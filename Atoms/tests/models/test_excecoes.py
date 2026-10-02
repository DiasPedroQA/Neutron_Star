# Atoms/tests/models/test_excecoes.py
# pylint: disable=C

"""Testes unitários para a hierarquia de exceções do domínio."""

from typing import Any

import pytest

from src.models.excecoes import (
    DiretorioInexistenteError,
    DominioError,
    ExtensaoInvalidaError,
    FormatoInvalidoError,
    PathInseguroError,
)


def test_path_inseguro_error_mensagem_e_heranca() -> None:
    """Garante formatação e hierarquia da exceção de Path Traversal."""
    caminho_violado = "/etc/passwd"
    erro = PathInseguroError(caminho=caminho_violado)

    assert isinstance(erro, DominioError)
    assert caminho_violado in str(erro)
    assert "Acesso Proibido" in str(erro)


def test_diretorio_inexistente_error_mensagem() -> None:
    """Garante mensagem amigável para diretório não localizado."""
    caminho = "~/pasta_fantasma"
    erro = DiretorioInexistenteError(caminho=caminho)

    assert isinstance(erro, DominioError)
    assert caminho in str(erro)
    assert "não existe no disco" in str(erro)


def test_extensao_invalida_error_e_alias() -> None:
    """Garante suporte e compatibilidade de alias de formato inválido."""
    erro = ExtensaoInvalidaError("Formato '.exe' não permitido.")
    assert isinstance(erro, DominioError)

    alias_erro = FormatoInvalidoError("Formato '.bin' inválido.")
    assert isinstance(alias_erro, ExtensaoInvalidaError)


@pytest.mark.parametrize(
    ("mensagem", "args_esperados"),
    [
        pytest.param(
            "Operação realizada com sucesso",
            ("Operação realizada com sucesso",),
            id="mensagem-sucesso",
        ),
        pytest.param(
            "O recurso solicitado não existe",
            ("O recurso solicitado não existe",),
            id="mensagem-recurso-inexistente",
        ),
        pytest.param(
            "Falha ao validar os dados do domínio",
            ("Falha ao validar os dados do domínio",),
            id="mensagem-validacao-dominio",
        ),
    ],
)
def test_dominio_error_deve_ser_criada_com_mensagens_realistas(
    mensagem: str, args_esperados: tuple[Any, ...]
) -> None:
    # Act
    excecao = DominioError(mensagem)

    # Assert
    assert isinstance(excecao, Exception)
    assert isinstance(excecao, DominioError)
    assert str(excecao) == mensagem
    assert excecao.args == args_esperados


@pytest.mark.parametrize(
    ("argumentos", "mensagem_esperada"),
    [
        pytest.param(
            (),
            "",
            id="sem-argumentos",
        ),
        pytest.param(
            (None,),
            "None",
            id="argumento-none",
        ),
        pytest.param(
            ("",),
            "",
            id="mensagem-vazia",
        ),
        pytest.param(
            (0,),
            "0",
            id="argumento-zero",
        ),
        pytest.param(
            (False,),
            "False",
            id="argumento-falso",
        ),
    ],
)
def test_dominio_error_deve_preservar_casos_de_borda(
    argumentos: tuple[Any, ...], mensagem_esperada: str
) -> None:
    # Act
    excecao = DominioError(*argumentos)

    # Assert
    assert isinstance(excecao, DominioError)
    assert str(excecao) == mensagem_esperada
    assert excecao.args == argumentos


@pytest.mark.parametrize(
    ("argumentos", "mensagem_esperada"),
    [
        pytest.param(
            ("campo inválido", 422),
            "('campo inválido', 422)",
            id="mensagem-com-codigo-http",
        ),
        pytest.param(
            ("erro", {"campo": "nome"}),
            "('erro', {'campo': 'nome'})",
            id="mensagem-com-detalhes",
        ),
        pytest.param(
            (["item inválido"],),
            "['item inválido']",
            id="mensagem-com-lista",
        ),
    ],
)
def test_dominio_error_deve_aceitar_argumentos_de_erro_variados(
    argumentos: tuple[Any, ...], mensagem_esperada: str
) -> None:
    # Act
    excecao = DominioError(*argumentos)

    # Assert
    assert isinstance(excecao, DominioError)
    assert excecao.args == argumentos
    assert str(excecao) == mensagem_esperada


@pytest.mark.parametrize(
    "classe_excecao",
    [
        pytest.param(DominioError, id="classe-dominio-error"),
    ],
)
def test_dominio_error_deve_poder_ser_lancada_e_capturada(classe_excecao: type[Exception]) -> None:
    mensagem = "Regra de domínio violada"

    # Act
    with pytest.raises(classe_excecao) as contexto:
        raise classe_excecao(mensagem)

    # Assert
    assert contexto.value.args == (mensagem,)
    assert str(contexto.value) == mensagem


def test_dominio_error_deve_ser_subclasse_direta_de_exception() -> None:
    # Act
    bases = DominioError.__bases__

    # Assert
    assert bases == (Exception,)
    assert DominioError.__doc__ == ("Exceção base para todas as regras de domínio.")


@pytest.mark.parametrize(
    ("caminho", "mensagem_esperada"),
    [
        pytest.param(
            "../configuracoes.py",
            (
                "Acesso Proibido! O caminho '../configuracoes.py' tenta "
                "acessar arquivos fora da sua pasta pessoal de segurança."
            ),
            id="parent-directory-configuracoes",
        ),
        pytest.param(
            "../../etc/passwd",
            (
                "Acesso Proibido! O caminho '../../etc/passwd' tenta "
                "acessar arquivos fora da sua pasta pessoal de segurança."
            ),
            id="parent-directory-etc-passwd",
        ),
        pytest.param(
            "/etc/shadow",
            (
                "Acesso Proibido! O caminho '/etc/shadow' tenta "
                "acessar arquivos fora da sua pasta pessoal de segurança."
            ),
            id="caminho-absoluto-sistema",
        ),
        pytest.param(
            "documentos/../../../segredo.txt",
            (
                "Acesso Proibido! O caminho "
                "'documentos/../../../segredo.txt' tenta "
                "acessar arquivos fora da sua pasta pessoal de segurança."
            ),
            id="traversal-com-diretorio-intermediario",
        ),
    ],
)
def test_path_inseguro_error_deve_informar_caminho_bloqueado(
    caminho: Any, mensagem_esperada: str
) -> None:
    # Act
    excecao = PathInseguroError(caminho)

    # Assert
    assert isinstance(excecao, PathInseguroError)
    assert isinstance(excecao, DominioError)
    assert isinstance(excecao, Exception)
    assert str(excecao) == mensagem_esperada
    assert excecao.args == (mensagem_esperada,)


@pytest.mark.parametrize(
    ("caminho", "mensagem_esperada"),
    [
        pytest.param(
            "",
            (
                "Acesso Proibido! O caminho '' tenta "
                "acessar arquivos fora da sua pasta pessoal de segurança."
            ),
            id="caminho-vazio",
        ),
        pytest.param(
            ".",
            (
                "Acesso Proibido! O caminho '.' tenta "
                "acessar arquivos fora da sua pasta pessoal de segurança."
            ),
            id="diretorio-atual",
        ),
        pytest.param(
            "..",
            (
                "Acesso Proibido! O caminho '..' tenta "
                "acessar arquivos fora da sua pasta pessoal de segurança."
            ),
            id="diretorio-pai",
        ),
        pytest.param(
            "arquivo com espaços.txt",
            (
                "Acesso Proibido! O caminho 'arquivo com espaços.txt' tenta "
                "acessar arquivos fora da sua pasta pessoal de segurança."
            ),
            id="nome-com-espacos",
        ),
        pytest.param(
            "pasta/arquivo-çã.txt",
            (
                "Acesso Proibido! O caminho 'pasta/arquivo-çã.txt' tenta "
                "acessar arquivos fora da sua pasta pessoal de segurança."
            ),
            id="caminho-com-unicode",
        ),
    ],
)
def test_path_inseguro_error_deve_formatar_casos_de_borda(
    caminho: Any, mensagem_esperada: str
) -> None:
    # Act
    excecao = PathInseguroError(caminho)

    # Assert
    assert str(excecao) == mensagem_esperada
    assert excecao.args == (mensagem_esperada,)


@pytest.mark.parametrize(
    ("caminho", "mensagem_esperada"),
    [
        pytest.param(
            None,
            (
                "Acesso Proibido! O caminho 'None' tenta "
                "acessar arquivos fora da sua pasta pessoal de segurança."
            ),
            id="caminho-none",
        ),
        pytest.param(
            123,
            (
                "Acesso Proibido! O caminho '123' tenta "
                "acessar arquivos fora da sua pasta pessoal de segurança."
            ),
            id="caminho-inteiro",
        ),
        pytest.param(
            ["..", "segredo.txt"],
            (
                "Acesso Proibido! O caminho '['..', 'segredo.txt']' tenta "
                "acessar arquivos fora da sua pasta pessoal de segurança."
            ),
            id="caminho-lista",
        ),
    ],
)
def test_path_inseguro_error_deve_formatar_valores_de_caminho_invalidos(
    caminho: Any, mensagem_esperada: str
) -> None:
    # Act
    excecao = PathInseguroError(caminho)

    # Assert
    assert isinstance(excecao, PathInseguroError)
    assert str(excecao) == mensagem_esperada
    assert excecao.args == (mensagem_esperada,)


@pytest.mark.parametrize(
    "caminho",
    [
        pytest.param("../arquivo.txt", id="lancamento-parent-directory"),
        pytest.param("/var/log/app.log", id="lancamento-caminho-absoluto"),
    ],
)
def test_path_inseguro_error_deve_poder_ser_lancada(caminho: Any) -> None:
    # Act
    with pytest.raises(PathInseguroError) as contexto:
        raise PathInseguroError(caminho)

    # Assert
    assert contexto.value.args[0].startswith("Acesso Proibido!")
    assert caminho in str(contexto.value)


def test_path_inseguro_error_deve_herdar_a_docstring_da_classe() -> None:
    # Act
    docstring = PathInseguroError.__doc__

    # Assert
    assert docstring == (
        "Lançada quando um caminho tenta acessar áreas fora do escopo seguro (Path Traversal)."
    )


@pytest.mark.parametrize(
    "extensao",
    [
        pytest.param(".pdf", id="extensao-pdf"),
        pytest.param(".docx", id="extensao-docx"),
        pytest.param(".xlsx", id="extensao-xlsx"),
        pytest.param("json", id="extensao-json-sem-ponto"),
    ],
)
def test_extensao_invalida_error_deve_ser_criada_com_extensoes_realistas(
    extensao: Any,
) -> None:
    # Act
    excecao = ExtensaoInvalidaError(extensao)

    # Assert
    assert isinstance(excecao, ExtensaoInvalidaError)
    assert isinstance(excecao, DominioError)
    assert isinstance(excecao, Exception)
    assert excecao.args == (extensao,)
    assert str(excecao) == extensao


@pytest.mark.parametrize(
    "argumentos",
    [
        pytest.param((), id="sem-argumentos"),
        pytest.param(("",), id="extensao-vazia"),
        pytest.param((".",), id="somente-ponto"),
        pytest.param(("   ",), id="extensao-com-espacos"),
        pytest.param(("EXTENSAO_MUITO_LONGA_" * 10,), id="extensao-muito-longa"),
    ],
)
def test_extensao_invalida_error_deve_aceitar_casos_de_borda(argumentos: tuple[Any, ...]) -> None:
    # Act
    excecao = ExtensaoInvalidaError(*argumentos)

    # Assert
    assert isinstance(excecao, ExtensaoInvalidaError)
    assert excecao.args == argumentos
    assert str(excecao) == (str(argumentos[0]) if argumentos else "")


@pytest.mark.parametrize(
    ("argumento", "texto_esperado"),
    [
        pytest.param(None, "None", id="extensao-none"),
        pytest.param(123, "123", id="extensao-inteira"),
        pytest.param(
            ["pdf", "docx"],
            "['pdf', 'docx']",
            id="extensao-lista",
        ),
        pytest.param(
            {"extensao": "exe"},
            "{'extensao': 'exe'}",
            id="extensao-dicionario",
        ),
    ],
)
def test_extensao_invalida_error_deve_aceitar_argumentos_de_tipos_invalidos(
    argumento: Any, texto_esperado: str
) -> None:
    # Act
    excecao = ExtensaoInvalidaError(argumento)

    # Assert
    assert isinstance(excecao, ExtensaoInvalidaError)
    assert excecao.args == (argumento,)
    assert str(excecao) == texto_esperado


@pytest.mark.parametrize(
    "argumentos",
    [
        pytest.param(
            (".exe",),
            id="lancamento-com-extensao-executavel",
        ),
        pytest.param(
            ("formato-desconhecido",),
            id="lancamento-com-formato-desconhecido",
        ),
    ],
)
def test_extensao_invalida_error_deve_poder_ser_lancada(argumentos: tuple[Any, ...]) -> None:
    # Act
    with pytest.raises(ExtensaoInvalidaError) as contexto:
        raise ExtensaoInvalidaError(*argumentos)

    # Assert
    assert contexto.value.args == argumentos
    assert isinstance(contexto.value, DominioError)


def test_extensao_invalida_error_deve_herdar_diretamente_de_dominio_error() -> None:
    # Act
    bases = ExtensaoInvalidaError.__bases__

    # Assert
    assert bases == (DominioError,)
    assert ExtensaoInvalidaError.__doc__ == (
        "Lançada quando um formato de saída ou extensão não é suportado."
    )


@pytest.mark.parametrize(
    "mensagem",
    [
        pytest.param("Formato PDF não suportado", id="formato-pdf"),
        pytest.param("Extensão .exe inválida", id="extensao-executavel"),
        pytest.param(
            "O formato de exportação CSV não está disponível",
            id="exportacao-csv-indisponivel",
        ),
    ],
)
def test_formato_invalido_error_deve_preservar_mensagens_realistas(mensagem: str) -> None:
    # Act
    excecao = FormatoInvalidoError(mensagem)

    # Assert
    assert isinstance(excecao, FormatoInvalidoError)
    assert isinstance(excecao, ExtensaoInvalidaError)
    assert isinstance(excecao, DominioError)
    assert isinstance(excecao, Exception)
    assert excecao.args == (mensagem,)
    assert str(excecao) == mensagem


@pytest.mark.parametrize(
    "argumentos",
    [
        pytest.param((), id="sem-argumentos"),
        pytest.param(("",), id="mensagem-vazia"),
        pytest.param((" ",), id="mensagem-com-espaco"),
        pytest.param(
            ("mensagem muito longa " * 20,),
            id="mensagem-muito-longa",
        ),
    ],
)
def test_formato_invalido_error_deve_aceitar_casos_de_borda(argumentos: tuple[Any, ...]) -> None:
    # Act
    excecao = FormatoInvalidoError(*argumentos)

    # Assert
    assert isinstance(excecao, FormatoInvalidoError)
    assert excecao.args == argumentos
    assert str(excecao) == (argumentos[0] if argumentos else "")


@pytest.mark.parametrize(
    ("argumento", "texto_esperado"),
    [
        pytest.param(None, "None", id="mensagem-none"),
        pytest.param(404, "404", id="mensagem-inteira"),
        pytest.param(
            ["pdf", "docx"],
            "['pdf', 'docx']",
            id="mensagem-lista",
        ),
        pytest.param(
            {"formato": "binário"},
            "{'formato': 'binário'}",
            id="mensagem-dicionario",
        ),
    ],
)
def test_formato_invalido_error_deve_aceitar_tipos_de_mensagem_variados(
    argumento: Any, texto_esperado: str
) -> None:
    # Act
    excecao = FormatoInvalidoError(argumento)

    # Assert
    assert isinstance(excecao, FormatoInvalidoError)
    assert excecao.args == (argumento,)
    assert str(excecao) == texto_esperado


@pytest.mark.parametrize(
    "mensagem",
    [
        pytest.param("Não é possível exportar neste formato", id="erro-exportacao"),
        pytest.param("Extensão desconhecida", id="erro-extensao"),
    ],
)
def test_formato_invalido_error_deve_poder_ser_lancada(mensagem: str) -> None:
    # Act
    with pytest.raises(FormatoInvalidoError) as contexto:
        raise FormatoInvalidoError(mensagem)

    # Assert
    assert contexto.value.args == (mensagem,)
    assert str(contexto.value) == mensagem


def test_formato_invalido_error_deve_herdar_diretamente_de_extensao_invalida() -> None:
    # Act
    bases = FormatoInvalidoError.__bases__

    # Assert
    assert bases == (ExtensaoInvalidaError,)
    assert FormatoInvalidoError.__doc__ == (
        "Alias compatível para formatos e extensões não suportadas."
    )
