"""Testes das entidades de domínio TagA e VirtualFolder."""

from typing import Any

from dominio.entidades import TagA, VirtualFolder


class TestTagA:
    """Comportamento do favorito individual."""

    def test_to_dict_contem_todos_os_campos(self) -> None:
        """to_dict deve serializar url, titulo e metadados sem perder informação."""
        bookmark = TagA(
            url="https://exemplo.com",
            titulo="Exemplo",
            data_adicao="123",
            ultima_modificacao="456",
            icon_uri="data:image/png;base64,abc",
        )

        resultado: dict[str, str] = bookmark.to_dict()

        assert resultado == {
            "url": "https://exemplo.com",
            "titulo": "Exemplo",
            "data_adicao": "123",
            "ultima_modificacao": "456",
            "icon_uri": "data:image/png;base64,abc",
        }

    def test_to_dict_usa_valores_padrao_quando_metadados_ausentes(self) -> None:
        """Campos opcionais devem virar string vazia quando não informados."""
        bookmark = TagA(url="https://exemplo.com", titulo="Exemplo")

        resultado: dict[str, str] = bookmark.to_dict()

        assert resultado["data_adicao"] == ""
        assert resultado["ultima_modificacao"] == ""
        assert resultado["icon_uri"] == ""


class TestVirtualFolder:
    """Comportamento da pasta que agrupa favoritos e subpastas."""

    def test_to_dict_serializa_pasta_vazia(self) -> None:
        """Pasta sem filhos deve gerar lista vazia em filhos_da_pasta."""
        pasta = VirtualFolder(nome="Raiz")

        assert pasta.to_dict() == {
            "nome": "Raiz",
            "data_adicao": "",
            "ultima_modificacao": "",
            "filhos_da_pasta": [],
        }

    def test_to_dict_serializa_favoritos_e_subpastas_recursivamente(self) -> None:
        """to_dict deve descer recursivamente em subpastas aninhadas."""
        pasta = VirtualFolder(
            nome="Raiz",
            filhos_da_pasta=[
                TagA(url="https://a.com", titulo="A"),
                VirtualFolder(
                    nome="Sub",
                    filhos_da_pasta=[TagA(url="https://b.com", titulo="B")],
                ),
            ],
        )

        resultado: dict[str, Any] = pasta.to_dict()

        assert resultado["filhos_da_pasta"][0]["titulo"] == "A"
        assert resultado["filhos_da_pasta"][1]["nome"] == "Sub"
        assert resultado["filhos_da_pasta"][1]["filhos_da_pasta"][0]["titulo"] == "B"
