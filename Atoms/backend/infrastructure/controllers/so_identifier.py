# Atoms/backend/infrastructure/controllers/so_identifier.py

"""Módulo de identificação do sistema operacional local."""

import logging
import platform
from pathlib import Path

from backend.core.entidades.entidade_sistema_operacional import (
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
        logger.debug("Obtendo nome do sistema operacional...")
        try:
            nome: str = platform.system().lower()
            logger.debug("Nome do sistema detectado: %s", nome)
            return nome
        except Exception:
            logger.exception("Erro ao obter o nome do sistema operacional.")
            raise

    def obter_versao_sistema(self) -> str:
        """Obtém a versão do sistema operacional local.
        A versão retornada é uma representação simples fornecida pela plataforma.

        Returns:
            str: Versão do sistema operacional atual.
        """
        logger.debug("Obtendo versão do sistema operacional...")
        try:
            versao: str = platform.release()
            logger.debug("Versão do sistema detectada: %s", versao)
            return versao
        except Exception:
            logger.exception("Erro ao obter a versão do sistema operacional.")
            raise

    def obter_pasta_usuario(self) -> Path:
        """Obtém o diretório home do usuário como Path."""
        logger.debug("Obtendo diretório home do usuário...")
        try:
            caminho: Path = Path.home()
            logger.debug("Diretório home: %s", caminho)
            return caminho
        except Exception:
            logger.exception("Erro ao obter o diretório home do usuário.")
            raise

    def detectar_sistema_operacional(self) -> ModeloSistemaOperacional:
        """Cria um modelo representando o sistema operacional local.
        O modelo inclui informações básicas como nome, versão e diretório home do usuário.

        Returns:
            ModeloSistemaOperacional: Instância preenchida com os dados do
            sistema operacional detectado.
        """
        logger.info("Iniciando detecção do sistema operacional...")

        nome = self.obter_nome_sistema()
        versao = self.obter_versao_sistema()
        home = self.obter_pasta_usuario()

        modelo = ModeloSistemaOperacional(
            nome_sistema=nome,
            versao_sistema=versao,
            pasta_usuario=home,
        )

        logger.debug("Modelo criado com sucesso: %s", modelo)
        logger.info(
            "Sistema operacional detectado: %s - %s",
            modelo.nome_sistema,
            modelo.versao_sistema,
        )
        return modelo
