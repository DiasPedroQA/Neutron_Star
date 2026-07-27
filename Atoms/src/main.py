#!/usr/bin/env python3

"""
Ponto de entrada principal do Neutron Star.

Fornece API programática para:
- Busca de arquivos de bookmarks
- Extração da árvore
- Exportação em múltiplos formatos
- Processamento em lote
"""

from __future__ import annotations

import logging
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from aplicacao.casos_de_uso.processar_lote import processar_arquivos_em_lote
from aplicacao.tipos import ParametrosBusca
from dominio.excecoes import ErroBookmarks
from orquestracao import (
    DEFAULT_FORMATOS,
    PipelineBuilder,
    criar_contexto,
    executar_pipeline_basico,
    executar_pipeline_condicional,
)

logger: logging.Logger = logging.getLogger(name=__name__)


# -----------------------------------------------------------------------------
# Auxiliares internas (nomes únicos)
# -----------------------------------------------------------------------------
def _normalizar_saida(caminho: Path | str | None) -> Path:
    """Converte entrada para Path, usando '.' se None."""
    return Path(".") if caminho is None else Path(caminho)


def _obter_nome_raiz(contexto: Any) -> str:
    """Extrai o nome da raiz de bookmarks de um contexto ou objeto de raiz."""
    raiz: Any = None

    raiz = contexto.get("raiz_bookmarks", None) if hasattr(contexto, "get") or isinstance(contexto, dict) else contexto

    if raiz is None:
        return "N/A"
    if hasattr(raiz, "nome"):
        return str(raiz.nome)
    return str(raiz.get("nome", "N/A")) if isinstance(raiz, dict) else str(raiz)


def _buscar_arquivos(ctx: ParametrosBusca) -> list[Path]:
    """Executa a etapa de busca e atualiza o contexto."""
    resultado: ParametrosBusca = executar_pipeline_basico(contexto=ctx)
    arquivos: list[Path] = resultado.get("arquivos_encontrados", [])
    ctx.update(resultado)  # atualiza o contexto original
    return arquivos


def _executar_processamento(
    arquivos: list[Path],
    formatos: list[str],
    saida: Path,
) -> dict[Path, ErroBookmarks]:
    """Chama o caso de uso de processamento em lote."""
    return processar_arquivos_em_lote(
        arquivos=arquivos,
        formatos=formatos,
        diretorio_saida=saida,
    )


def _imprimir_resumo(arquivos: list[Path], falhas: dict[Path, ErroBookmarks]) -> None:
    """Exibe resumo do lote no console."""
    sucesso: int = len(arquivos) - len(falhas)
    print(f"Lote concluído: {sucesso}/{len(arquivos)} processados com sucesso.")
    for arq, erro in falhas.items():
        print(f"  [FALHA] {arq}: {erro}")


# -----------------------------------------------------------------------------
# Funções públicas (API)
# -----------------------------------------------------------------------------
def executar_busca_html(
    diretorio: Path | None = None,
) -> list[Path]:
    """Busca arquivos de bookmarks."""
    ctx: ParametrosBusca = criar_contexto(
        diretorio=diretorio,
    )
    try:
        return _buscar_arquivos(ctx)
    except ErroBookmarks as e:
        logger.error(msg=f"Erro na busca: {e}")
        raise


def executar_extracao(
    diretorio: Path | None = None,
) -> Any:
    """Busca, seleciona e extrai a árvore de bookmarks."""
    ctx: ParametrosBusca = criar_contexto(diretorio=diretorio)
    try:
        resultado: ParametrosBusca = executar_pipeline_basico(contexto=ctx)
        return resultado.get("raiz_bookmarks")
    except (ErroBookmarks, ValueError) as e:
        logger.error(msg=f"Erro na extração: {e}")
        raise


def executar_exportacao(
    diretorio: Path | None = None,
    *,
    formatos: list[str] | None = None,
    saida: Path | str | None = None,
) -> None:
    """Pipeline completo: busca -> seleção -> extração -> exportação."""
    ctx: ParametrosBusca = criar_contexto(
        diretorio=diretorio,
        formatos_exportacao=formatos,
        diretorio_saida=saida,
    )
    try:
        executar_pipeline_basico(contexto=ctx)
    except (ErroBookmarks, ValueError) as e:
        logger.error(msg=f"Erro na exportação: {e}")
        raise


def executar_lote(
    diretorio: Path | None = None,
    formatos: list[str] | None = None,
    saida: Path | str | None = None,
) -> dict[Path, ErroBookmarks]:
    """Processa todos os arquivos encontrados em lote."""
    ctx: ParametrosBusca = criar_contexto(
        diretorio=diretorio,
        formatos_exportacao=formatos,
        diretorio_saida=saida,
    )

    try:
        return _processar_lote(ctx)
    except ErroBookmarks as e:
        logger.error(msg=f"Erro no lote: {e}")
        raise


