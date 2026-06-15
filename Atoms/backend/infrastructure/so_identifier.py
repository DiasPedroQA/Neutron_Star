"""Módulo de identificação do sistema operacional local."""

import logging
import platform
from pathlib import Path

from Atoms.backend.core.entidades.entidade_sistema_operacional import (
    ModeloSistemaOperacional,
)

logger: logging.Logger = logging.getLogger(name=__name__)


class DetectarSistemaOperacional:
    """Identifica o sistema operacional local e fornece modelos de domínio."""

    def obter_nome_sistema(self) -> str:
        """Obtém o nome do sistema operacional local em letras minúsculas.
        O nome retornado identifica genericamente a família do sistema operacional.

        Returns:
            str: Nome do sistema operacional atual em formato normalizado.
        """
        nome: str = platform.system().lower()
        logger.debug("Nome do sistema detectado: %s", nome)
        return nome

    def obter_versao_sistema(self) -> str:
        """Obtém a versão do sistema operacional local.
        A versão retornada é uma representação simples fornecida pela plataforma.

        Returns:
            str: Versão do sistema operacional atual.
        """
        versao: str = platform.release()
        logger.debug("Versão do sistema detectada: %s", versao)
        return versao

    def obter_pasta_usuario(self) -> Path:
        """Obtém o diretório home do usuário como Path."""
        caminho: Path = Path.home()
        logger.debug("Diretório home: %s", caminho)
        return caminho

    def detectar_sistema_operacional(self) -> ModeloSistemaOperacional:
        """Cria um modelo representando o sistema operacional local.
        O modelo inclui informações básicas como nome, versão e diretório home do usuário.

        Returns:
            ModeloSistemaOperacional: Instância preenchida com os dados do
            sistema operacional detectado.
        """
        modelo = ModeloSistemaOperacional(
            nome_sistema=self.obter_nome_sistema(),
            versao_sistema=self.obter_versao_sistema(),
            pasta_usuario=self.obter_pasta_usuario(),
        )
        logger.info(
            "Sistema operacional detectado: %s %s",
            modelo.nome_sistema,
            modelo.versao_sistema,
        )
        return modelo
