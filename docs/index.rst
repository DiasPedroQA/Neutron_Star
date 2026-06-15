Neutron Star
============

Documentação do projeto Neutron Star, com foco em arquitetura limpa,
linguagem em pt-BR e geração de APIs internas a partir de docstrings.

.. toctree::
   :maxdepth: 2
   :caption: Guias

   uso
   arquitetura
   guia_idioma

API
---

Entidades
~~~~~~~~~

.. automodule:: Atoms.backend.core.entidades.entidade_bookmark
   :members:

.. automodule:: Atoms.backend.core.entidades.entidade_arquivo
   :members:

.. automodule:: Atoms.backend.core.entidades.entidade_diretorio
   :members:

.. automodule:: Atoms.backend.core.entidades.entidade_sistema_operacional
   :members:

.. automodule:: Atoms.backend.core.entidades.entidade_processamento
   :members:

Serviços
~~~~~~~~

.. automodule:: Atoms.backend.core.services
   :members:

Infraestrutura
~~~~~~~~~~~~~~

.. automodule:: Atoms.backend.infrastructure.parser
   :members:

.. automodule:: Atoms.backend.infrastructure.file_scanners
   :members:

.. automodule:: Atoms.backend.infrastructure.so_identifier
   :members:

.. automodule:: Atoms.backend.infrastructure.exporters.json_exporter
   :members:

.. automodule:: Atoms.backend.infrastructure.exporters.csv_exporter
   :members:

.. automodule:: Atoms.backend.infrastructure.exporters.pdf_exporter
   :members:
