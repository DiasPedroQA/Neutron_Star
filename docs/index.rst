Neutron Star — Documentação
============================

Ferramenta CLI de busca em sistema de arquivos com filtros avançados,
extração de bookmarks (HTML) e exportação de resultados em JSON, CSV, TXT e PDF.

.. toctree::
   :maxdepth: 2
   :caption: Conteúdo

   uso
   arquitetura
   guia_idioma
   api/dominio
   api/aplicacao
   api/adaptadores
   api/infraestrutura

Início rápido
-------------

Instale o projeto em modo desenvolvimento::

   pip install -e "Atoms[dev]"

Execute o pipeline configurado em ``Atoms/pyproject.toml`` (seções ``[pipeline]`` e ``[parametros]``)::

   neutron

Ou use diretamente via Python::

   from aplicacao.etapas import etapa_busca, etapa_extrair, etapa_exportar

   ctx = etapa_busca({"dirs": ["./dados"], "extensao": ".html"})
   ctx = etapa_extrair(ctx)
   etapa_exportar(ctx)

Índices
-------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
