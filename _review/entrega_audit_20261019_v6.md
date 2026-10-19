# Auditoria de Entrega · Case Mereo (Grupo Aurora) · case-mereo-analytics-engineer
> Score estimado: **93/100 — FORTE — pronto para submeter após 2 ajustes curtos**
> Gerado por `/auditoria-entrega-mereo` em 2026-10-19, 6ª rodada (HEAD `158378e`, **1 commit à frente de `origin/main`**). Rodadas anteriores: [1ª](entrega_audit_20261019.md) 84 · [2ª](entrega_audit_20261019_v2.md) 91 · [3ª](entrega_audit_20261019_v3.md) 92 · [4ª](entrega_audit_20261019_v4.md) 92 · [5ª](entrega_audit_20261019_v5.md) 93.

---

## Veredicto

Os dois achados de baixo impacto da 5ª rodada foram fechados: a rodada certa (4ª) agora é citada no doc do painel, e R6/R9/R11 entraram no system prompt. A melhoria do prompt funcionou no que se propunha: a pergunta 4 agora explica a nota zero citando a regra, sem especular. O comentário registra com honestidade que foi uma rodada só. Os números seguem idênticos ("TUDO CONFERE") e não há chave de API no repositório.

A mesma mudança trouxe dois problemas novos, e por isso o score fica em 93 em vez de subir:

1. **O resumo de R9 no prompt descreve R8 errado.** Diz que a meta sai do score quando falta lançamento válido "no mês". O enunciado diz que só sai quando *nenhum* mês conta. É regra de negócio errada dentro do agente, a parte do case que a vaga mais valoriza ("validar os dados e as consultas que alimentam" os agentes).
2. **O README principal continua descrevendo o prompt antigo** ("o system prompt nunca deu as regras", com a melhoria listada como futura), enquanto o `agente/README` e o `respostas.md` dizem que ela foi aplicada.

Os dois se resolvem em ~10 min, sem precisar rodar o LLM de novo.

---

## Score por critério (pesos exatos do enunciado)

| Critério | Peso | Nota estimada | Pontos | Gaps críticos | Δ vs 5ª rodada |
|---|---|---|---|---|---|
| Corretude dos números (Parte 1) | 30% | 9.5/10 | 28.5/30 | 0 | = |
| Problemas de qualidade | 20% | 9.5/10 | 19.0/20 | 0 | = |
| Agente de IA | 20% | 9.0/10 | 18.0/20 | 0 | = (melhoria aplicada +, regra mal resumida −) |
| Painel | 15% | 9.5/10 | 14.25/15 | 0 | = |
| Perguntas abertas | 10% | 9.0/10 | 9.0/10 | 0 | = |
| Organização e README | 5% | 8.5/10 | 4.25/5 | 0 | −0.5 |
| **TOTAL** | **100%** | — | **93/100** | — | **=** |

Com os gaps 1 e 2 corrigidos: Agente 9.5 e Organização 9.0, total **94**.

---

## Verificação de reprovação imediata

| Critério | Status |
|---|---|
| `respostas/p1_*`, `p2_*`, `p3_*` presentes e com conteúdo | ✅ |
| `verificacao_independente.py` existe e é independente | ✅ TUDO CONFERE |
| Estrutura bate com README.md / sql/ / respostas/ / painel/ / agente/ | ✅ |
| `agente/respostas.md` sem placeholder | ✅ regenerado após a mudança do prompt; os 5 números batem |
| As 3 perguntas abertas respondidas | ✅ 10/10/10 |

Nenhum bloqueador.

---

## Status dos gaps da 5ª rodada

| # | Gap | Status |
|---|---|---|
| 1 | Doc do painel citava a 2ª rodada em vez da 4ª | ✅ `powerbi_construcao_painel.md` corrigido nos dois pontos |
| 2 | R6 no system prompt (opcional) | ✅ aplicado (R6/R9/R11), `respostas.md` regenerado, comentário 4 atualizado com ressalva. ⚠️ mas ver gaps 1 e 2 abaixo |

---

## Gaps por impacto na nota

### Impacto alto

Nenhum.

### Impacto médio (corrigir antes do push)

