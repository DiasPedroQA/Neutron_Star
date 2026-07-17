Arquitetura
===========

O Neutron Star segue Clean Architecture, com quatro camadas em
``Atoms/src``:

Camadas
-------

* ``dominio/`` — entidades (``Bookmark``, ``BookmarkFolder``), filtros e
  exceções. Não depende de nenhuma outra camada.
* ``aplicacao/`` — casos de uso (``busca_arquivos``, ``parse_bookmarks``,
  ``exportar_bookmarks``), o pipeline de etapas (``etapas.py``) e as portas
  (interfaces) que a infraestrutura implementa.
* ``adaptadores/`` — implementações concretas das portas de exportação
  (JSON, CSV, TXT, PDF).
* ``infraestrutura/`` — acesso a sistema de arquivos e integrações externas.

Fluxo de execução
------------------

1. ``main.py`` lê a configuração do pipeline a partir de
   ``Atoms/pyproject.toml`` (seções ``[pipeline]`` e ``[parametros]``).
2. Cada etapa nomeada em ``[pipeline].etapas`` é resolvida em
   ``aplicacao/etapas.py`` e executada em sequência, passando um contexto
   (``dict``) de uma etapa para a próxima.
3. A etapa de busca usa ``dominio/filtros.py`` para selecionar arquivos.
4. A etapa de extração usa os casos de uso de ``aplicacao/casos_de_uso/`` para
   interpretar bookmarks HTML no formato Netscape.
5. A etapa de exportação delega para os adaptadores em ``adaptadores/exportadores/``.

Pontos de atenção
------------------

* Mantenha nomes de método em pt-BR, seguindo :doc:`guia_idioma`.
* ``dominio/`` nunca deve importar de ``adaptadores/`` ou ``infraestrutura/``
  — a dependência é sempre de fora para dentro.
* Toda classe e função pública deve ter docstring, para manter a geração
  automática do Sphinx (``sphinx.ext.autodoc``) útil e atualizada.
