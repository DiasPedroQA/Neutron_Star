"""Testes do gerenciamento do sistema e da varredura local de arquivos."""

from pathlib import Path

import pytest

from src.models.buscador import BuscadorLocal, GerenciadorSistemaLocal
from src.models.entidades import ResultadoEscaneamento


class TestGerenciadorSistemaLocal:
    """Contrato dos dados ambientais e dos atalhos sugeridos."""

    def test_obter_informacoes_so_retorna_dados_e_pastas_existentes(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Inclui atalhos padrão, pastas existentes e os dados do ambiente."""
        home: Path = tmp_path / "usuario"
        (home / "Downloads").mkdir(parents=True)
        monkeypatch.setattr(Path, "home", lambda: home)
        monkeypatch.setattr("src.models.buscador.getpass.getuser", lambda: "ana")
        monkeypatch.setattr("src.models.buscador.platform.system", lambda: "Linux")
        monkeypatch.setattr("src.models.buscador.platform.release", lambda: "6.1")

        resultado = GerenciadorSistemaLocal.obter_informacoes_so()

        assert resultado["so"] == "Linux (6.1)"
        assert resultado["usuario"] == "ana"
        assert resultado["pasta_home"] == str(home)
        assert resultado["atalhos_sugeridos"] == [
            {"label": "Pasta Home (~/)", "caminho": "~/"},
            {"label": f"Downloads ({home}/Downloads)", "caminho": "~/Downloads"},
            {"label": "Outro Caminho...", "caminho": "editável"},
        ]


class TestBuscadorLocal:
    """Contrato da validação de pasta e da varredura hierárquica."""

    def test_construtor_guarda_limite_de_arquivos(self) -> None:
        """Permite configurar o limite máximo de arquivos examinados."""
        buscador = BuscadorLocal(max_arquivos=12)

        assert buscador.max_arquivos == 12

    def test_validar_pasta_reconhece_diretorio_e_rejeita_arquivo(self, tmp_path: Path) -> None:
        """Aceita diretórios válidos e rejeita arquivos e caminhos ausentes."""
        arquivo: Path = tmp_path / "arquivo.html"
        arquivo.write_text("conteúdo", encoding="utf-8")
        buscador = BuscadorLocal()

        assert buscador.validar_pasta(tmp_path) is True
        assert buscador.validar_pasta(arquivo) is False
        assert buscador.validar_pasta(tmp_path / "inexistente") is False

    def test_escanear_filtra_extensao_profundidade_e_monta_arvore(self, tmp_path: Path) -> None:
        """Retorna metadados e árvore somente dos arquivos dentro da profundidade."""
        pasta_filha: Path = tmp_path / "Documentos"
        pasta_filha.mkdir()
        (tmp_path / "a.html").write_text("<DL><DT>favorito</DT></DL>", encoding="utf-8")
        (tmp_path / "b.txt").write_text("ignorado", encoding="utf-8")
        (pasta_filha / "c.HTML").write_text("<html></html>", encoding="utf-8")
        (pasta_filha / "d.htm").write_text("<html></html>", encoding="utf-8")
        (tmp_path / ".oculto.html").write_text("oculto", encoding="utf-8")
        (tmp_path / ".privada").mkdir()
        (tmp_path / ".privada" / "e.html").write_text("oculto", encoding="utf-8")

        resultado: ResultadoEscaneamento = BuscadorLocal().escanear(
            caminho=tmp_path,
            extensao="todos",
            profundidade=1,
        )

        assert resultado["total_arquivos"] == 3
        assert resultado["total_elegiveis"] == 1
        assert resultado["extensao_usada"] == ".html,.htm"
        assert {item["nome"] for item in resultado["arquivos"]} == {
            "a.html",
            "c.HTML",
            "d.htm",
        }
        nomes_raiz: list[str] = [no.get("name", "") for no in resultado["tree"]]
        assert nomes_raiz == ["Documentos", "a.html"]

    def test_escanear_limita_profundidade_e_normaliza_valor_negativo(self, tmp_path: Path) -> None:
        """Profundidade negativa equivale à raiz, sem percorrer subpastas."""
        (tmp_path / "raiz.html").write_text("<html></html>", encoding="utf-8")
        subpasta: Path = tmp_path / "subpasta"
        subpasta.mkdir()
        (subpasta / "filho.html").write_text("<html></html>", encoding="utf-8")

        resultado: ResultadoEscaneamento = BuscadorLocal().escanear(
            caminho=tmp_path,
            profundidade=-1,
        )

        assert resultado["profundidade_usada"] == 0
        assert [item["nome"] for item in resultado["arquivos"]] == ["raiz.html"]

    def test_escanear_caminho_invalido_lanca_file_not_found(self, tmp_path: Path) -> None:
        """Expõe erro claro quando a raiz informada não é uma pasta existente."""
        buscador = BuscadorLocal()

        with pytest.raises(FileNotFoundError, match="não pôde ser encontrada"):
            buscador.escanear(caminho=tmp_path / "inexistente")
