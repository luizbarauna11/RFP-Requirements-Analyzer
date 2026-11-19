# ADR-002 — Extração híbrida de requisitos

**Status:** Aceito · **Data:** 2026-11

## Contexto
RFPs corporativas costumam numerar requisitos (RT-01, SLA-03). Usar LLM para extrair o que uma regex
extrai com 100% de fidelidade gera custo, latência e risco de paráfrase.

## Decisão
1. Regex primeiro: se houver ao menos `MIN_CODED_REQUIREMENTS` códigos, a extração é determinística.
2. Senão, LLM por blocos de texto, com grounding (ADR-003).
3. Sem LLM disponível, heurística por sentenças normativas ("deverá", "desejável", perguntas).

## Consequências
- (+) Para a maioria das RFPs, a extração custa zero tokens e é reprodutível.
- (+) O LLM é usado onde agrega: interpretação e análise.
- (−) RFPs com numeração exótica podem exigir ajuste da regex (coberto por testes).
