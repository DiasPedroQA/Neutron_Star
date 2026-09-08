# Atoms/tests/dominio/test_excecoes.py

"""Testes unitários para as exceções personalizadas do domínio."""

import pytest

from src.dominio.excecoes import (
    DiretorioInexistenteError,
    ErroDominio,
    NenhumFavoritoEncontradoError,
    PathInseguroError,
)


def test_erro_dominio_e_uma_exception() -> None:
    """Garante que ErroDominio herda de Exception e pode ser levantada sozinha."""
    with pytest.raises(ErroDominio):
        raise ErroDominio("erro genérico de domínio")


def test_erro_dominio_preserva_a_mensagem_recebida() -> None:
    """Garante que a mensagem passada ao construtor é preservada em str()."""
    erro = ErroDominio("mensagem de teste")

    assert str(erro) == "mensagem de teste"


def test_path_inseguro_error_e_subclasse_de_erro_dominio() -> None:
    """Garante que PathInseguroError pode ser capturada como ErroDominio."""
    with pytest.raises(ErroDominio):
        raise PathInseguroError(caminho="../../etc/passwd")


def test_path_inseguro_error_mensagem_contem_caminho_e_aviso() -> None:
    """Garante que a mensagem final embute o caminho recebido e o aviso de segurança."""
    erro = PathInseguroError(caminho="../../etc/passwd")

    assert "Acesso Proibido" in str(erro)
    assert "../../etc/passwd" in str(erro)
    assert "fora da sua pasta pessoal" in str(erro)


def test_diretorio_inexistente_error_e_subclasse_de_erro_dominio() -> None:
    """Garante que DiretorioInexistenteError pode ser capturada como ErroDominio."""
    with pytest.raises(ErroDominio):
        raise DiretorioInexistenteError(caminho="/home/diaspedro/Inexistente")


def test_diretorio_inexistente_error_mensagem_contem_caminho_e_aviso() -> None:
    """Garante que a mensagem final embute o caminho recebido e o aviso correto."""
    erro = DiretorioInexistenteError(caminho="/home/diaspedro/Inexistente")

    assert "Diretório não encontrado" in str(erro)
    assert "/home/diaspedro/Inexistente" in str(erro)
    assert "não existe no disco local" in str(erro)


def test_nenhum_favorito_encontrado_error_e_subclasse_de_erro_dominio() -> None:
    """Garante que NenhumFavoritoEncontradoError pode ser capturada como ErroDominio."""
    with pytest.raises(ErroDominio):
        raise NenhumFavoritoEncontradoError(arquivo="vazio.html")


def test_nenhum_favorito_encontrado_error_mensagem_contem_arquivo_e_aviso() -> None:
    """Garante que a mensagem final embute o nome do arquivo e o aviso correto."""
    erro = NenhumFavoritoEncontradoError(arquivo="vazio.html")

    assert "vazio.html" in str(erro)
    assert "não possui tags de favoritos" in str(erro)
    assert "válidas para extração" in str(erro)
