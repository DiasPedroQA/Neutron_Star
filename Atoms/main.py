# Atoms/main.py

"""Ponto de entrada único para rodar com 'python main.py'."""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(app="montagem.composicao:app", host="127.0.0.1", port=8000, reload=True)
