# Busca de conhecimento

Recuperação lexical TF-IDF com pontuação e limiar para ausência de resultado.

Área de aplicação — Engenharia de IA.

## Executar

Na raiz do repositório, com as dependências instaladas, execute:

```bash
python -m app.cli retrieval
```

A base sintética é inicializada automaticamente. Os casos compartilham o banco local; para uma execução isolada, defina WORKBENCH_DB com um caminho temporário. A verificação de todos os casos usa uma base temporária própria.

## Implementação

- [Código principal](../../app/knowledge.py)
- [Contrato HTTP](../../app/api.py) — /api/search
- [Testes de regressão](../../tests/test_workbench.py)
- [Arquitetura e limites](../../docs/architecture.md)

## Critério de entrega

Entrada validada, saída reproduzível e comportamento documentado em falhas. Os resultados representam dados sintéticos. O estado de validação das integrações está no [relatório de verificação](../../docs/verification.md).

Ferramentas relacionadas — scikit-learn, FastAPI. dbt, Airflow e n8n são integrações complementares documentadas em integrations/.
