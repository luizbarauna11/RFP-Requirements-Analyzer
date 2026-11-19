# ADR-003 — Grounding obrigatório na extração por LLM

**Status:** Aceito · **Data:** 2026-11

## Contexto
Um requisito inventado pelo modelo é o pior erro possível: o time pode precificar algo que o cliente
não pediu.

## Decisão
O prompt exige `source_text` literal. Cada item é aceito apenas se o trecho existir no documento
(comparação normalizada sem acentos e espaços, ou maior trecho comum ≥ `GROUNDING_MIN_RATIO`, padrão
85%). Itens reprovados são descartados e contabilizados em log.

## Consequências
- (+) Elimina requisitos fabricados; o texto exibido é sempre o do documento.
- (−) Paráfrases legítimas são descartadas (preferimos perder um item a inventar um).
