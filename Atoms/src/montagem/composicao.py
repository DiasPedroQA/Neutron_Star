# Atoms/src/composicao.py

"""Composition Root e metadados públicos da aplicação FastAPI."""

from adaptadores.api import router
from fastapi import FastAPI

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
    },
    license_info={"name": "GPL-3.0-only", "identifier": "GPL-3.0-only"},
)
app.include_router(router)
