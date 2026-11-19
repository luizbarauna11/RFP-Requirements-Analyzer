# 03 — Segurança e compliance

## Modelo de ameaças (resumo)

| Ameaça | Vetor | Controle |
|---|---|---|
| Vazamento de dados pessoais ao LLM externo | Texto da RFP com contatos, CPFs, CNPJs | `security/pii.py` mascara CPF, CNPJ, e-mail, telefone e cartão **antes** de qualquer chamada; teste garante que nada vaza |
| Prompt injection via documento | RFP maliciosa com "ignore as instruções anteriores" | Documento tratado como dado (delimitado em `<documento>`), escape de delimitadores, detecção de padrões com flag em `security_flags`, e — principal — **o LLM não tem poder**: não reescreve requisitos, não decide e não executa ações |
| Alucinação de requisitos | LLM inventa cláusulas | Grounding obrigatório (ADR-003) e extração determinística quando há códigos |
| Manipulação da saída | LLM devolve códigos/estruturas inesperados | Códigos desconhecidos são descartados; schema validado item a item; texto original preservado |
| Abuso de custo | Uploads enormes, loop de chamadas | Limite de upload (10 MB), teto de tokens por análise, cache |
| Vazamento de credencial | `GROQ_API_KEY` em repo/log | `SecretStr`, `.env` no `.gitignore`, Secret K8s em QA/PRD, nunca logado |
| Upload malicioso | Arquivos executáveis | Allowlist de extensões (.txt, .md, .pdf, .docx), parsing sem execução |

## OWASP Top 10 para LLMs — cobertura

| Item | Status |
|---|---|
| LLM01 Prompt Injection | Mitigado (ver acima) |
| LLM02 Insecure Output Handling | Mitigado: saída validada por schema; nada é executado |
| LLM04 Model DoS | Mitigado: limites de upload, timeout, teto de tokens |
| LLM06 Sensitive Information Disclosure | Mitigado: mascaramento de PII; opção de LLM soberano |
| LLM08 Excessive Agency | Não aplicável por design: sistema sem ferramentas de escrita |
| LLM09 Overreliance | Mitigado: disclaimers, aderência e decisão sempre humanas |

## LGPD

- **Minimização:** só o texto necessário vai ao LLM, já mascarado; o resultado não guarda o documento original, apenas o hash SHA-256.
- **Transferência internacional:** a Groq processa dados fora do Brasil. Por isso o uso exige a exceção formal em [00-excecoes.md](00-excecoes.md) e, para RFPs classificadas como confidenciais, o modo soberano (LLM interno) ou o modo offline.
- **Retenção:** a API é stateless; o cache LLM é efêmero (`/tmp` no contêiner). Persistência de resultados (fase 2) seguirá a política de retenção da área.

## Autenticação e exposição

- Publicação **interna** (rede corporativa), atrás do Kong com SSO Microsoft e rate limiting.
- A aplicação não implementa login próprio (evita auth local, que é reprovada em revisão de SI).

## Checklist para revisão de SI

- [x] Nenhum secret no repositório (`.env.example` sem valores)
- [x] Mascaramento de PII antes do LLM externo
- [x] Validação de entrada (extensão, tamanho, schema)
- [x] Contêiner não-root, porta > 1024, imagem UBI
- [x] Scans de dependência (trivy) e licenças (bloqueio de GPL) no CI
- [x] IA sem permissão de escrita em sistemas
- [ ] Exceção da Groq aprovada pelo comitê de arquitetura
- [ ] App Registration/SSO configurado no Kong
