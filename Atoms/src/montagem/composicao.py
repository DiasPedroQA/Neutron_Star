# Atoms/src/montagem/composicao.py

"""Composition Root e metadados públicos da aplicação FastAPI."""

import logging
import os
from pathlib import Path

from fastapi import FastAPI

from src.adaptadores.api import router

# para testes, mas não é bom para produção
BASE_DIR = Path(os.getenv(key="NEUTRON_STAR_BASE_DIR", default="~/Downloads/temp"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger: logging.Logger = logging.getLogger(name=__name__)

app: FastAPI = FastAPI(
    title="Neutron Star — API de Bookmarks",
    summary="Localize arquivos HTML de bookmarks e extraia seus links.",
    description=(
        "A API opera sobre arquivos já presentes no sistema onde o servidor é executado.\n\n"
        "- Use **Listar arquivos HTML** para localizar candidatos.\n"
        "- Use **Extrair bookmarks de um arquivo** para processar um caminho específico.\n"
        "- Use **Localizar arquivos e extrair bookmarks** para executar o fluxo completo.\n\n"
        "A API não faz upload de arquivos nem possui autenticação; "
        "execute-a apenas em ambientes confiáveis."
    ),
    version="0.1.0",
    contact={
        "name": "DiasPedroQA",
        "url": "https://github.com/DiasPedroQA/Neutron_Star",
        "e-mail": "diaspedro.dev@gmail.com",
    },
    license_info={"name": "GPL-3.0-only", "identifier": "GPL-3.0-only"},
)
app.include_router(router)

logger.info(msg="Inicializando Neutron_Star API...")
