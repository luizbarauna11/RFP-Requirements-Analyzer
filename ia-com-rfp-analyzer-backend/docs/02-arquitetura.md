# 02 — Arquitetura

## Classificação

**Tier 2 IA (Assistido).** O sistema resume, classifica e analisa documentos, **não executa ações de
escrita** em sistemas de produção e não decide nada sozinho. Exigências do tier atendidas: logs
estruturados, gestão de custo de tokens e API versionada (`/v1`). Itens de Tier 1 (fallback de LLM,
observabilidade OTel completa) já estão implementados por serem baratos e úteis.

## C4 — Nível 1: Contexto

```mermaid
flowchart TB
    PV([Analista de pré-vendas]) -- "sobe RFP, lê relatório" --> SYS
    AR([Áreas responsáveis]) -- "preenchem aderência na matriz" --> XLS[(Matriz Excel)]
    SYS[RFP Requirements Analyzer] -- "gera" --> XLS
    SYS -- "chat completions (JSON)" --> GROQ[Groq Cloud<br/>Llama 3.x]
    SYS -- "traces OTLP" --> OBS[Collector OTel corporativo<br/>→ Langfuse / Grafana]
    N8N[n8n / Zeev BPM<br/>fluxo de bid] -- "POST /v1/analyses" --> SYS
```

## C4 — Nível 2: Contêineres

```mermaid
flowchart LR
    subgraph Borda
      KONG[Kong API Gateway<br/>SSO, rate limit]
    end
    subgraph "OpenShift — ns ia-com-rfp-analyzer-backend"
      API[API FastAPI<br/>uvicorn :8080]
      CACHE[(Cache LLM<br/>disco efêmero → Redis na fase 2)]
    end
    CLI[CLI rfp-analyzer<br/>uso local / batch]
    KONG --> API
    API --> CACHE
    API -- LiteLLM --> GROQ[Groq]
    API -. fallback .-> ALT[Outro provider<br/>ex.: IA Box soberana]
    CLI -- LiteLLM --> GROQ
```

## C4 — Nível 3: Componentes (pipeline)

```mermaid
flowchart TB
    L[ingestion.loaders] --> G[security.pii<br/>PII + injection]
    G --> X[pipeline.extract<br/>regex · LLM+grounding · heurística]
    X --> E[pipeline.enrich<br/>lotes · validação item a item]
    E --> A[pipeline.analyze<br/>lacunas · riscos · perguntas · KPIs]
    A --> S[pipeline.summarize<br/>resumo + sinal de bid]
    S --> R[reporting<br/>Markdown · Excel · JSON]
    E & X & S --> GW[[llm.gateway<br/>porta LLMGateway]]
    GW --> LIT[LiteLLMGateway<br/>retry · fallback · cache · budget · self-correction]
    P[(prompts/*.yaml<br/>versionados)] --> E & X & S
```

Cada etapa tem uma única responsabilidade (sem "God Agent") e conversa com o LLM apenas pela porta
`LLMGateway` — o que permite testar o pipeline inteiro com dublês, sem rede.

## Fluxo de uma análise

```mermaid
sequenceDiagram
    participant U as Usuário
    participant API
    participant P as Pipeline
    participant GW as LLM Gateway
    participant Q as Groq
    U->>API: POST /v1/analyses (arquivo)
    API->>P: analyze_text(texto)
    P->>P: guardrails (PII mascarada, injection sinalizado)
    P->>P: extração determinística (41 requisitos)
    loop lotes de 8 requisitos
        P->>GW: complete_json(enrich)
        GW->>GW: cache? orçamento?
        GW->>Q: chat.completions (json_object)
        alt erro transitório
            GW->>Q: retry com backoff
        else falha persistente
            GW->>Q: modelo de fallback
        end
        Q-->>GW: JSON
        GW-->>P: dict validado
    end
    P->>P: regras: lacunas, riscos cruzados, KPIs
    P->>GW: complete_json(executive_summary)
    P-->>API: AnalysisResult
    API-->>U: JSON (ou relatório Markdown)
```

## Decisões principais (ver ADRs)

| ADR | Decisão |
|---|---|
| [ADR-001](adr/ADR-001-groq-via-litellm.md) | Groq como provider primário, sempre via LiteLLM |
| [ADR-002](adr/ADR-002-extracao-hibrida.md) | Extração híbrida: regex primeiro, LLM só quando necessário |
| [ADR-003](adr/ADR-003-grounding-anti-alucinacao.md) | Grounding: todo trecho extraído por LLM precisa existir no documento |
| [ADR-004](adr/ADR-004-regras-deterministicas.md) | Lacunas e riscos como regras em código, não como prompt |
| [ADR-005](adr/ADR-005-degradacao-graciosa.md) | Degradação graciosa: o sistema nunca devolve vazio por falha do LLM |

## Requisitos não funcionais

| Requisito | Como é atendido |
|---|---|
| Latência | Groq (inferência rápida) + lotes de 8 requisitos; modo offline em milissegundos |
| Resiliência | Retry com backoff, fallback de modelo, timeout de 25 s, modo heurístico |
| Custo | Extração por regex (zero tokens), cache por hash do prompt, teto de tokens por análise |
| Confiabilidade da saída | `response_format=json_object`, validação Pydantic item a item, self-correction de JSON |
| Rastreabilidade | `trace_id`, SHA-256 do documento, versões de prompt e modelos usados em cada resultado |
| Testabilidade | Porta `LLMGateway` + dublês: 25 testes sem rede e sem chave |
| Portabilidade | 12-factor (env vars), contêiner UBI não-root, provider trocável por configuração |

## Pontos de extensão

- **Novo provider:** alterar `LLM_PRIMARY_MODEL`/`LLM_FALLBACK_MODEL` (qualquer modelo suportado pelo LiteLLM).
- **Nova regra de risco:** função em `pipeline/analyze.py` + entrada em `RISK_RULES` + teste.
- **Novo tópico de lacuna:** item em `COVERAGE_CHECKLIST`.
- **Novo formato de saída:** módulo em `reporting/` consumindo `AnalysisResult`.
