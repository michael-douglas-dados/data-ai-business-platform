# Pesquisa de mercado para o portfólio

Pesquisa realizada em 17 de novembro de 2026. O recorte reúne anúncios públicos de empregadores no Brasil e um relatório recente do LinkedIn. A seleção foi intencional, orientada à experiência de Michael com BI, dados, automação e aplicações de negócio. Ela permite identificar requisitos concretos para os projetos e tem alcance limitado para estimar participação de mercado, remuneração ou volume de vagas.

## O que aparece nas fontes

| Área | Evidência observada | Implicação para os projetos | Fonte |
| --- | --- | --- | --- |
| Engenharia de dados e IA | Python, SQL, integração, APIs, RAG, agentes e documentação aparecem juntos. FastAPI, Airflow, dbt, LangGraph e bancos vetoriais são citados no anúncio. | Demonstrar o caminho entre ingestão, qualidade, recuperação de documentos e uma API testável. | [Gomes de Matos — Engenheiro de Dados em IA](https://gomesdematos.gupy.io/jobs/12732834) |
| Analytics engineering | Modelos de transformação, SQL avançado, testes, documentação, otimização e tradução de perguntas de negócio. O ambiente citado usa dbt, BigQuery, Airflow e Looker. | Explicar regras dos indicadores, granularidade, reconciliação e custo de processamento. | [Leega — Engenheiro Analítico Sênior](https://leega.gupy.io/jobs/12664767?jobBoardSource=gupy_public_page) |
| Engenharia de dados em nuvem | Pipelines, padronização, governança, Python, Git, Dataform/dbt e Apache Airflow. | Oferecer execução reproduzível e separar a lógica de dados da orquestração. | [Verity — Data Engineer Sênior](https://verity.gupy.io/jobs/12530984?jobBoardSource=gupy_public_page) |
| Automação financeira | Workflows em n8n, integração REST e webhooks, SQL, Python/JavaScript, tratamento de erros e indicadores de eficiência. | Tornar falhas, reprocessamentos e rastreabilidade visíveis nas automações. | [Grupo SBF — Analista de Automação Pleno](https://gruposbftalentos.gupy.io/jobs/12739489?jobBoardSource=gupy_public_page) |
| Automação com IA | Mapeamento de processos, n8n, Power Automate, ferramentas de agentes e integração com LLMs. Sustentação e mensuração do ganho fazem parte da função. | Associar cada recurso a um problema operacional e medir seu comportamento. | [Leega — Desenvolvedor de Automação/RPA](https://leega.gupy.io/jobs/12840598?jobBoardSource=gupy_public_page) |
| Aplicações web | React entre os frameworks aceitos, JavaScript/TypeScript, APIs, bancos como PostgreSQL e Git. Testes, containers e CI/CD aparecem como diferenciais. | Entregar um CRM navegável, com estados de erro, contratos de API e persistência. | [Claro — Desenvolvedor Full Stack Especialista](https://vempraclaro.gupy.io/jobs/12411969?jobBoardSource=gupy_public_page) |
| Engenharia de CRM | Segmentação por SQL, auditoria de bases, regras de validação, jornadas e funil comercial. A função exige experiência específica em Salesforce. | Mostrar regras de audiência, consentimento, funil e qualidade de dados. Experiência com a plataforma Salesforce exige validação própria. | [Suno — Analista de CRM Pleno](https://gruposunojobs.gupy.io/jobs/12650289?jobBoardSource=gupy_public_page) |
| CRM e varejo | Frequência, recência, valor de compra, fidelização, qualidade de cadastro e análise de conversão. | Conectar segmentação e coortes a decisões de relacionamento com clientes. | [Grupo Pereira — Analista de CRM Pleno](https://programadeestagiogp.pandape.infojobs.com.br/Detail/3938982) |

Os anúncios acima estavam acessíveis ou indexados no dia da pesquisa. A maioria das páginas consultadas não expunha uma data de publicação verificável. A página da Leega para engenharia analítica foi identificada pelo mecanismo de busca como banco de talentos, por isso seu conteúdo é tratado como referência de requisitos. A disponibilidade das oportunidades pode mudar.

## Sinal recente sobre IA

Em publicação de 27 de outubro de 2026, o LinkedIn informa que AI Engineer esteve entre as dez ocupações com maior crescimento em sete economias no trimestre de julho a setembro. A publicação também aponta aumento da presença de competências de IA nos anúncios. São sinais internacionais e não quantificam a demanda brasileira por cada biblioteca. [LinkedIn — dados sobre trabalho, competências e IA](https://news.linkedin.com/2026/linkedin-data-shows-where-opportunity-is-emerging-as-work-changes)

Minha interpretação para este portfólio é priorizar a combinação de fundamentos de dados, entendimento do negócio e engenharia de software verificável. As vagas consultadas conectam essas competências a integração, qualidade, APIs e sustentação. Um projeto ganha evidência quando outra pessoa consegue executar seus testes, observar falhas e compreender suas decisões.

## Como selecionar ferramentas

| Tecnologia | Uso justificável neste portfólio | Evidência que a implementação deve oferecer |
| --- | --- | --- |
| SQL e Python | Ingestão, tratamento, agregação, regras de negócio e automação. | Dados de entrada, contratos, resultados esperados e testes. |
| React e TypeScript | CRM, funil de oportunidades, pesquisa e painéis operacionais. | Build reproduzível, navegação funcional e estados de carregamento e erro. |
| FastAPI | Exposição das regras e operações por API. | Esquemas de entrada, respostas documentadas, validação e testes HTTP. |
| PostgreSQL | Evolução da persistência relacional quando o projeto executar nesse banco. | Migrações e testes realizados no mecanismo declarado. |
| dbt | Transformações analíticas, documentação e testes de modelos. | Modelos executáveis e evidência de execução do comando de construção. |
| Airflow | Agendamento e dependências de pipelines. | DAG carregável, tratamento de falhas e execução registrada. |
| n8n | Integrações operacionais e fluxos acionados por eventos. | Workflow importável, configuração documentada e teste do fluxo. |
| scikit-learn | Detecção de anomalias e recuperação lexical com baseline reproduzível. | Dados sintéticos, sementes fixas, métricas e limites do método. |
| Frameworks de agentes e RAG | Aplicações que precisam de seleção de ferramentas ou recuperação com geração. | Rastros, conjunto de avaliação e identificação do modelo efetivamente usado. |

No momento da pesquisa, o núcleo local observado usa FastAPI, SQLite e scikit-learn, com frontend React/TypeScript em implementação. As tecnologias adicionais só devem receber a identificação de implementadas e testadas quando essa evidência existir no repositório. A busca TF-IDF atual representa recuperação lexical e a investigação atual usa um fluxo determinístico de ferramentas.

## Recortes de negócio para os vinte projetos

A amplitude pode ser construída com casos que compartilham infraestrutura e preservam objetivos próprios.

- **CRM e relacionamento** — Cadastro, oportunidades, segmentação, pontuação explicável de clientes e preparação de campanhas.
- **Dados e operação** — Ingestão, qualidade, atualização por versão, reconciliação e monitoramento de execuções.
- **Análise de negócio** — Coortes, receita, compras e fornecedores, indicadores agregados de RH e projeções com baseline.
- **Engenharia de IA e conhecimento** — Preparação documental, recuperação com fontes, avaliação, detecção de anomalias e investigação por ferramentas.

Cada caso precisa mostrar qual decisão apoia, qual regra executa, como pode falhar e como foi verificado. Os indicadores de RH devem permanecer agregados para apoio operacional. Os dados de demonstração devem ser sintéticos ou públicos com procedência identificada.

## Referências técnicas para evolução

As fontes de vagas fundamentam a seleção de competências. As fontes técnicas abaixo orientam a implementação e os critérios de revisão.

- Contratos e testes HTTP. [FastAPI — Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- Modelos e testes de transformação. [dbt — Data tests](https://docs.getdbt.com/docs/build/data-tests)
- Interface pública de orquestração. [Apache Airflow — Public interface](https://airflow.apache.org/docs/apache-airflow/stable/public-airflow-interface.html)
- Avaliação de aplicações e agentes. [MLflow — Evaluation](https://mlflow.org/genai/evaluations)
- Automação e integrações. [n8n — Documentação](https://docs.n8n.io/)
- Interfaces e componentes. [React — Documentação](https://react.dev/learn)

Pesquisa e síntese realizadas com assistência de IA. As fontes sustentam os requisitos observados. A autoria dos projetos de referência pertence aos respectivos mantenedores.
