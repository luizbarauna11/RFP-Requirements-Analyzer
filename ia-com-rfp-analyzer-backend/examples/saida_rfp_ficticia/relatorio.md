# Análise de RFP — RFP FICTÍCIA – SERVIÇOS DE FIELD SERVICES E SUPORTE DE TI

> Documento: `rfp_ficticia_field_services.txt` · Análise `edc53a9be4ed` · 19/11/2026 22:27 UTC · trace `0811d156c9454a1582d788bda2f8295b`

## 1. Resumo executivo

**Sinal indicativo de bid:** ⚪ INDEFINIDO (faltam dados para decidir)

A RFP 'RFP FICTÍCIA – SERVIÇOS DE FIELD SERVICES E SUPORTE DE TI' contém 41 itens analisados, distribuídos em 9 categorias. Foram identificadas 12 lacunas de informação e 7 riscos cruzados entre requisitos. Índice de clareza: 26/100.

**Justificativa:** Sinal calculado por regras determinísticas: faltam dados essenciais para precificar (volumetria e/ou penalidades).

_Sinal INDICATIVO gerado automaticamente. A decisão de bid/no-bid e a declaração de aderência são responsabilidade do comitê de pré-vendas._

| Indicador | Valor |
|---|---|
| Requisitos analisados | 41 |
| Criticidade alta | 20 |
| Risco alto (por requisito) | 3 |
| Lacunas de informação | 12 (3 de severidade alta) |
| Riscos cruzados | 7 (2 de severidade alta) |
| Ambiguidades detectadas | 11 |
| Índice de clareza da RFP | 26/100 |

**Principais riscos**

- Preço fixo sem volumetria definida
- SLA de início agressivo com atendimento presencial multi-site
- Meta de disponibilidade sem janela de cobertura
- SLAs medem apenas o início do atendimento
- Ramp-up curto com exigência de perfis experientes

**Próximos passos**

1. Enviar ao cliente as perguntas de esclarecimento de prioridade ALTA
2. Montar premissas de precificação explícitas para cada lacuna de prioridade ALTA
3. Validar a matriz de requisitos com as áreas responsáveis (coluna 'Área')
4. Preencher o status de aderência (Atende/Parcial/Não atende) na matriz
5. Levar o sinal de bid ao comitê de pré-vendas com os riscos mitigados

## 2. Riscos cruzados entre requisitos

| ID | Sev. | Risco | Requisitos | Mitigação sugerida |
|---|---|---|---|---|
| RX-01 | 🔴 ALTA | **Preço fixo sem volumetria definida** — A RFP exige valor mensal fechado com todos os custos inclusos, mas não informa quantidade de usuários nem volume de chamados. | RC-01, RC-02, PEN-01, PEN-02 | Precificar com premissas explícitas de volumetria e banda de variação (ex.: ±15%), com cláusula de repactuação fora da banda. |
| RX-02 | 🔴 ALTA | **SLA de início agressivo com atendimento presencial multi-site** — Início de atendimento em até 15–30 minutos combinado com presença física em várias localidades exige técnico residente por site ou início remoto. | SLA-01, SLA-02, LOC-01 | Propor que 'início de atendimento' seja contabilizado pelo primeiro contato remoto (registro no ITSM) e dimensionar ao menos um técnico residente por unidade. |
| RX-03 | 🟠 MEDIA | **Meta de disponibilidade sem janela de cobertura** — A disponibilidade é exigida 'durante o horário contratado', que não é definido na RFP. | SLA-06, PEN-05 | Explicitar na proposta a janela assumida e a fórmula de cálculo da disponibilidade. |
| RX-04 | 🟠 MEDIA | **SLAs medem apenas o início do atendimento** — Não há meta de solução: o cliente pode, durante a execução, cobrar resolução com expectativa implícita não precificada. | SLA-01, SLA-02, SLA-03, SLA-04 | Propor metas de solução como indicador de acompanhamento (não penalizável) ou precificá-las explicitamente. |
| RX-05 | 🟠 MEDIA | **Ramp-up curto com exigência de perfis experientes** — Implantação total em até 30 dias exige recrutar perfis com experiência mínima comprovada em paralelo à transição. | PRZ-02, PP-01, PP-02, PP-04, PP-05 | Iniciar pipeline de recrutamento na fase de proposta e prever operação assistida (hypercare) com metas de SLA escalonadas nos primeiros 60 dias. |
| RX-06 | 🟠 MEDIA | **Deslocamentos embutidos no preço sem volumetria de visitas** — Custos de deslocamento devem estar no preço fixo, mas a frequência de visitas e os deslocamentos extraordinários não são estimados. | RC-02, LOC-01, LOC-02, LOC-03 | Separar deslocamentos ordinários (no preço) de extraordinários (reembolso sob aprovação). |
| RX-07 | 🟢 BAIXA | **Fluxo de caixa: pagamento condicionado a validação e aceite** — Folha é paga mensalmente, mas o recebimento ocorre 30 dias após validação e aceite, sem prazo máximo de validação — exige capital de giro. | RC-03, RC-04 | Incluir custo financeiro no preço e propor prazo máximo para validação (aceite tácito). |

