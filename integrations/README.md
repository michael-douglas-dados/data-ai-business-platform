# Integrações complementares

## PostgreSQL e dbt

Instale dbt-core==1.11.0, dbt-postgres==1.11.0 e psycopg2-binary em ambiente próprio. Configure PGHOST, PGPORT, PGDATABASE, PGUSER e PGPASSWORD fora do versionamento. O destino padrão é portfolio em 127.0.0.1:55488.

Com PostgreSQL disponível e base local inicializada:

```bash
python -m integrations.postgres.load
dbt build --project-dir integrations/dbt --profiles-dir integrations/dbt
```

O carregador cria raw e faz upsert transacional. Os modelos criam métricas de clientes e receita mensal em analytics, com testes de unicidade, preenchimento e conciliação.

## Airflow

airflow/business_pipeline.py usa airflow.sdk do Airflow 3. O worker precisa do projeto e dependências no PYTHONPATH e WORKBENCH_DB apontando para armazenamento persistente. A DAG agenda ingestão, conciliação e avaliação.

## n8n

Importe n8n/prepare-audience.json e ajuste o endereço da API para sua rede local. O workflow prepara e consulta a fila de campanha. Configure autenticação antes de qualquer uso fora do ambiente local.

[Estado de validação](../docs/verification.md)
