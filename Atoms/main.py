# Atoms/main.py

"""Ponto de entrada único para rodar com 'python main.py'."""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(app="montagem.composicao:app", host="0.0.0.0", port=8000, reload=True)