## 3. Lacunas de informação

| Sev. | Tópico | Status | Por que importa |
|---|---|---|---|
| 🔴 ALTA | Volumetria (usuários e chamados) | Pendente na RFP (PEN-01, PEN-02) | Sem volumetria não há base para dimensionar equipe nem precificar. |
| 🔴 ALTA | Horário de cobertura do serviço | Pendente na RFP (PEN-05) | SLAs e disponibilidade dependem da janela de cobertura (8x5, 12x6, 24x7). |
| 🔴 ALTA | Penalidades / glosas por descumprimento | Ausente | Exposição financeira desconhecida impede precificar o risco. |
| 🟠 MEDIA | SLA de solução (tempo de resolução) | Ausente | Medir apenas o início do atendimento abre espaço para disputas sobre a qualidade da entrega. |
| 🟠 MEDIA | Critérios de julgamento das propostas | Ausente | Sem critérios de julgamento não é possível calibrar o posicionamento técnico vs. preço. |
| 🟠 MEDIA | Cronograma do processo de RFP | Ausente | Datas do processo (perguntas, entrega, apresentação) não informadas. |
| 🟠 MEDIA | Reajuste contratual | Ausente | Contrato de mão de obra intensiva exige regra de reajuste (dissídio/índice). |
| 🟠 MEDIA | LGPD / tratamento de dados pessoais | Ausente | Técnicos acessam equipamentos com dados pessoais; papéis LGPD precisam estar claros. |
| 🟢 BAIXA | Matriz de escalonamento | Ausente | Fronteira entre N2 da contratada e N1/N3 da contratante não está definida. |
| 🟢 BAIXA | Plano de saída (desmobilização) | Ausente | Obrigações de repasse no encerramento podem gerar custo não previsto. |
| 🟢 BAIXA | Garantias contratuais / seguros | Ausente | Garantias exigidas impactam custo financeiro da proposta. |
| 🟢 BAIXA | Subcontratação | Ausente | Cobertura nacional pode exigir parceiros locais; a RFP não diz se é permitido. |

## 4. Perguntas de esclarecimento (priorizadas)