**1. O system prompt resume R8 errado dentro da explicação de R9** — Agente (20%) · ~3 min

`agente/agent.py`, `SYSTEM_PROMPT`:
> *"Score do colaborador: soma(nota x peso) / soma(peso), considerando so as metas que tem nota (**uma meta sem lancamento valido no mes** nao entra nem no numerador nem no denominador)."*

Enunciado: *"R8. Meta sem nota. Uma meta **sem nenhum mês que conte** fica sem nota e não entra no score."* Um mês sem lançamento válido só sai do cálculo do atingimento (R3/R4). A meta continua no score com os meses que contam. Com o texto atual, perguntado "por que a meta X do fulano não pesou no score?", o agente pode explicar com a regra errada, e com a "certeza" que a mudança quis justamente induzir. Hoje nenhuma das 5 perguntas exercita esse trecho, por isso o `respostas.md` não mostra o erro.

Correção (não precisa rerodar o LLM, porque as 5 respostas não tocam em R8):
```
- Score do colaborador: soma(nota x peso) / soma(peso), considerando so
  as metas que tem nota. Uma meta sem NENHUM mes valido no ciclo fica
  sem nota e nao entra no score; um mes isolado sem lancamento valido
  so sai do calculo do atingimento daquela meta.
```

**2. O README principal ainda descreve o prompt antigo** — Organização (5%) · ~5 min

`README.md:586-602` ("Onde acertou, onde errou, o que eu melhoraria"):
- *"porque o system prompt nunca deu as regras de negócio ao agente, só os números já calculados"*: no presente, e não é mais verdade;
- *"O que eu faria para melhorar: (1) colocar um resumo das regras-chave (pelo menos R6) no system prompt"*: já foi feito.

O `agente/README.md` e o comentário 4 do `respostas.md` dizem "aplicado e verificado". O avaliador lê o README principal primeiro, e é o único dos três que ficou desatualizado. Correção: espelhar o texto do `agente/README` (passado para a causa, "(1) aplicado: ..." com a ressalva de uma rodada só).

### Impacto baixo (nice to have)

**3. Na pergunta 5, o agente sugeriu nomes que não consultou** — Agente · ~2 min (só texto)

Nesta rodada, a resposta da pergunta 5 diz *"pode haver 'Vendas Norte', 'Vendas Sul' ou outra variação cadastrada"* sem ter chamado nenhuma tool de área. O prompt pede para sugerir só nomes "a partir de outras chamadas". O palpite acertou (as coordenações existem) e veio com hedge, então não é alucinação de número. Mas o comentário 5 celebra justamente a rodada em que ele *não* fez isso. Uma frase no comentário ("nesta rodada sugeriu Norte/Sul sem consultar, com hedge; o prompt pede sugestão só a partir de consulta") mantém o padrão de honestidade dos outros comentários.

**4. Commit `158378e` não enviado** — ~1 min

`main` está 1 à frente de `origin/main`. Se o avaliador recebe o link do repositório, a melhoria do prompt ainda não está lá. Fazer push depois de corrigir os gaps 1 e 2.

---

## Checklist final antes de submeter

**Corretude (30%)**
- [x] Verificação independente pandas (0.0000) + T-SQL contra `staging` (PASS)

**Qualidade (20%)**
- [x] Achados reconciliados, decisões justificadas e medidas

**Agente de IA (20%)**
- [x] Tools fixas, `respostas.md` real e regenerado, sem chave no repo
- [x] Regras de negócio no prompt (melhoria aplicada)
- [ ] Resumo das regras no prompt fiel ao enunciado. **R8 (gap 1)**

**Painel (15%)**
- [x] Sem mudanças desde a 5ª rodada; tudo ok

**Perguntas abertas (10%)**
- [x] 10/10/10 linhas, exemplos concretos

**Organização e README (5%)**
- [ ] README principal, `agente/README` e `respostas.md` contam a mesma história sobre o prompt (gap 2)
- [ ] Push feito (gap 4)

---

## Como re-auditar

```
claude "/auditoria-entrega-mereo"
```

---

*Case Mereo (Grupo Aurora) · /auditoria-entrega-mereo v2.0*
