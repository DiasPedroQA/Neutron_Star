# Atoms/main.py

"""Ponto de entrada único para rodar com 'python main.py'."""

import uvicorn

from src.composicao import app

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
