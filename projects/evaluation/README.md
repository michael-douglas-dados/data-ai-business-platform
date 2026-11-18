# Avaliação de recuperação

Conjunto de referência com Recall@3, MRR e latência por pergunta.

Área de aplicação — Engenharia de IA.

## Executar

Na raiz do repositório, com as dependências instaladas, execute:

```bash
python -m app.cli evaluation
```

A base sintética é inicializada automaticamente. Os casos compartilham o banco local; para uma execução isolada, defina WORKBENCH_DB com um caminho temporário. A verificação de todos os casos usa uma base temporária própria.

## Implementação

- [Código principal](../../app/knowledge.py)
- [Contrato HTTP](../../app/api.py) — /api/evaluations
- [Testes de regressão](../../tests/test_workbench.py)
- [Arquitetura e limites](../../docs/architecture.md)

## Critério de entrega

Entrada validada, saída reproduzível e comportamento documentado em falhas. Os resultados representam dados sintéticos. O estado de validação das integrações está no [relatório de verificação](../../docs/verification.md).

Ferramentas relacionadas — Python, scikit-learn. dbt, Airflow e n8n são integrações complementares documentadas em integrations/.
