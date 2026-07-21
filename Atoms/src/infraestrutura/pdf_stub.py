"""Stub de infraestrutura para a dependência opcional de geração de PDFs.

Fornece uma implementação mínima compatível com a interface esperada da
biblioteca fpdf2, emitindo um erro claro quando a funcionalidade de PDF é usada sem a dependência instalada.
"""


class FPDF:
    """Stub mínimo usado quando a biblioteca fpdf2 não está instalada.

    Sinaliza claramente a ausência da dependência opcional necessária
    para geração de arquivos PDF, em vez de falhar com ImportError
    genérico em um ponto distante do uso real.
    """

    def __init__(self, *_args: object, **_kwargs: object) -> None:
        raise RuntimeError("fpdf library is required for PDF export. Install with 'pip install fpdf2'")

    def add_page(self, *_args: object, **_kwargs: object) -> None:
        """Stub method."""

    def set_font(self, *_args: object, **_kwargs: object) -> None:
        """Stub method."""

    def set_text_color(self, *_args: object, **_kwargs: object) -> None:
        """Stub method."""

    def cell(self, *_args: object, **_kwargs: object) -> None:
        """Stub method."""

    def multi_cell(self, *_args: object, **_kwargs: object) -> None:
        """Stub method."""

    def ln(self, *_args: object, **_kwargs: object) -> None:
        """Stub method."""

    def output(self, *_args: object, **_kwargs: object) -> None:
        """Stub method."""
