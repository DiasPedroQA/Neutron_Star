# Atoms/main.py

"""Ponto de entrada único para rodar com 'python main.py'."""

import uvicorn


def main() -> None:
    """Inicializa o servidor Uvicorn."""
    uvicorn.run(
        app="montagem.composicao:app",
        host="127.0.0.1",  # Segurança: não expõe por padrão em todas as interfaces
        port=8000,
        reload=True,
    )


if __name__ == "__main__":  # pragma: no cover - ponto de entrada do script
    main()
