# RFP Requirements Analyzer — contexto do projeto

Backend Python que analisa RFPs com IA (Groq via LiteLLM). Slug: `ia-com-rfp-analyzer-backend`.

## Stack
- Python 3.11+ · FastAPI · Pydantic v2 · LiteLLM (router obrigatório) · openpyxl · Typer
- Provider LLM: Groq (exceção registrada em `docs/00-excecoes.md`)
- Observabilidade: OpenTelemetry + OpenLIT (extra `obs`) → collector corporativo

## Como rodar
- `make install` · `make check` (ruff + mypy --strict + pytest) · `make run` (API :8080)
- Testes NÃO usam rede nem chave: LLM é substituído por `tests/fakes.py`

## Regras do repo
- Branch principal: `main` · deploy por tag (`vX.Y.Z-qa` QA, `vX.Y.Z` PRD)
- Prompts só em `src/rfp_analyzer/prompts/*.yaml`; mudou prompt → suba `version` e o golden test
- O LLM nunca reescreve texto de requisito, nunca declara aderência e nunca decide bid
- Fatos (extração, lacunas, riscos) = código determinístico em `pipeline/analyze.py`
- Nunca commitar `.env` nem colocar credenciais em prompts, logs ou testes

## Onde não mexer sem ADR
- `domain/models.py` (contrato público da API)
- `llm/gateway.py` (resiliência, custo e cache)

Detalhes: `docs/02-arquitetura.md` e `docs/adr/`.
