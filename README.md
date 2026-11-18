# Customer Data Workbench

Portfólio de Michael Douglas com 20 casos executáveis de CRM, engenharia de dados, BI e engenharia de IA em uma aplicação integrada.

React e TypeScript no frontend. FastAPI e Python na API. SQLite na demonstração local. Integrações complementares para PostgreSQL, dbt, Airflow e n8n.

## Começar

Requer Python 3.13 e Node.js 22 ou 24.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m app.seed
cd web
npm ci --registry=https://registry.npmjs.org
npm run build
cd ..
python -m uvicorn app.api:app --host 127.0.0.1 --port 8088
```

Abra http://127.0.0.1:8088/ para usar o CRM e http://127.0.0.1:8088/docs para explorar o contrato HTTP.

## Verificar

```bash
python -m unittest discover -s tests -v
python -m scripts.verify
python -m app.cli segmentation
```

A verificação dos 20 casos usa banco temporário. Os testes cobrem entradas inválidas, reexecução, correções por versão, rollback, concorrência otimista, consentimento, coortes, projeção temporal e avaliação de busca.

## Casos executáveis

[Catálogo de 20 casos](projects/README.md)

## Escopo e evidências

Os 20 casos compartilham módulos e dados sintéticos. A aplicação é uma demonstração local. A data de referência é fixa em 17/11/2026 para reprodução dos resultados.

A busca usa TF-IDF e avaliação de recuperação. A investigação usa um fluxo determinístico de ferramentas. Os resultados de Isolation Forest exigem revisão humana.

- [Arquitetura e decisões](docs/architecture.md)
- [Verificações realizadas e limites](docs/verification.md)
- [Pesquisa de mercado e fontes](docs/market-research.md)
- [Time pessoal e autoria](docs/team.md)
- [Integrações complementares](integrations/README.md)

Responsável pelo portfólio e direção dos casos — Michael Douglas. Código e documentação desenvolvidos com assistência de IA.
