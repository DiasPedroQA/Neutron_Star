"""Testes dos formatadores e da resolução de destinos de exportação."""

import csv
import json
from pathlib import Path

import pytest

from src.models.entidades import FavoritoDict
from src.models.escritores import (
    EscritorLocal,
    FormatadorCSV,
    FormatadorJSON,
    FormatadorMarkdown,
)


def _favorito() -> FavoritoDict:
    """Cria um favorito válido para os exemplos dos formatadores."""
    return {
        "titulo": "Título | exemplo",
        "url": "https://exemplo.com",
        "pasta": "Pessoal|Leitura",
        "data_adicao": "01/01/2026",
    }


class TestFormatadorJSON:
    """Contrato de gravação JSON."""

    def test_salvar_grava_lista_unicode_formatada(self, tmp_path: Path) -> None:
        """Cria a pasta de destino e preserva os valores serializados."""
        destino: Path = tmp_path / "saida" / "favoritos.json"

        FormatadorJSON().salvar(destino, [_favorito()])

        assert json.loads(destino.read_text(encoding="utf-8")) == [_favorito()]
        assert "\n    " in destino.read_text(encoding="utf-8")


class TestFormatadorCSV:
    """Contrato de gravação CSV com delimitador e codificação compatíveis."""

    def test_salvar_grava_cabecalho_e_linhas_com_ponto_e_virgula(self, tmp_path: Path) -> None:
        """Gera um CSV legível por Excel com as quatro colunas do favorito."""
        destino: Path = tmp_path / "saida" / "favoritos.csv"

        FormatadorCSV().salvar(destino, [_favorito()])

        with destino.open(encoding="utf-8-sig", newline="") as arquivo:
            linhas = list(csv.DictReader(arquivo, delimiter=";"))

        assert linhas == [_favorito()]

    def test_salvar_lista_vazia_cria_diretorio_sem_arquivo(self, tmp_path: Path) -> None:
        """Mantém o contrato atual do formatador quando não há linhas para gravar."""
        destino: Path = tmp_path / "saida" / "vazio.csv"

        FormatadorCSV().salvar(destino, [])

        assert destino.parent.is_dir()
        assert not destino.exists()


class TestFormatadorMarkdown:
    """Contrato básico da tabela Markdown, sem repetir os casos de BUG-003."""

    def test_salvar_grava_tabela_e_normaliza_pipe_em_titulo_e_pasta(self, tmp_path: Path) -> None:
        """Preserva a tabela de quatro colunas para título e pasta com pipe."""
        destino: Path = tmp_path / "saida" / "favoritos.md"

        FormatadorMarkdown().salvar(destino, [_favorito()])

        conteudo: str = destino.read_text(encoding="utf-8")
        assert "# 📑 Favoritos Exportados" in conteudo
        assert "*Total de links processados: 1*" in conteudo
        assert "[Título - exemplo](https://exemplo.com)" in conteudo
        assert "Pessoal/Leitura" in conteudo


class TestEscritorLocal:
    """Contrato de seleção de formato e construção do caminho de saída."""

    def test_gerar_caminho_destino_normaliza_extensao_e_pasta_saida(self, tmp_path: Path) -> None:
        """Usa o nome-base original e normaliza a extensão informada."""
        origem: Path = tmp_path / "origem" / "Favoritos.HTML"
        pasta_saida: Path = tmp_path / "exportados"

        destino: Path = EscritorLocal.gerar_caminho_destino(
            caminho_original=origem,
            extensao=".JSON",
            pasta_saida=pasta_saida,
        )

        assert destino == pasta_saida.resolve() / "Favoritos_processado.json"

    @pytest.mark.parametrize(
        ("extensao", "sufixo_esperado"),
        [
            pytest.param("csv", "Favoritos_processado.csv", id="csv"),
            pytest.param("md", "Favoritos_processado.md", id="markdown"),
        ],
    )
    def test_gerar_caminho_destino_sem_pasta_saida(
        self, tmp_path: Path, extensao: str, sufixo_esperado: str
    ) -> None:
        """Salva junto ao arquivo original quando a pasta não é especificada."""
        origem: Path = tmp_path / "Favoritos.html"

        destino: Path = EscritorLocal.gerar_caminho_destino(origem, extensao)

        assert destino == tmp_path.resolve() / sufixo_esperado

    @pytest.mark.parametrize(
        ("dados", "extensao", "mensagem"),
        [
            pytest.param([], "json", "Não há dados para exportar", id="lote-vazio"),
            pytest.param([_favorito()], "xml", "não suportado", id="formato-desconhecido"),
        ],
    )
    def test_salvar_lote_rejeita_entrada_invalida(
        self,
        tmp_path: Path,
        dados: list[FavoritoDict],
        extensao: str,
        mensagem: str,
    ) -> None:
        """Falha com mensagem de domínio para lote vazio ou extensão desconhecida."""
        escritor = EscritorLocal()
        caminho_original: Path = tmp_path / "Favoritos.html"

        with pytest.raises(ValueError, match=mensagem):
            escritor.salvar_lote(
                caminho_original=caminho_original,
                dados=dados,
                extensao=extensao,
            )

    @pytest.mark.parametrize("extensao", ["json", "csv", "md", "markdown"])
    def test_salvar_lote_delega_ao_formatador_e_retorna_destino(
        self, tmp_path: Path, extensao: str
    ) -> None:
        """Persiste nos quatro aliases públicos de formato e retorna o caminho."""
        origem: Path = tmp_path / "Favoritos.html"

        destino: str = EscritorLocal().salvar_lote(origem, [_favorito()], extensao)

        caminho_destino: Path = Path(destino)
        assert caminho_destino.is_file()
        assert caminho_destino.suffix == f".{extensao}"
