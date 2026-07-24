"""Testes do adaptador de API (adaptadores/api/app.py).

Verificam que a API é uma casca fina sobre o mesmo núcleo usado pela CLI:
os mesmos cenários (busca, exportação, falha) devem se comportar igual.
"""

from pathlib import Path

from adaptadores.api.app import app
from fastapi.testclient import TestClient

_HTML_VALIDO = """
<DL><p>
    <DT><A HREF="https://a.com">Site A</A>
</DL><p>
"""

cliente = TestClient(app)


class TestHealth:
    """Endpoint de verificação de disponibilidade."""

    def test_retorna_status_ok(self) -> None:
        """GET /health deve responder 200 com status 'ok'."""
        resposta = cliente.get("/health")

        assert resposta.status_code == 200
        assert resposta.json() == {"status": "ok"}


class TestBuscar:
    """POST /bookmarks/buscar — mesmo comportamento de aplicacao.etapas.etapa_buscar."""

    def test_encontra_arquivos_que_atendem_aos_filtros(self, tmp_path: Path) -> None:
        """Arquivo que bate com extensão e chave deve aparecer na resposta."""
        (tmp_path / "bookmarks_trabalho.html").write_text(_HTML_VALIDO, encoding="utf-8")

        resposta = cliente.post(
            url="/bookmarks/buscar",
            json={"diretorio": str(tmp_path), "chaves": ["trabalho"]},
        )

        assert resposta.status_code == 200
        encontrados: str = resposta.json()["arquivos_encontrados"]
        assert str(tmp_path / "bookmarks_trabalho.html") in encontrados

    def test_diretorio_invalido_retorna_erro_422(self, tmp_path: Path) -> None:
        """Diretório inexistente deve virar HTTP 422, não um 500 genérico."""
        resposta = cliente.post(
            url="/bookmarks/buscar",
            json={"diretorio": str(tmp_path / "nao_existe")},
        )

        assert resposta.status_code == 422


class TestProcessarLote:
    """POST /bookmarks/lote — mesmo comportamento do modo --lote da CLI."""

    def test_processa_arquivos_e_retorna_resumo(self, tmp_path: Path) -> None:
        """Arquivos válidos devem ser exportados e contabilizados como sucesso."""
        arquivo: Path = tmp_path / "bookmarks.html"
        arquivo.write_text(data=_HTML_VALIDO, encoding="utf-8")
        saida: Path = tmp_path / "saida"

        resposta = cliente.post(
            url="/bookmarks/lote",
            json={
                "arquivos": [str(arquivo)],
                "formatos": [".json"],
                "diretorio_saida": str(saida),
            },
        )

        assert resposta.status_code == 200
        corpo = resposta.json()
        assert corpo == {"total": 1, "sucesso": 1, "falhas": {}}
        assert (saida / "bookmarks.json").exists()

    def test_arquivo_invalido_aparece_em_falhas_sem_quebrar_a_requisicao(self, tmp_path: Path) -> None:
        """Um arquivo inválido deve aparecer em 'falhas', com resposta 200 (não 500)."""
        invalido: Path = tmp_path / "invalido.html"
        invalido.write_text(data="<html>sem bookmarks</html>", encoding="utf-8")

        resposta = cliente.post(
            url="/bookmarks/lote",
            json={"arquivos": [str(invalido)], "formatos": [".json"]},
        )

        assert resposta.status_code == 200
        corpo = resposta.json()
        assert corpo["sucesso"] == 0
        assert str(invalido) in corpo["falhas"]
