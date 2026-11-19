# ADR-004 — Lacunas e riscos cruzados como regras em código

**Status:** Aceito · **Data:** 2026-11

## Contexto
Lacunas ("a RFP não fala de penalidades") e riscos cruzados ("SLA de 15 min + presença em 3 cidades")
são o maior valor do produto e influenciam decisões financeiras. Precisam ser reprodutíveis,
explicáveis e revisáveis por pré-vendas.

## Decisão
Implementar como funções puras em `pipeline/analyze.py` (checklist de 12 tópicos e 7 regras de risco),
com testes. O LLM complementa com riscos e ambiguidades por requisito, mas não decide lacunas nem riscos
cruzados.

## Consequências
- (+) Mesmo documento → mesmo resultado; cada risco aponta os requisitos que o originaram.
- (+) O conhecimento de negócio fica versionado e revisável em code review.
- (−) Regras exigem manutenção; revisão trimestral com pré-vendas prevista no roadmap.
