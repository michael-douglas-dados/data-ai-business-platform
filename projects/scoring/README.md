# Priorização comercial explicável

Pontuação por regras com justificativas e bloqueio por ausência de consentimento.

Área de aplicação — Vendas.

## Executar

Na raiz do repositório, com as dependências instaladas, execute:

```bash
python -m app.cli scoring
```

A base sintética é inicializada automaticamente. Os casos compartilham o banco local; para uma execução isolada, defina WORKBENCH_DB com um caminho temporário. A verificação de todos os casos usa uma base temporária própria.

## Implementação

- [Código principal](../../app/sectors.py)
- [Contrato HTTP](../../app/api.py) — /api/lead-scores
- [Testes de regressão](../../tests/test_workbench.py)
- [Arquitetura e limites](../../docs/architecture.md)

## Critério de entrega

Entrada validada, saída reproduzível e comportamento documentado em falhas. Os resultados representam dados sintéticos. O estado de validação das integrações está no [relatório de verificação](../../docs/verification.md).

Ferramentas relacionadas — Python, SQL. dbt, Airflow e n8n são integrações complementares documentadas em integrations/.
