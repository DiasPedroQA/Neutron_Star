"""Testes do ponto de entrada da CLI (main.py)."""

from pathlib import Path

from pytest import CaptureFixture

_HTML_VALIDO = """
<DL><p>
    <DT><A HREF="https://a.com">Site A</A>
</DL><p>
"""


class TestConstruirParser:
    """Configuração e valores padrão do parser de linha de comando."""

    def test_valores_padrao_quando_nenhum_argumento_informado(self) -> None:
        """Sem argumentos, os padrões documentados devem ser aplicados."""
        ...

    def test_lote_pode_ser_ativado_por_comando(self) -> None:
        """O comando 'lote' deve ser reconhecido, não uma flag."""
        ...


class TestMontarContexto:
    """Conversão dos argumentos da CLI em ParametrosBusca."""

    def test_contexto_reflete_os_argumentos_informados(self, tmp_path: Path) -> None:
        """Cada argumento informado deve aparecer com o mesmo valor no contexto."""
        ...


class TestMainModoPadrao:
    """Execução do pipeline completo (buscar -> selecionar -> extrair -> exportar)."""

    def test_processa_arquivo_unico_encontrado(self, tmp_path: Path) -> None:
        """Com um arquivo válido no diretório, o pipeline deve gerar a exportação."""
        ...


class TestMainModoLote:
    """Execução do modo lote (processa todos os arquivos encontrados)."""

    def test_processa_todos_os_arquivos_encontrados(self, tmp_path: Path) -> None:
        """Múltiplos arquivos encontrados devem virar múltiplas exportações no lote."""
        ...

    def test_nenhum_arquivo_encontrado_nao_quebra(self, tmp_path: Path, capsys: CaptureFixture[str]) -> None:
        """Sem arquivos encontrados, deve avisar e retornar, sem lançar exceção."""
        ...


class TestEntryPointInstalado:
    """Integração real: sobe o comando 'neutron' como um processo de verdade.

    Diferente dos testes acima (que chamam main() em processo), este spawna
    o interpretador Python de verdade e importa 'main' do zero — pega bugs
    de instalação/entry-point que uma chamada direta a main() nunca pegaria
    (foi assim, manualmente, que achamos o bug do entry point quebrado antes;
    isso automatiza aquela checagem).
    """

    def test_modulo_main_roda_via_subprocesso(self, tmp_path: Path) -> None:
        """`python -m main buscar` deve rodar de ponta a ponta como processo real."""
        (tmp_path / "bookmarks_favoritos.html").write_text(data=_HTML_VALIDO, encoding="utf-8")
        ...
