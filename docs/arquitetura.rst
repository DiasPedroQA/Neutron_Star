Arquitetura
===========

O Neutron Star foi organizado com separação de responsabilidade entre domínio,
integração e apresentação.

Camadas principais
------------------

* `Atoms/backend/core` - regras de negócio e modelos de domínio.
* `Atoms/backend/infrastructure` - implementação de parsing, scanners e exportadores.
* `Atoms/frontend` - interface de linha de comando e apresentação.

Dependências internas
---------------------

A documentação Sphinx inclui automaticamente as APIs internas mais relevantes
para desenvolvedores por meio de módulos e docstrings.

O fluxo de implementação esperado é:

1. `ModeloArquivo` entra no parser.
2. `TagsFinder` extrai `Favorito`.
3. Serviços usam os favoritos para exportação ou processamento.
4. A CLI invoca serviços e exportadores.

Pontos de atenção
-----------------

* Mantenha todos os nomes de método em pt-BR, seguindo o `guia_idioma`.
* Não exponha configurações ou objetos de infraestrutura diretamente na API
  do domínio.
* Use docstrings em cada classe e método para manter a geração automática do
  Sphinx útil e atualizada.
