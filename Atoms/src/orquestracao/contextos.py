# Normaliza formato com ponto e separa defaults de disponíveis
EXPORTADORES = {
    ".json": "exportador_json",
    ".csv": "exportador_csv",
    ".pdf": "exportador_pdf",
    ".txt": "exportador_txt",
    ".md": "exportador_md",
}

# Formatos disponíveis (chaves com ponto). Não incluí .pdf no DEFAULT por depender de fpdf2 opcional.
DEFAULT_FORMATOS = [".json", ".csv", ".txt", ".md"]


def normaliza_ext(ext: str) -> str:
    if not ext:
        return ""
    return ext if ext.startswith(".") else f".{ext}"


def formatos_para_exportar(extensoes=None):
    if extensoes is None:
        return list(DEFAULT_FORMATOS)
    return [normaliza_ext(e) for e in extensoes]
