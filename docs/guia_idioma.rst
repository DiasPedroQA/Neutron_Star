Guia De Idioma
==============

O código novo do projeto deve usar pt-BR como idioma canônico para nomes de
variáveis, funções, métodos, parâmetros, comentários e docstrings.

Regra principal
---------------

Use nomes em português nas APIs internas:

* ``favoritos`` em vez de ``bookmarks``.
* ``titulo`` em vez de ``title``.
* ``data_adicao`` em vez de ``add_date``.
* ``eh_html`` em vez de ``file_is_html``.
* ``pasta_usuario`` em vez de ``user_home``.
* ``processar_diretorio`` em vez de ``process_directory``.
* ``analisar_arquivo`` em vez de ``parse_file``.
* ``suporta_arquivo`` em vez de ``supports_file``.
* ``exportar`` em vez de ``export``.
* ``salvar`` e ``carregar`` em vez de ``save`` e ``load``.

Aliases De Compatibilidade
--------------------------

Alguns nomes antigos em inglês continuam existindo como aliases para reduzir
quebras durante a migração. Eles não devem ser usados em código novo nem em
novos testes. Quando uma classe implementa uma interface abstrata, implemente
sempre os métodos canônicos em pt-BR.

Exemplo correto em testes:

.. code-block:: python

   class DummyParser(FavoritoParser):
       def suporta_arquivo(self, arquivo: ModeloArquivo) -> bool:
           return True

       def analisar_arquivo(self, arquivo: ModeloArquivo) -> list[Bookmark]:
           return []

Exceções
--------

Use inglês apenas quando o nome vier de protocolo, formato externo ou biblioteca:

* Atributos HTML como ``href`` e ``add_date``.
* Extensões e formatos como ``json``, ``csv`` e ``pdf``.
* Termos esperados em nomes de arquivos exportados, como ``bookmark``.
* Nomes de pacotes, módulos de terceiros e APIs externas.
