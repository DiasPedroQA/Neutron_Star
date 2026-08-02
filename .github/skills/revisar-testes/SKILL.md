---
name: revisar-testes
description: "Use when: revisar, ajustar ou alinhar testes de pytest com o código atual do projeto, incluindo estrutura, cobertura, nomes e expectativas."
---

# Revisar testes e alinhá-los ao projeto

## Quando usar
Use esta skill quando precisar revisar testes existentes, corrigir expectativas desatualizadas ou escrever testes que reflitam a arquitetura real do projeto.

## Objetivo
Produzir testes que:
- validem o comportamento real do código em [src](src)
- sigam as convenções definidas em [pyproject.toml](pyproject.toml)
- sejam enxutos, determinísticos e fáceis de manter
- cubram tanto o caminho feliz quanto casos de borda e falhas

## Fluxo de trabalho

1. Mapear o ponto em teste
   - Identifique o módulo, função, classe ou fluxo que será testado.
   - Leia a implementação em [src](src) e entenda o contrato público.
   - Considere o contexto de domínio, aplicação, infraestrutura ou CLI.

2. Inspecionar os testes atuais
   - Compare os testes com o comportamento atual do código.
   - Remova assertions antigas, obsoletas ou baseadas em detalhes internos.
   - Verifique se o nome do teste e a estrutura ainda fazem sentido.

3. Escolher a estratégia certa
   - Se for lógica de domínio, prefira testes unitários diretos.
   - Se envolver sistema de arquivos, use tmp_path ou pyfakefs em vez de mockar demais.
   - Se for ponto de entrada CLI, teste a função pública ou o fluxo observável.
   - Se for comportamento assíncrono, use pytest-asyncio e marque adequadamente.

4. Reescrever ou adicionar testes
   - Mantenha cada teste focado em uma única responsabilidade.
   - Assert o resultado esperado, não detalhes de implementação.
   - Cubra cenários positivos, negativos e exceções.
   - Prefira fixtures simples quando houver repetição.

5. Alinhar com as convenções do projeto
   - Coloque os testes em [tests](tests) seguindo a mesma estrutura de pacotes do código.
   - Use nomes de arquivo como test_*.py e funções test_*.
   - Aplique marcadores unit, integration e slow quando fizer sentido.
   - Respeite as regras do projeto em [pyproject.toml](pyproject.toml), incluindo estilo e cobertura.

6. Validar a mudança
   - Execute os testes relevantes com pytest.
   - Se necessário, rode também ruff para checar estilo.
   - Ajuste até que os testes estejam verdes e coerentes.

## Pontos de decisão
- Se o comportamento é uma regra pura de negócio, teste diretamente a entidade ou função.
- Se o teste depende de arquivos ou caminhos, prefira tmp_path ou pyfakefs.
- Se um teste está frágil porque depende de implementação interna, reescreva-o para validar o resultado público.
- Se o projeto usa camadas bem separadas, mantenha o teste no nível correto: domínio, aplicação, infraestrutura ou interface.

## Checklist de conclusão
- Os testes refletem o código atual.
- Asserções antigas foram removidas ou corrigidas.
- Há cobertura de sucesso e falha.
- O nome, a organização e os marcadores estão coerentes com o projeto.
- A execução relevante de pytest passou.

## Exemplos de prompts
- "Revise os testes deste módulo e alinhe com o comportamento atual do código."
- "Ajuste os testes para refletirem a arquitetura do projeto e remover expectativas obsoletas."
- "Adicione testes de borda para este fluxo sem depender de detalhes internos."
- "Reescreva estes testes para que validem o comportamento público e não a implementação."
