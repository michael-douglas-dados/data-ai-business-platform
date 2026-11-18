# Arquitetura

A interface React consulta a API FastAPI. A API reutiliza os módulos de regras entre HTTP, CLI e testes.

SQLite possui clientes, pedidos, oportunidades, fila de campanha, execuções e auditoria. Chaves estrangeiras são habilitadas. Dinheiro usa centavos inteiros. Pedidos têm chave primária e versão, permitindo reexecução idempotente e correções. Oportunidades usam versão para impedir sobrescrita concorrente.

A ingestão rejeita linhas inválidas individualmente e grava as válidas com histórico em uma transação. A conciliação local verifica consistência entre total e agregação da mesma tabela. A integração PostgreSQL possui teste dbt entre raw e mart.

Campanhas preparam uma fila pendente de revisão, com consentimento e unicidade. Reexecuções removem elegibilidades obsoletas. A aplicação não dispara comunicações.

A busca lexical usa TF-IDF sobre documentos sintéticos. Recall@3 e MRR medem quatro perguntas. A investigação combina funções permitidas em fluxo determinístico. Nenhum modelo generativo externo é chamado.

## Segurança e operação

Execução local em loopback. Campos e origem do navegador são validados para mutações. Produção exige autenticação, autorização por usuário, TLS, limites de requisição, gestão de segredos e retenção. Controle de origem é defesa complementar.

runtime/, ambientes virtuais, builds e configurações locais são ignorados pelo Git. Dados são sintéticos. Exportações incluem métricas e identificadores da demonstração.
