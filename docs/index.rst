Neutron Star — Documentação
============================

Ferramenta CLI de busca em sistema de arquivos com filtros avançados,
exportação de resultados e análise de metadados.

.. toctree::
   :maxdepth: 2
   :caption: Conteúdo

   api/models
   api/controllers
   api/views
   api/utils

Início rápido
-------------

Instale o projeto::

   pip install -e .[dev]

Execute a busca padrão::

   neutron

Ou use diretamente via Python::

   from models.configuracoes import ConfigBusca
   from controllers.buscador import buscar
   from views.apresentador import Apresentador

   config = ConfigBusca(padrao="*.py", recursivo=True)
   resultado = buscar(config)
   Apresentador().exibir(resultado)

Índices
-------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
