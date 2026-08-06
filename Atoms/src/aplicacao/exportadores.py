"""Escritores de formato de saída para o DataFrame de bookmarks (I/O)."""

from __future__ import annotations

import json
from collections.abc import Callable, Hashable
from pathlib import Path
from typing import Any

from pandas import DataFrame


def write_csv(df: DataFrame, output_path: Path) -> None:
    """Salva o DataFrame em formato CSV."""
    df.to_csv(path_or_buf=output_path, index=False)


def write_json(df: DataFrame, output_path: Path) -> None:
    """Salva o DataFrame em formato JSON, sem escapar barras nas URLs."""
    dados: list[dict[Hashable, Any]] = df.to_dict(orient="records")
    json_str: str = json.dumps(dados, ensure_ascii=False, indent=2).replace("\\/", "/")
    with open(file=output_path, mode="w", encoding="utf-8") as f:
        f.write(json_str)


def write_parquet(df: DataFrame, output_path: Path) -> None:
    """Salva o DataFrame em formato Parquet."""
    df.to_parquet(path=output_path, index=False)


def write_xml(df: DataFrame, output_path: Path) -> None:
    """Salva o DataFrame em formato XML."""
    df.to_xml(path_or_buffer=output_path, index=False, root_name="bookmarks", row_name="link")


def write_md(df: DataFrame, output_path: Path) -> None:
    """Salva o DataFrame como uma tabela Markdown."""
    with open(file=output_path, mode="w", encoding="utf-8") as f:
        f.write(df.to_markdown(index=False))


# Mapeamento de extensões para funções de escrita
WRITERS: dict[str, Callable[[DataFrame, Path], None]] = {
    ".csv": write_csv,
    ".json": write_json,
    ".parquet": write_parquet,
    ".xml": write_xml,
    ".md": write_md,
}
