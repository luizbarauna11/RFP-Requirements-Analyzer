# ADR-005 — Degradação graciosa

**Status:** Aceito · **Data:** 2026-11

## Contexto
Provider fora do ar, chave expirada ou orçamento estourado não podem impedir o time de trabalhar perto
do prazo de uma proposta.

## Decisão
Toda etapa com LLM tem alternativa heurística. Falhas viram `degraded_mode=true` e entradas em
`usage.errors`, nunca erro 500. Itens inválidos do LLM caem individualmente para a heurística. O mesmo
caminho serve para o modo `--offline` (triagem a custo zero).

## Consequências
- (+) Disponibilidade do serviço independe da disponibilidade do LLM.
- (+) O usuário sabe exatamente o que veio da IA (`enrichment.source`, `cobertura_llm_pct`).
- (−) A qualidade em modo degradado é menor; isso fica explícito no relatório.
