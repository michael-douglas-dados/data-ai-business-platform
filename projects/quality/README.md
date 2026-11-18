# Validação de dados

Validação de schema, chaves, duplicidades, valores e datas com motivos de rejeição.

Área de aplicação — Governança.

## Executar

Na raiz do repositório, com as dependências instaladas, execute:

```bash
python -m app.cli quality
```

A base sintética é inicializada automaticamente. Os casos compartilham o banco local; para uma execução isolada, defina WORKBENCH_DB com um caminho temporário. A verificação de todos os casos usa uma base temporária própria.

## Implementação

- [Código principal](../../app/pipeline.py)
- [Contrato HTTP](../../app/api.py) — /api/operations
- [Testes de regressão](../../tests/test_workbench.py)
- [Arquitetura e limites](../../docs/architecture.md)

## Critério de entrega

Entrada validada, saída reproduzível e comportamento documentado em falhas. Os resultados representam dados sintéticos. O estado de validação das integrações está no [relatório de verificação](../../docs/verification.md).

Ferramentas relacionadas — Python, Pydantic. dbt, Airflow e n8n são integrações complementares documentadas em integrations/.
