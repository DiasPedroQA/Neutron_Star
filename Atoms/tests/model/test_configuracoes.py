"""Testes para o modelo de configurações ConfigApp.

Verifica a criação, atributos padrão, personalização e métodos
de serialização (pendentes).
"""

from pathlib import Path

import pytest

from src.models.configuracoes import ConfigApp


class TestConfigApp:
    """Suite de testes para a classe ConfigApp."""

    def test_valores_padrao(self) -> None:
        """Verifica que os valores padrão são definidos corretamente."""
        config = ConfigApp()

        assert config.case_sensitive is True
        assert config.executavel_por_extensao is False
        assert not config.extensoes_executaveis
        assert config.ignorar_ocultos is True
        assert config.seguir_symlinks is False
        assert config.profundidade_maxima == -1
        assert config.calcular_hashes is False
        assert config.padroes_exclusao == [r"\.git", r"__pycache__", r".*\.pyc"]
        assert not config.caminhos_indexados

    def test_personalizacao_campos(self) -> None:
        """Verifica que os campos podem ser personalizados na criação."""
        config = ConfigApp(
            case_sensitive=False,
            executavel_por_extensao=True,
            extensoes_executaveis=[".exe", ".bat", ".cmd"],
            ignorar_ocultos=False,
            seguir_symlinks=True,
            profundidade_maxima=3,
            calcular_hashes=True,
            padroes_exclusao=[r"\.tmp", r"\.log"],
            caminhos_indexados=[Path("/home/user/docs"), Path("/var/data")],
        )

        assert config.case_sensitive is False
        assert config.executavel_por_extensao is True
        assert config.extensoes_executaveis == [".exe", ".bat", ".cmd"]
        assert config.ignorar_ocultos is False
        assert config.seguir_symlinks is True
        assert config.profundidade_maxima == 3
        assert config.calcular_hashes is True
        assert config.padroes_exclusao == [r"\.tmp", r"\.log"]
        assert config.caminhos_indexados == [Path("/home/user/docs"), Path("/var/data")]

    def test_extensoes_executaveis_sao_lista_isolada(self) -> None:
        """Garante que a lista de extensões executáveis é uma nova lista por instância."""
        config1 = ConfigApp()
        config2 = ConfigApp()

        config1.extensoes_executaveis.append(".sh")
        assert ".sh" in config1.extensoes_executaveis
        assert ".sh" not in config2.extensoes_executaveis

    def test_padroes_exclusao_sao_lista_isolada(self) -> None:
        """Garante que a lista de padrões de exclusão é uma nova lista por instância."""
        config1 = ConfigApp()
        config2 = ConfigApp()

        config1.padroes_exclusao.append(r"\.env")
        assert r"\.env" in config1.padroes_exclusao
        assert r"\.env" not in config2.padroes_exclusao

    def test_caminhos_indexados_aceita_paths(self) -> None:
        """Verifica que caminhos_indexados pode receber objetos Path."""
        caminhos: list[Path] = [Path("/a"), Path("/b/c")]
        config = ConfigApp(caminhos_indexados=caminhos)
        assert config.caminhos_indexados == caminhos
        assert all(isinstance(p, Path) for p in config.caminhos_indexados)

    def test_carregar_de_arquivo_nao_implementado(self) -> None:
        """Verifica que o método levanta NotImplementedError."""
        with pytest.raises(expected_exception=NotImplementedError):
            ConfigApp.carregar_de_arquivo(caminho=Path("/tmp/config.yaml"))

    def test_salvar_em_arquivo_nao_implementado(self) -> None:
        """Verifica que o método levanta NotImplementedError."""
        config = ConfigApp()
        with pytest.raises(expected_exception=NotImplementedError):
            config.salvar_em_arquivo(caminho=Path("/tmp/config.yaml"))

    def test_mutabilidade_dos_atributos(self) -> None:
        """Verifica que os atributos podem ser alterados após a criação (não é frozen)."""
        config = ConfigApp()
        config.case_sensitive = False
        config.profundidade_maxima = 5
        assert not config.case_sensitive
        assert config.profundidade_maxima == 5

    def test_extensoes_executaveis_por_padrao_vazio(self) -> None:
        """Confirma que a lista de extensões executáveis começa vazia."""
        config = ConfigApp()
        assert not config.extensoes_executaveis
