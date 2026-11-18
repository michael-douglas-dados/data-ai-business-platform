# Catálogo de projetos

| Caso | Área | Descrição |
| --- | --- | --- |
| [CRM e funil comercial](crm/README.md) | Comercial | Clientes, oportunidades e mudança de etapa com controle de concorrência. |
| [ETL de pedidos](etl/README.md) | Operações | Ingestão CSV, transformação monetária e histórico de carga. |
| [Validação de dados](quality/README.md) | Governança | Validação de schema, chaves, duplicidades, valores e datas com motivos de rejeição. |
| [Carga incremental versionada](incremental/README.md) | Engenharia de dados | Reprocessamento idempotente e atualização somente por versões mais recentes. |
| [Modelo analítico de receita](warehouse/README.md) | Analytics Engineering | Agregação mensal de receita e volume para consumo por indicadores. |
| [Conciliação de indicadores](reconciliation/README.md) | Financeiro | Conferência entre total da base e agregação por cliente em centavos. |
| [Segmentação por comportamento](segmentation/README.md) | CRM e Growth | Audiências por frequência e recência com consentimento explícito. |
| [Retenção por coortes](retention/README.md) | Produtos e assinaturas | Coortes por mês da primeira compra com meses de atividade zero preservados. |
| [Preparação de campanhas](campaigns/README.md) | Marketing | Fila idempotente de clientes elegíveis com etapa de revisão humana. |
| [Detecção de valores atípicos](anomalies/README.md) | Auditoria | Isolation Forest aponta pedidos para revisão com semente reproduzível. |
| [Ingestão de conhecimento](documents/README.md) | Operações e suporte | Documentos divididos em trechos com identificador e fonte rastreável. |
| [Busca de conhecimento](retrieval/README.md) | Engenharia de IA | Recuperação lexical TF-IDF com pontuação e limiar para ausência de resultado. |
| [Avaliação de recuperação](evaluation/README.md) | Engenharia de IA | Conjunto de referência com Recall@3, MRR e latência por pergunta. |
| [Investigação com ferramentas](investigation/README.md) | Operações de dados | Workflow determinístico combina conciliação, indicadores e busca com trilha de execução. |
| [Observabilidade de cargas](observability/README.md) | DataOps | Histórico de duração, linhas aceitas/rejeitadas e trilha de alterações. |
| [Análise de fornecedores](procurement/README.md) | Compras | Concentração de gastos e taxa de entregas no prazo por fornecedor sintético. |
| [Indicadores agregados de RH](workforce/README.md) | People Analytics | Custos e ausência ponderada por horas previstas em dados sintéticos. |
| [Projeção de receita](forecast/README.md) | Planejamento financeiro | Baseline de média móvel com backtest temporal e erro absoluto médio. |
| [Priorização comercial explicável](scoring/README.md) | Vendas | Pontuação por regras com justificativas e bloqueio por ausência de consentimento. |
| [Contrato de dados para BI](exports/README.md) | BI e integrações | Exportação de métricas de clientes em CSV com colunas fixas e valores em centavos. |
