# Atoms/frontend/cli/main.py

"""Ponto de entrada CLI para o Neutron Star."""

import sys
from pathlib import Path
from typing import Any

from Atoms.backend.core.entities import ModeloSistemaOperacional
from Atoms.backend.infrastructure.exporters import CSVExporter, JSONExporter, PDFExporter
from Atoms.backend.infrastructure.identifier import detectar_sistema_operacional
from Atoms.backend.infrastructure.scanners import FileSystemScanner
from Atoms.frontend.cli.display import exibir_pasta, exibir_sistema_operacional

# Adiciona Atoms ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def main() -> None:  # sourcery skip: extract-method
    """Função principal do CLI."""
    # Cria scanner (pode ser uma única instância)
    scanner = FileSystemScanner()

    # Detecta SO
    so: ModeloSistemaOperacional = detectar_sistema_operacional()
    exibir_sistema_operacional(
        nome_sistema=so.nome_sistema,
        versao_sistema=so.versao_sistema,
        caminho_pasta_home=str(so.user_home),
    )

    # Diretório a escanear (padrão: home)
    print(f"\nEscaneando: {so.user_home}\n")

    # Processa
    bookmarks: list[dict[str, Any]] = scanner.scan_and_process(root_path=so.user_home)

    # Exibe estrutura
    exibir_pasta(
        nome_pasta=pasta_root.nome_pasta,
        caminho_pasta=str(pasta_root.caminho_pasta),
        pasta_pai=pasta_root.pasta_pai,
        subpastas=pasta_root.subpastas,
        subarquivos=pasta_root.arquivos,
        titulo="Pasta Root",
    )

    # Exibe alguns bookmarks
    print(f"\n📚 Total de bookmarks encontrados: {len(bookmarks)}")
    if bookmarks:
        print("\nPrimeiros 5 bookmarks:")
        for i, bm in enumerate(iterable=bookmarks[:5], start=1):
            print(f"  {i}. {bm.get('title', 'Sem título')}")
            print(f"     {bm.get('url', 'Sem URL')}")

    # Pergunta se quer exportar
    if bookmarks:
        print("\nDeseja exportar os bookmarks?")
        print("1. JSON")
        print("2. CSV")
        print("3. PDF")
        print("4. Não exportar")

        opcao: str = input("Escolha (1-4): ").strip()

        exporters: dict[
            str, tuple[str, JSONExporter] | tuple[str, CSVExporter] | tuple[str, PDFExporter]
        ] = {
            "1": ("bookmarks.json", JSONExporter()),
            "2": ("bookmarks.csv", CSVExporter()),
            "3": ("bookmarks.pdf", PDFExporter()),
        }

        if opcao in exporters:
            nome_arquivo, exporter = exporters[opcao]
            exporter.export(bookmarks=bookmarks, saida=Path(nome_arquivo))
            print(f"✅ Exportado para {nome_arquivo}")


if __name__ == "__main__":
    main()
