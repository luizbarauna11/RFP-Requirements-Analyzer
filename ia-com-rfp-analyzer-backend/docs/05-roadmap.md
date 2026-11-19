# 05 — Roadmap

| Fase | Entregas | Valor |
|---|---|---|
| **1.0 (atual)** | Pipeline híbrido, Groq via LiteLLM, API, CLI, relatórios MD/Excel, guardrails, 25 testes | Análise de RFP em segundos com rastreabilidade |
| **1.1 — Qualidade mensurável** | Golden dataset com 10+ RFPs reais anotadas; avaliação automática (precisão de categoria/criticidade ≥ 85%) no CI; feedback de concordância na matriz | Confiança baseada em números, não em impressão |
| **1.2 — Persistência e colaboração** | PostgreSQL para histórico de análises; Redis para cache semântico; UI web simples (React) para upload e revisão | Histórico, comparação entre RFPs, uso por não técnicos |
| **2.0 — Integração ao processo de bid** | Webhook n8n → Zeev (tarefa de go/no-go com o resumo anexado); notificação no Teams | IA dentro do fluxo existente |
| **2.1 — Memória de propostas (RAG)** | Base vetorial (pgvector/Qdrant) com propostas e respostas anteriores; sugestão de texto de resposta por requisito, com citação da fonte | Reuso de conhecimento e padronização das respostas |
| **2.2 — Inteligência comercial** | Estimativa de esforço/headcount a partir de volumetria e SLAs; comparação com contratos semelhantes | Precificação mais rápida e consistente |
| **Contínuo** | Modo soberano (LLM interno) como padrão para RFPs confidenciais; revisão trimestral das regras de risco | Compliance e atualização do conhecimento de negócio |
