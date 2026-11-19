# 01 — Visão estratégica

## Problema

Responder RFPs de serviços de TI é uma corrida contra o prazo em que o maior risco não é escrever a
proposta — é **precificar errado**. As causas recorrentes são três:

1. **Omissões da RFP** — penalidades, volumetria, janela de cobertura, reajuste. Quem não pergunta, assume; quem assume, absorve o prejuízo.
2. **Combinações perigosas** — cada cláusula parece razoável isolada; juntas (ex.: SLA de 15 min + presença física em 3 cidades + preço fixo sem volumetria) tornam a operação deficitária.
3. **Trabalho braçal** — horas de tabulação manual que poderiam ser gastas em estratégia de solução e preço.

## Proposta de valor

O RFP Requirements Analyzer entrega, em segundos, o "primeiro rascunho do pensamento crítico" do time de
pré-vendas, e deixa a decisão com as pessoas:

| Entrega | Valor para o negócio |
|---|---|
| Matriz de requisitos classificada (categoria, obrigatoriedade, criticidade, risco, custo, área) | Distribui o trabalho entre áreas no dia 1 |
| Riscos cruzados entre cláusulas, com mitigação sugerida | Evita contratos deficitários |
| Lacunas de informação (checklist de 12 tópicos) | Transforma "o que faltou" em perguntas formais ao cliente |
| Perguntas de esclarecimento consolidadas e priorizadas | Aproveita a janela de Q&A da concorrência |
| Sinal indicativo de bid + Índice de Clareza | Acelera a reunião de go/no-go com dados |

## Princípios de produto

- **Humano no comando.** A IA nunca declara aderência nem decide bid; ela prepara a decisão.
- **Fatos auditáveis.** Extração, lacunas e riscos são regras explícitas, versionadas e testadas.
- **Funciona sem IA.** O modo determinístico entrega ~80% do valor com custo zero e serve de contingência.
- **Custo previsível.** Circuit breaker de tokens por documento e cache de respostas.

## KPIs de sucesso (propostos)

| KPI | Linha de base (a medir) | Meta 6 meses |
|---|---|---|
| Tempo da RFP recebida até a matriz de requisitos pronta | 1–3 dias | < 1 hora |
| % das RFPs com perguntas enviadas na janela de Q&A | a medir | > 90% |
| Lacunas críticas descobertas após o envio da proposta | a medir | redução de 50% |
| Concordância do time com a classificação da IA (amostragem) | — | > 85% |
| Custo de IA por RFP analisada | — | < US$ 0,10 |

## Usuários e jornada

1. **Analista de pré-vendas** sobe a RFP (UI, API ou CLI) e recebe relatório + matriz.
2. **Áreas responsáveis** (Operações, RH, SI, Financeiro, Jurídico) preenchem as colunas de aderência da matriz.
3. **Gerente da conta** envia as perguntas priorizadas ao cliente.
4. **Comitê de bid** decide com base no resumo executivo, riscos e KPIs.

## Estratégia de adoção

| Fase | Escopo | Critério de saída |
|---|---|---|
| Piloto (4 semanas) | 1 time de pré-vendas, RFPs reais em paralelo ao processo atual | Concordância > 80% e feedback qualitativo positivo |
| Expansão | Todos os times de serviços; integração com o fluxo de bid no Zeev | Uso em > 70% das RFPs recebidas |
| Escala | Base histórica de propostas (RAG) para sugerir respostas e preços | Ver [roadmap](05-roadmap.md) |

## Riscos do próprio produto

| Risco | Mitigação |
|---|---|
| Confiança excessiva na IA | Disclaimers, colunas de aderência humanas, sinal "indicativo" |
| Vazamento de dados de cliente para LLM externo | Mascaramento de PII, exceção formal, opção de LLM soberano (ver [00-excecoes](00-excecoes.md)) |
| Regras de negócio desatualizadas | Regras em código com testes; revisão trimestral com pré-vendas |
| Dependência de um provider | LiteLLM: trocar de provider é configuração, não código |
