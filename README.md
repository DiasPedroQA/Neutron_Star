# Neutron Star

Projeto Python para localizar arquivos HTML de bookmarks e extrair seus links
por meio de uma API FastAPI.

O código da aplicação está em [`Atoms/`](Atoms/README.md). Consulte esse
README para instalação, execução local, rotas HTTP e testes.

## Desenvolvimento rápido

```bash
make install
make check
make run
```

Por segurança, execute a API apenas em ambientes confiáveis: ela recebe
caminhos de arquivos disponíveis no servidor.
