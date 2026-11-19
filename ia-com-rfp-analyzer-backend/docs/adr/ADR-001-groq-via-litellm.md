# ADR-001 — Groq como provider primário, sempre via LiteLLM

**Status:** Aceito (sujeito à EXC-001) · **Data:** 2026-11

## Contexto
O projeto deve usar a Groq. A stack corporativa exige um LLM Router para troca dinâmica de provider e
proíbe acoplamento a um único fornecedor.

## Decisão
Acessar a Groq pelo LiteLLM (`groq/llama-3.3-70b-versatile` primário, `groq/llama-3.1-8b-instant`
fallback), atrás de uma porta `LLMGateway` no código. O adapter concentra retry, fallback, cache,
teto de custo e correção de JSON.

## Consequências
- (+) Trocar de modelo/provider é configuração; testes usam dublês sem rede.
- (+) OpenLIT instrumenta o LiteLLM automaticamente.
- (−) Uma dependência a mais (LiteLLM) e o ritmo de atualização dela.
