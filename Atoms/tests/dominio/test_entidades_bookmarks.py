"""Testes das entidades imutáveis do domínio."""

from dominio.entidades import ArquivoTemp, ConversaoResultado, TagExtraida


def test_conversao_resultado_agrega_arquivo_e_tags() -> None:
    """O resultado preserva o arquivo de origem e as tags extraídas."""
    arquivo = ArquivoTemp(nome="bookmarks.html", caminho_absoluto="/tmp/bookmarks.html", tamanho=10)
    tag = TagExtraida(titulo="Exemplo", url="https://example.com")

    resultado = ConversaoResultado(arquivo=arquivo, tags_extraidas=[tag])

    assert resultado.arquivo == arquivo
    assert resultado.tags_extraidas == [tag]