1. 🔴 Quantos usuários serão atendidos em cada localidade? _(ref.: PEN-01)_
2. 🔴 Qual é o volume médio mensal de chamados por categoria e prioridade? _(ref.: PEN-02)_
3. 🔴 Qual ferramenta ITSM será disponibilizada pela CONTRATANTE? _(ref.: PEN-03)_
4. 🔴 Existem usuários VIP que necessitam de níveis de serviço diferenciados? _(ref.: PEN-04)_
5. 🔴 Será necessário atendimento fora do horário comercial, aos finais de semana ou feriados? _(ref.: PEN-05)_
6. 🔴 A CONTRATANTE fornecerá notebooks e demais equipamentos necessários para os profissionais alocados? _(ref.: PEN-06)_
7. 🔴 Quais penalidades/glosas se aplicam ao descumprimento de SLA e qual o teto mensal?
8. 🔴 Qual o horário de cobertura contratado? _(ref.: SLA-06)_
9. 🔴 As políticas podem ser enviadas antes da proposta? _(ref.: SEG-03)_
10. 🔴 Qual o prazo máximo (em minutos) para a comunicação? _(ref.: SEG-04)_
11. 🟠 Haverá metas de tempo de solução por prioridade? Como serão medidas e pausadas?
12. 🟠 Quais os critérios e pesos de avaliação técnica e comercial?
13. 🟠 Qual o cronograma do processo (prazo de perguntas, entrega da proposta e decisão)?
14. 🟠 Qual o índice e a periodicidade de reajuste, inclusive em caso de prorrogação?
15. 🟠 A contratada atuará como operadora de dados pessoais? Haverá DPA/aditivo LGPD?
16. 🟠 Qual o inventário de periféricos suportados? _(ref.: RT-01)_
17. 🟠 Existe limite de volume/escopo? _(ref.: RT-04)_
18. 🟠 Qual a periodicidade mínima de atualização? _(ref.: RT-05)_
19. 🟠 Quais critérios definem a viabilidade do atendimento remoto? _(ref.: LOC-02)_
20. 🟠 Qual o fluxo e SLA de aprovação? _(ref.: LOC-03)_
21. 🟠 Como a competência será avaliada (entrevista, certificação)? _(ref.: PP-05)_
22. 🟢 Qual a fronteira de responsabilidade e o fluxo de escalonamento entre N1, N2 e N3?
23. 🟢 Há obrigações de transição de saída ao término do contrato? Por quanto tempo?
24. 🟢 Será exigida garantia contratual ou seguro? Em que percentual?
25. 🟢 É permitida subcontratação/parceiros para atendimento em localidades remotas?

## 5. Matriz de requisitos

