# Atoms/composicao.py

"""Composition Root: montagem da aplicação FastAPI."""

from fastapi import FastAPI
from src.api import router

app = FastAPI(title="Neutron Star - API Unificada")
app.include_router(router)