def _processar_lote(ctx) -> dict[Path, ErroBookmarks]:
    # 1. Buscar arquivos
    arquivos: list[Path] = _buscar_arquivos(ctx)
    if not arquivos:
        print("Nenhum arquivo encontrado.")
        return {}

    # 2. Parâmetros efetivos
    formatos_efetivos: list[str] = ctx.get("formatos_exportacao", DEFAULT_FORMATOS)
    saida_efetiva: Path = _normalizar_saida(caminho=ctx.get("diretorio_saida"))

    # 3. Processar
    falhas: dict[Path, ErroBookmarks] = _executar_processamento(
        arquivos, formatos=formatos_efetivos, saida=saida_efetiva
    )

    # 4. Resumo
    _imprimir_resumo(arquivos, falhas)

    return falhas


# -----------------------------------------------------------------------------
# Ponto de entrada (script)
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # --- Configuração comum ---
    DIRETORIO_BASE: Path = Path.home()
    EXTENSAO = ".html"
    CHAVES: list[str] = ["bookmarks", "favoritos"]
    FORMATOS: list[str] = [".json", ".csv", "md", "txt"]

    print("=" * 60)
    print("🧪 NEUTRON STAR - Teste de todas as funções")
    print("=" * 60)

    # 1. Buscar arquivos
    print("\n📂 1. Buscar arquivos HTML de bookmarks")
    try:
        arquivos: list[Path] = executar_busca_html(diretorio=DIRETORIO_BASE)
        print(f"   ✅ Encontrados {len(arquivos)} arquivo(s):")
        for idx, arq in enumerate(arquivos, 1):
            print(f"      {idx}. {arq}")
    except Exception as e:  # pylint: disable=W0718
        print(f"   ❌ Falha: {e}")

    if not arquivos:
        print("\n⚠️  Nenhum arquivo encontrado. Encerrando.")
        sys.exit(0)

    # 2. Extrair árvore do primeiro arquivo
    print("\n🌳 2. Extrair árvore de bookmarks do primeiro arquivo")
    try:
        if raiz := executar_extracao(diretorio=DIRETORIO_BASE):
            print(f"   ✅ Raiz extraída: {raiz.nome}")
            # Exibe estatísticas simples
            total: int = len(raiz.filhos_da_pasta) if hasattr(raiz, "filhos_da_pasta") else 0
            print(f"      Total de itens no primeiro nível: {total}")
        else:
            print("   ⚠️  Nenhuma raiz retornada.")
    except Exception as e:  # pylint: disable=W0718
        print(f"   ❌ Falha na extração: {e}")

    # 3. Exportar o primeiro arquivo (pipeline completo)
    print("\n📤 3. Exportar o primeiro arquivo (JSON + CSV)")
    try:
        executar_exportacao(
            diretorio=DIRETORIO_BASE,
            formatos=[".json", ".csv"],
            saida=DIRETORIO_BASE / "exportados",
        )
        print("   ✅ Exportação concluída.")
    except Exception as e:  # pylint: disable=W0718
        print(f"   ❌ Falha na exportação: {e}")

    # 4. Processar todos os arquivos em lote
    print("\n📦 4. Processar todos os arquivos em lote")
    try:
        if falhas := executar_lote(
            diretorio=DIRETORIO_BASE,
            formatos=FORMATOS,
            saida=DIRETORIO_BASE / "lote_output",
        ):
            print(f"   ⚠️  {len(falhas)} arquivo(s) falharam.")
        else:
            print("   ✅ Todos os arquivos processados com sucesso.")
    except Exception as e:  # pylint: disable=W0718
        print(f"   ❌ Falha no lote: {e}")

    # 5. (Opcional) Usar PipelineBuilder para pipeline condicional
    print("\n🔧 5. Demonstração do PipelineBuilder (buscar + extrair)")

    ctx: ParametrosBusca = criar_contexto(diretorio=DIRETORIO_BASE)

    try:
        # Usando builder
        resultado: ParametrosBusca = (
            PipelineBuilder(contexto_inicial=ctx)
            .adicionar("buscar")
            .adicionar("selecionar_arquivo", condicao=lambda c: len(c.get("arquivos_encontrados", [])) > 0)
            .adicionar("extrair")
            .depois(lambda c: print(f"      Extração concluída. Raiz: {c.get('raiz_bookmarks', {})}"))
            .executar()
        )
        print("   ✅ PipelineBuilder executado com sucesso.")
    except Exception as e:  # pylint: disable=W0718
        print(f"   ❌ Falha no PipelineBuilder: {e}")

    # 6. (Opcional) Uso de pipeline condicional com etapas customizadas
    print("\n🧩 6. Pipeline condicional (buscar → extrair se houver arquivo)")
    try:
        etapas: list[tuple[str, None] | tuple[str, Callable[..., bool]]] = [
            ("buscar", None),
            ("extrair", lambda c: len(c.get("arquivos_encontrados", [])) > 0),
        ]
        ctx_cond: ParametrosBusca = criar_contexto(diretorio=DIRETORIO_BASE)
        resultado_cond: ParametrosBusca = executar_pipeline_condicional(contexto=ctx_cond)
        print("   ✅ Pipeline condicional executado.")
        if resultado_cond.get("raiz_bookmarks"):
            print("      Raiz extraída com sucesso.")
        else:
            print("      Nenhuma raiz extraída (arquivo não encontrado?).")
    except Exception as e:  # pylint: disable=W0718
        print(f"   ❌ Falha no pipeline condicional: {e}")

    print("\n" + "=" * 60)
    print("✅ Testes concluídos.")