| Código | Categoria | Obrig. | Critic. | Risco | Custo | Área | Resumo |
|---|---|---|---|---|---|---|---|
| RT-01 | TECNICO | OBRIGATORIO | 🟠 | 🟠 | 🟠 | Engenharia de Soluções | A CONTRATADA deverá prestar suporte técnico de Nível 2 para desktops, notebooks, monitores, impressoras, dispositivos móveis e periféricos utilizados pelos usuários. |
| RT-02 | TECNICO | OBRIGATORIO | 🟠 | 🟢 | 🟠 | Engenharia de Soluções | Os profissionais deverão realizar instalação, configuração, atualização e troubleshooting dos sistemas operacionais Windows 11. |
| RT-03 | TECNICO | OBRIGATORIO | 🟠 | 🟢 | 🟠 | Engenharia de Soluções | O serviço deverá contemplar suporte ao Microsoft 365, Microsoft Teams, Outlook e OneDrive. |
| RT-04 | TECNICO | OBRIGATORIO | 🟠 | 🟠 | 🟠 | Engenharia de Soluções | A solução deverá registrar e acompanhar todos os chamados por meio da ferramenta ITSM disponibilizada pela CONTRATANTE. |
| RT-05 | TECNICO | OBRIGATORIO | 🟠 | 🟠 | 🟠 | Engenharia de Soluções | A CONTRATADA deverá manter documentação atualizada dos procedimentos técnicos e da base de conhecimento utilizada pela equipe. |
| RC-01 | COMERCIAL | OBRIGATORIO | 🔴 | 🟢 | 🔴 | Comercial/Financeiro | A proposta comercial deverá apresentar o valor mensal do serviço e o valor total estimado para o período contratual. |
| RC-02 | COMERCIAL | OBRIGATORIO | 🔴 | 🟠 | 🔴 | Comercial/Financeiro | Todos os custos com salários, benefícios, impostos, equipamentos e deslocamentos da equipe deverão estar incluídos na proposta. |
| RC-03 | COMERCIAL | OBRIGATORIO | 🔴 | 🟢 | 🔴 | Comercial/Financeiro | O faturamento será realizado mensalmente após a validação dos serviços prestados. |
| RC-04 | COMERCIAL | OBRIGATORIO | 🔴 | 🟢 | 🔴 | Comercial/Financeiro | O prazo fictício de pagamento será de 30 dias após a emissão e aceite da nota fiscal. |
| RC-05 | COMERCIAL | OBRIGATORIO | 🔴 | 🟢 | 🔴 | Comercial/Financeiro | A proposta comercial deverá permanecer válida por pelo menos 60 dias após sua apresentação. |
| SLA-01 | SLA | OBRIGATORIO | 🔴 | 🔴 | 🔴 | Operações/Service Delivery | Chamados de prioridade crítica deverão ter início de atendimento em até 15 minutos. |
| SLA-02 | SLA | OBRIGATORIO | 🔴 | 🔴 | 🔴 | Operações/Service Delivery | Chamados de prioridade alta deverão ter início de atendimento em até 30 minutos. |
| SLA-03 | SLA | OBRIGATORIO | 🔴 | 🟢 | 🔴 | Operações/Service Delivery | Chamados de prioridade média deverão ter início de atendimento em até 2 horas. |
| SLA-04 | SLA | OBRIGATORIO | 🔴 | 🟢 | 🔴 | Operações/Service Delivery | Chamados de prioridade baixa deverão ter início de atendimento em até 4 horas. |
| SLA-05 | SLA | OBRIGATORIO | 🔴 | 🟠 | 🔴 | Operações/Service Delivery | A meta mensal de cumprimento dos SLAs deverá ser igual ou superior a 95%. |
| SLA-06 | SLA | OBRIGATORIO | 🔴 | 🔴 | 🔴 | Operações/Service Delivery | A disponibilidade mensal do serviço deverá ser de pelo menos 99,5% durante o horário contratado. |
| SEG-01 | SEGURANCA | OBRIGATORIO | 🔴 | 🟠 | 🟢 | Segurança da Informação | Todos os profissionais deverão assinar termo de confidencialidade antes do início das atividades. |
| SEG-02 | SEGURANCA | OBRIGATORIO | 🔴 | 🟢 | 🟢 | Segurança da Informação | O acesso aos ambientes da CONTRATANTE deverá utilizar contas individuais, sendo proibido o compartilhamento de credenciais. |
| SEG-03 | SEGURANCA | OBRIGATORIO | 🔴 | 🟠 | 🟢 | Segurança da Informação | A CONTRATADA deverá seguir as políticas de segurança da informação fornecidas pela CONTRATANTE. |
| SEG-04 | SEGURANCA | OBRIGATORIO | 🔴 | 🟠 | 🟢 | Segurança da Informação | Qualquer incidente de segurança identificado durante o atendimento deverá ser comunicado imediatamente ao responsável designado pela CONTRATANTE. |
| SEG-05 | SEGURANCA | OBRIGATORIO | 🔴 | 🟢 | 🟢 | Segurança da Informação | Dados corporativos não poderão ser copiados para dispositivos pessoais ou serviços de armazenamento não autorizados. |
| LOC-01 | LOCALIDADE | OBRIGATORIO | 🟠 | 🟢 | 🔴 | Operações/Service Delivery | O atendimento presencial deverá ser disponibilizado nas unidades fictícias de São Paulo/SP, Curitiba/PR e Belo Horizonte/MG. |
| LOC-02 | LOCALIDADE | INFORMATIVO | 🟠 | 🟠 | 🔴 | Operações/Service Delivery | Usuários de outras localidades brasileiras poderão receber atendimento remoto quando tecnicamente possível. |
| LOC-03 | LOCALIDADE | OBRIGATORIO | 🟠 | 🟠 | 🔴 | Operações/Service Delivery | Deslocamentos extraordinários entre localidades deverão ser previamente aprovados pela CONTRATANTE. |
| PRZ-01 | PRAZO | OBRIGATORIO | 🔴 | 🟠 | 🟠 | PMO/Transição | A CONTRATADA deverá apresentar o plano de transição em até 10 dias úteis após a assinatura do contrato. |
| PRZ-02 | PRAZO | OBRIGATORIO | 🔴 | 🟢 | 🟠 | PMO/Transição | A operação deverá estar totalmente implantada em até 30 dias corridos após a assinatura do contrato. |
| PRZ-03 | PRAZO | OBRIGATORIO | 🔴 | 🟢 | 🟠 | PMO/Transição | O contrato terá duração fictícia de 12 meses, podendo ser prorrogado mediante acordo entre as partes. |
| PRZ-04 | PRAZO | OBRIGATORIO | 🔴 | 🟢 | 🟠 | PMO/Transição | Relatórios mensais deverão ser apresentados até o quinto dia útil do mês seguinte ao período de referência. |
| PP-01 | PERFIL | OBRIGATORIO | 🟠 | 🟢 | 🔴 | RH/Recrutamento | O Analista de Suporte Nível 2 deverá possuir experiência mínima de 2 anos em suporte técnico a usuários corporativos. |
| PP-02 | PERFIL | OBRIGATORIO | 🟠 | 🟢 | 🔴 | RH/Recrutamento | O profissional deverá possuir conhecimentos em Windows 11, Microsoft 365, hardware de notebooks e desktops, redes básicas e ferramentas de acesso remoto. |
| PP-03 | PERFIL | DESEJAVEL | 🟢 | 🟢 | 🔴 | RH/Recrutamento | Será desejável conhecimento de ITIL 4 e boas práticas de gerenciamento de serviços de TI. |
| PP-04 | PERFIL | OBRIGATORIO | 🟠 | 🟢 | 🔴 | RH/Recrutamento | O Coordenador de Serviços deverá possuir experiência mínima de 3 anos em coordenação de equipes de suporte e acompanhamento de indicadores de SLA. |
| PP-05 | PERFIL | OBRIGATORIO | 🟠 | 🟠 | 🔴 | RH/Recrutamento | Os profissionais deverão possuir boa comunicação, capacidade de documentação e atendimento ao usuário. |
| GOV-01 | GOVERNANCA | OBRIGATORIO | 🟠 | 🟢 | 🟢 | Operações/Service Delivery | A CONTRATADA deverá fornecer relatório mensal contendo volume de chamados, classificação por prioridade, percentual de cumprimento de SLA, principais incidentes e backlog. |
| GOV-02 | GOVERNANCA | OBRIGATORIO | 🟠 | 🟢 | 🟢 | Operações/Service Delivery | Deverá ser realizada reunião mensal de acompanhamento dos indicadores e definição dos planos de ação necessários. |
| PEN-01 | PENDENCIA | INFORMATIVO | 🟠 | 🟢 | 🟠 | Pré-vendas | Quantos usuários serão atendidos em cada localidade? |
| PEN-02 | PENDENCIA | INFORMATIVO | 🟠 | 🟢 | 🟠 | Pré-vendas | Qual é o volume médio mensal de chamados por categoria e prioridade? |
| PEN-03 | PENDENCIA | INFORMATIVO | 🟠 | 🟢 | 🟠 | Pré-vendas | Qual ferramenta ITSM será disponibilizada pela CONTRATANTE? |
| PEN-04 | PENDENCIA | INFORMATIVO | 🟠 | 🟢 | 🟠 | Pré-vendas | Existem usuários VIP que necessitam de níveis de serviço diferenciados? |
| PEN-05 | PENDENCIA | INFORMATIVO | 🟠 | 🟢 | 🟠 | Pré-vendas | Será necessário atendimento fora do horário comercial, aos finais de semana ou feriados? |
| PEN-06 | PENDENCIA | INFORMATIVO | 🟠 | 🟢 | 🟠 | Pré-vendas | A CONTRATANTE fornecerá notebooks e demais equipamentos necessários para os profissionais alocados? |

## 6. Rastreabilidade e uso de IA

- Modelos utilizados: nenhum (modo determinístico)
- Chamadas LLM: 0 (cache: 0) · tokens: 0
- Fallback de modelo acionado: não
- Modo degradado (heurístico): sim
- Cobertura de enriquecimento por LLM: 0.0%
- Alertas de segurança: nenhum
- Versões de prompt: enrich_requirements@1.0.0, extract_requirements@1.0.0, executive_summary@1.0.0
- SHA-256 do documento: `9d726f38f6678c30a813cb89ffff1678dc76a7bae3972a3fe987e68d9c6fa647`
