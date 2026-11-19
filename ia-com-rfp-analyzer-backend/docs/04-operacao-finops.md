# 04 — Operação e FinOps

## Ambientes

| Ambiente | Publicação | LLM | Observabilidade |
|---|---|---|---|
| Dev local | `localhost:8080` | Groq (chave pessoal de dev) ou `--offline` | Logs JSON no terminal; Langfuse local opcional |
| QA | DNS interno definido pela INFRA | Groq (chave de QA) | Collector OTel corporativo |
| PRD | DNS interno definido pela INFRA | Groq + fallback | Collector OTel corporativo → Langfuse + Grafana |

Deploy por tag: `vX.Y.Z-qa` → QA, `vX.Y.Z` → PRD (pipeline em `.gitlab-ci.yml`).

## Observabilidade

- **Logs** JSON com `trace_id` em todas as linhas (`pipeline_step` com duração, `llm_call` com modelo, latência e tokens, `analysis_completed` com totais).
- **Traces LLM** via OpenLIT (instale o extra `obs` e defina `OTEL_EXPORTER_OTLP_ENDPOINT`). Instrumenta o LiteLLM automaticamente: modelo, tokens, custo e latência por chamada.
- **Health:** `GET /health` (liveness) e `GET /ready?deep=true` (faz um ping real ao LLM — chave configurada não prova que o provider responde).

### Alertas sugeridos

| Sinal | Condição | Ação |
|---|---|---|
| `degraded_mode=true` em análises | > 20% em 15 min | Ver runbook RB-01 |
| `fallback_used=true` | contínuo por > 1 h | Avaliar status da Groq; considerar trocar o primário |
| Tokens por análise | p95 > 80% do teto | Revisar tamanho de lote/prompts |
| Latência `/v1/analyses` | p95 > 30 s | Verificar provider e tamanho dos documentos |

## Runbooks

**RB-01 — LLM indisponível ou lento.** O serviço continua respondendo em modo heurístico (o campo
`usage.degraded_mode` indica). Verifique `/ready?deep=true`; consulte o status da Groq; se o problema
persistir, troque o primário por configuração (`LLM_PRIMARY_MODEL`) e reinicie o deployment. Erro
instantâneo costuma ser certificado/credencial; erro após o timeout costuma ser rede/firewall.

**RB-02 — Orçamento de tokens estourado.** Aparece `BudgetExceededError` em `usage.errors`. Verifique se
o documento é atipicamente grande; ajuste `LLM_BATCH_SIZE` ou `LLM_MAX_TOKENS_PER_ANALYSIS` de forma
consciente — o teto existe para proteger o custo.

**RB-03 — Qualidade caiu após mudança de prompt.** Reverta a versão do YAML em `prompts/`, rode o
conjunto de testes e compare as saídas com `examples/`. Toda mudança de prompt deve subir `version`.

**RB-04 — Alerta de prompt injection.** `security_flags` contém `possivel_prompt_injection`. Não há
impacto operacional (o LLM não tem poder de ação), mas avise o responsável pela RFP: pode indicar
documento adulterado.

## FinOps

Estimativa de consumo para uma RFP com ~40 requisitos (como o exemplo): 6 chamadas de enriquecimento +
1 de resumo ≈ 10–15 mil tokens de entrada e 10–15 mil de saída. Na tabela pública da Groq para Llama 3.3
70B (ordem de US$ 0,6 por milhão de tokens de entrada e US$ 0,8 por milhão de saída — **confirmar a
tabela vigente antes de orçar**), isso fica na casa de **US$ 0,02 por RFP**. RFPs sem códigos usam a
extração por LLM e podem custar de 2 a 4 vezes mais.

Alavancas de custo já implementadas: extração por regex (zero token), cache por hash do prompt, teto
de tokens por análise, modelo de fallback mais barato e modo offline para triagem.
