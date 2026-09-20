# Atoms/tests/aplicacao/test_casos_uso.py

"""Testes unitários para os Casos de Uso da aplicação."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.aplicacao.casos_uso import (
    ConverterFavoritosLoteUseCase,
    EscanearDiretorioUseCase,
    ObterInfoSistemaUseCase,
)
from src.dominio.entidades import Favorito
from src.dominio.excecoes import DiretorioInexistenteError, PathInseguroError

CAMINHO_FORA_DA_HOME = "/etc/passwd"


def _caminho_seguro(nome_arquivo: str) -> str:
    """Monta um caminho de arquivo garantidamente dentro da Home do usuário de teste."""
    return str(Path.home() / nome_arquivo)


def _montar_conversor(
    leitor: MagicMock | None = None,
    parser: MagicMock | None = None,
    escritor: MagicMock | None = None,
) -> ConverterFavoritosLoteUseCase:
    """Monta o ConverterFavoritosLoteUseCase com portas mockadas,
    permitindo sobrescrever cada uma."""
    return ConverterFavoritosLoteUseCase(
        leitor=leitor or MagicMock(),
        parser=parser or MagicMock(),
        escritor=escritor or MagicMock(),
    )


# --- ObterInfoSistemaUseCase ------------------------------------------------


def test_obter_info_sistema_delega_para_o_gerenciador_e_repassa_o_resultado() -> None:
    """Garante que o resultado do adaptador é devolvido sem transformação."""
    gerenciador = MagicMock()
    gerenciador.obter_informacoes_so.return_value = {"so": "Linux", "usuario": "diaspedro"}
    caso_uso = ObterInfoSistemaUseCase(gerenciador_sistema=gerenciador)

    resultado = caso_uso.executar()

    assert resultado == {"so": "Linux", "usuario": "diaspedro"}
    gerenciador.obter_informacoes_so.assert_called_once_with()


# --- EscanearDiretorioUseCase ------------------------------------------------


def test_escanear_caminho_fora_da_home_levanta_path_inseguro_error() -> None:
    """Garante que um caminho fora da Home é barrado antes de tocar o buscador."""
    buscador = MagicMock()
    caso_uso = EscanearDiretorioUseCase(buscador=buscador)

    with pytest.raises(PathInseguroError):
        caso_uso.executar(caminho_str=CAMINHO_FORA_DA_HOME)

    buscador.validar_pasta.assert_not_called()
    buscador.escanear.assert_not_called()


def test_escanear_caminho_seguro_mas_inexistente_levanta_diretorio_inexistente_error() -> None:
    """Garante 404 de domínio quando validar_pasta recusa o caminho seguro."""
    buscador = MagicMock()
    buscador.validar_pasta.return_value = False
    caso_uso = EscanearDiretorioUseCase(buscador=buscador)
    caminho_str = _caminho_seguro("PastaInexistente")

    with pytest.raises(DiretorioInexistenteError):
        caso_uso.executar(caminho_str=caminho_str)

    buscador.escanear.assert_not_called()


def test_escanear_caminho_seguro_e_valido_retorna_resultado_do_buscador() -> None:
    """Garante que o resultado do escaneamento é repassado sem alteração."""
    buscador = MagicMock()
    buscador.validar_pasta.return_value = True
    buscador.escanear.return_value = {"total_arquivos": 3}
    caso_uso = EscanearDiretorioUseCase(buscador=buscador)
    caminho_str: str = _caminho_seguro("Documentos")

    resultado = caso_uso.executar(caminho_str=caminho_str)

    assert resultado == {"total_arquivos": 3}
    buscador.escanear.assert_called_once_with(Path(caminho_str))


# --- ConverterFavoritosLoteUseCase ------------------------------------------


def test_converter_lista_vazia_nao_produz_nenhum_evento() -> None:
    """Garante que uma lista vazia de arquivos não gera nenhum yield."""
    caso_uso = _montar_conversor()

    eventos = list(
        caso_uso.executar_com_progresso(arquivos_selecionados=[], extensao_destino="json")
    )

    assert not eventos


def test_converter_arquivo_fora_da_home_gera_erro_de_acesso_proibido_sem_tocar_as_portas() -> None:
    """Garante que um arquivo inseguro vira erro e nenhuma porta física é chamada."""
    leitor, parser, escritor = MagicMock(), MagicMock(), MagicMock()
    caso_uso: ConverterFavoritosLoteUseCase = _montar_conversor(
        leitor=leitor, parser=parser, escritor=escritor
    )

    eventos = list(
        caso_uso.executar_com_progresso(
            arquivos_selecionados=[CAMINHO_FORA_DA_HOME], extensao_destino="json"
        )
    )

    assert len(eventos) == 1
    evento = eventos[0]
    assert evento["progresso"] == 100
    assert evento["concluido"] is True
    assert evento["sucesso"] is False
    assert evento["arquivos_convertidos"] == []
    assert evento["erros"] == [
        {"arquivo": "passwd", "erro": "Acesso proibido: O arquivo está em local inseguro."}
    ]
    leitor.ler_arquivo.assert_not_called()
    parser.extrair_favoritos.assert_not_called()
    escritor.salvar_lote.assert_not_called()


def test_converter_arquivo_seguro_com_favoritos_e_convertido_com_sucesso() -> None:
    """Garante o caminho feliz: leitura, parse, escrita e evento de sucesso."""
    caminho_str: str = _caminho_seguro(nome_arquivo="favoritos.html")
    favoritos: list[Favorito] = [Favorito(titulo="GitHub", url="https://github.com")]

    leitor = MagicMock()
    leitor.ler_arquivo.return_value = "<html>conteudo</html>"
    parser = MagicMock()
    parser.extrair_favoritos.return_value = favoritos
    escritor = MagicMock()
    escritor.salvar_lote.return_value = "/home/diaspedro/favoritos_processado.json"

    caso_uso: ConverterFavoritosLoteUseCase = _montar_conversor(
        leitor=leitor, parser=parser, escritor=escritor
    )

    eventos = list(
        caso_uso.executar_com_progresso(
            arquivos_selecionados=[caminho_str], extensao_destino="json"
        )
    )

    assert len(eventos) == 1
    evento = eventos[0]
    assert evento["progresso"] == 100
    assert evento["concluido"] is True
    assert evento["sucesso"] is True
    assert evento["erros"] == []
    assert evento["arquivos_convertidos"] == [
        {"origem": "favoritos.html", "destino": "favoritos_processado.json", "total_links": 1}
    ]

    leitor.ler_arquivo.assert_called_once_with(caminho=Path(caminho_str))
    parser.extrair_favoritos.assert_called_once_with("<html>conteudo</html>")
    escritor.salvar_lote.assert_called_once_with(
        caminho_original=Path(caminho_str),
        dados=[favoritos[0].to_dict()],
        extensao="json",
    )


def test_converter_arquivo_sem_favoritos_gera_erro_de_nenhum_favorito_encontrado() -> None:
    """Garante que uma lista de favoritos vazia gera erro em vez de gravação."""
    caminho_str: str = _caminho_seguro(nome_arquivo="vazio.html")
    leitor = MagicMock()
    leitor.ler_arquivo.return_value = "<html></html>"
    parser = MagicMock()
    parser.extrair_favoritos.return_value = []
    escritor = MagicMock()

    caso_uso: ConverterFavoritosLoteUseCase = _montar_conversor(
        leitor=leitor, parser=parser, escritor=escritor
    )

    eventos = list(
        caso_uso.executar_com_progresso(
            arquivos_selecionados=[caminho_str], extensao_destino="json"
        )
    )

    evento = eventos[0]
    assert evento["sucesso"] is False
    assert evento["erros"] == [
        {"arquivo": "vazio.html", "erro": "Nenhum favorito válido foi encontrado no HTML."}
    ]
    escritor.salvar_lote.assert_not_called()


def test_converter_falha_na_leitura_e_capturada_e_vira_erro_de_processamento() -> None:
    """Garante que uma exceção do leitor não propaga e vira um erro no evento."""
    caminho_str = _caminho_seguro("corrompido.html")
    leitor = MagicMock()
    leitor.ler_arquivo.side_effect = OSError("disco cheio")
    caso_uso: ConverterFavoritosLoteUseCase = _montar_conversor(leitor=leitor)

    eventos = list(
        caso_uso.executar_com_progresso(
            arquivos_selecionados=[caminho_str], extensao_destino="json"
        )
    )

    evento = eventos[0]
    assert evento["sucesso"] is False
    assert evento["erros"] == [
        {"arquivo": "corrompido.html", "erro": "Falha no processamento: disco cheio"}
    ]


def test_converter_lote_com_varios_arquivos_produz_evento_por_arquivo_com_progresso_crescente() -> (
    None
):
    """Garante um evento por arquivo, progresso proporcional e 'concluido' só no último."""
    caminhos: list[str] = [_caminho_seguro(f"arquivo_{i}.html") for i in range(4)]
    leitor = MagicMock()
    leitor.ler_arquivo.return_value = "<html></html>"
    parser = MagicMock()
    parser.extrair_favoritos.return_value = [Favorito(titulo="X", url="https://x.com")]
    escritor = MagicMock()
    escritor.salvar_lote.return_value = "/home/diaspedro/saida.json"

    caso_uso: ConverterFavoritosLoteUseCase = _montar_conversor(
        leitor=leitor, parser=parser, escritor=escritor
    )

    eventos: list[dict] = list(
        caso_uso.executar_com_progresso(arquivos_selecionados=caminhos, extensao_destino="json")
    )

    assert len(eventos) == 4
    assert [evento["progresso"] for evento in eventos] == [25, 50, 75, 100]
    assert [evento["concluido"] for evento in eventos] == [False, False, False, True]
    assert eventos[-1]["arquivos_convertidos"][-1]["origem"] == "arquivo_3.html"


def test_converter_sucesso_permanece_true_apos_uma_conversao_bem_sucedida_no_lote() -> None:
    """Garante que, uma vez convertido um arquivo, 'sucesso' segue True nos eventos seguintes.

    Esse é o comportamento real do código (sucesso = há êxitos acumulados até aqui),
    não uma flag por-arquivo isolada — documentado aqui para não regredir sem perceber.
    """
    caminho_ok: str = _caminho_seguro("ok.html")
    caminho_ruim = CAMINHO_FORA_DA_HOME

    leitor = MagicMock()
    leitor.ler_arquivo.return_value = "<html></html>"
    parser = MagicMock()
    parser.extrair_favoritos.return_value = [Favorito(titulo="X", url="https://x.com")]
    escritor = MagicMock()
    escritor.salvar_lote.return_value = "/home/diaspedro/ok_processado.json"

    caso_uso: ConverterFavoritosLoteUseCase = _montar_conversor(
        leitor=leitor, parser=parser, escritor=escritor
    )

    eventos = list(
        caso_uso.executar_com_progresso(
            arquivos_selecionados=[caminho_ok, caminho_ruim], extensao_destino="json"
        )
    )

    assert eventos[0]["sucesso"] is True
    assert eventos[1]["sucesso"] is True
    assert isinstance(eventos[1]["erros"], list)
    assert len(eventos[1]["erros"]) == 1
