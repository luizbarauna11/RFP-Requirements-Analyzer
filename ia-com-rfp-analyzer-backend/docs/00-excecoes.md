# 00 — Exceções à stack corporativa

## EXC-001 — Groq como provider de LLM

| Campo | Valor |
|---|---|
| Item fora da stack | Groq Cloud (inferência de modelos Llama) como provider primário |
| Status | **Pendente de aprovação** pelo comitê de arquitetura |
| Solicitante | Time do RFP Requirements Analyzer |

**Justificativa técnica.** O requisito do projeto é usar a Groq: latência de inferência muito baixa
(boa experiência para documentos com dezenas de requisitos), modelos abertos (Llama) e custo por token
baixo. A integração respeita a regra da stack de usar um **LLM Router (LiteLLM)**: nenhum código depende
do SDK da Groq, e trocar de provider é uma mudança de configuração.

**Riscos e mitigações.**

| Risco | Mitigação |
|---|---|
| Dados de clientes processados fora do Brasil | Mascaramento de PII antes do envio; RFPs confidenciais usam o modo soberano (LLM interno) ou offline |
| Indisponibilidade do provider | Fallback de modelo/provider por configuração e modo heurístico |
| Dependência de fornecedor | LiteLLM como camada de abstração; prompts agnósticos de modelo |

**Plano de saída.** Se a exceção não for aprovada (ou for revogada), aponte `LLM_PRIMARY_MODEL` para o
provider aprovado (ex.: IA Box interna via endpoint compatível com OpenAI) e reexecute os testes. Nenhuma
mudança de código é necessária.

**Gatilho de revisão.** Revisar a exceção a cada 12 meses ou se o volume passar de 500 análises/mês.
