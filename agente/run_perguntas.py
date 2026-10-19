"""
run_perguntas.py -- Roda as 5 perguntas obrigatorias do case e grava
respostas.md com a resposta REAL de cada rodada + o comentario fixo
definido em COMENTARIOS (o enunciado pede esse comentario
explicitamente -- "comente onde o agente acertou, onde errou e o que
voce faria pra melhorar", nao e opcional).

Os comentarios moraram antes dentro do .md gerado, mas esse arquivo e
sobrescrito toda vez que o script roda -- ou seja, cada nova rodada
apagava o comentario anterior. Agora o comentario vive aqui, em codigo,
e e remontado junto com a resposta nova a cada execucao. Pra mudar o
texto de um comentario, edita o dict COMENTARIOS abaixo; pra ver a
resposta mais recente do agente, so rodar de novo.
"""
from agent import agent, Deps
import db

PERGUNTAS = [
    "Qual o score da Gerência de Marketing?",
    "Quais colaboradores do time da Sofia Oliveira ficaram com score abaixo de 90?",
    "Qual diretoria teve o melhor resultado consolidado?",
    "Quais metas do Nicolas Vasconcelos ficaram abaixo de 80% de atingimento?",
    "Qual o score da área Vendas Oeste?",
]

COMENTARIOS = {
    1: (
        "Na primeira rodada essa pergunta falhou — mas por um bug meu no roteiro de "
        "teste, não do agente: eu tinha escrito a pergunta sem o acento (\"Gerencia\"), "
        "e a área no banco é \"Gerência de Marketing\", com acento. ILIKE ignora "
        "maiúsculas/minúsculas, mas não ignora acento, então o nome sem acento não "
        "encontrava a área. O comportamento do agente diante da falha foi o certo mesmo "
        "assim: não achou, não chutou uma área parecida, pediu confirmação do nome — o "
        "mesmo padrão correto da pergunta 5, só que aqui o erro de origem era meu. "
        "Corrigi o roteiro e a resposta ficou certa: score_direto = score_consolidado = "
        "84,43 (conferido direto no CSV), área sem subárea. Lição: a resolução de nome "
        "por ILIKE é sensível a acento — registrado em \"Limitações conhecidas\" no "
        "README, com a melhoria proposta (normalizar acento antes de comparar)."
    ),
    2: (
        "Acertou. Conferi contra os CSVs de forma independente: a Sofia Oliveira tem 12 "
        "subordinados diretos, e exatamente 3 ficaram abaixo de 90 (Sabrina Cardoso "
        "54,85, Manuela Oliveira 63,67, Gabriela Ferraz 89,30), valores batendo na casa "
        "decimal. Depois da auditoria, a tool passou a filtrar só colaboradores "
        "elegíveis (R10) por padrão -- esses três já vêm filtrados por construção da "
        "query, não por uma flag que o agente precisasse interpretar."
    ),
    3: (
        "Acertou. Diretoria Financeira (103,30) na frente de Comercial (95,08) e "
        "Operações (93,19), conferido direto no vw_score_area.csv. Pergunta sem "
        "ambiguidade (já pede \"consolidado\" explicitamente), e o ranking_areas "
        "resolveu em uma chamada."
    ),
    4: (
        "Os dados continuam certos (2 metas, atingimento e peso batendo com "
        "vw_nota_meta.csv). MELHORIA APLICADA E VERIFICADA: o SYSTEM_PROMPT em "
        "agent.py passou a incluir um resumo das regras R6 (faixa de nota), R9 "
        "(score do colaborador) e R11 (score de área direto/consolidado) -- antes só "
        "os números calculados chegavam ao agente, nunca a regra por trás deles. "
        "Nesta rodada pós-mudança, a explicação citou a regra direto e com certeza "
        "(\"a regra de negócio diz que atingimento abaixo de 80% trava a nota em "
        "0... não é erro de lançamento, é consequência direta\"), sem hedge -- antes "
        "da mudança, uma rodada tinha dito \"provavelmente por estarem abaixo de "
        "algum limiar mínimo\", tratando como suposição uma regra determinística. "
        "Ressalva honesta: só rodei uma vez depois da mudança, não várias -- não dá "
        "pra afirmar que a variância sumiu de forma definitiva, só que a causa raiz "
        "(agente sem acesso à regra, tendo que adivinhar) foi removida, o que deveria "
        "eliminar o problema por construção, não por sorte dessa rodada."
    ),
    5: (
        "Acertou, e é o teste mais importante dos 5. \"Vendas Oeste\" não existe na base "
        "-- as áreas de Vendas reais são Coordenação Vendas Sul e Coordenação Vendas "
        "Norte (conferido direto contra área no SQL Server e contra area.csv). O agente "
        "não alucinou um número pra Sul ou Norte, não arredondou pro nome mais parecido "
        "-- disse que não encontrou e, numa das rodadas, foi ainda mais conservador: "
        "disse explicitamente que não tinha como sugerir um nome parecido \"com "
        "segurança\" porque não tinha consultado as outras áreas de vendas naquela "
        "conversa, em vez de supor Sul/Norte/Leste sem checar. É a prova de que a "
        "decisão de desenho (resolver_por_nome nunca \"pega o primeiro\", status "
        "nao_encontrado tratado explicitamente no prompt) funciona na prática. "
        "Ressalva: nesta rodada específica o agente sugeriu \"Vendas Norte/Sul\" "
        "sem ter consultado nenhuma tool antes -- o palpite acertou e veio com "
        "hedge, mas o prompt pede sugestão só a partir de nomes vistos em "
        "chamadas anteriores, e aqui ele não seguiu isso à risca."
    ),
}


def main():
    conn = db.get_connection()
    deps = Deps(conn=conn)
    linhas = ["# Respostas do agente -- case Mereo", ""]
    for i, pergunta in enumerate(PERGUNTAS, start=1):
        print(f"[{i}/5] {pergunta}")
        resultado = agent.run_sync(pergunta, deps=deps)
        linhas.append(f"## {i}. {pergunta}")
        linhas.append("")
        linhas.append(resultado.output)
        linhas.append("")
        comentario = COMENTARIOS.get(i, "_[sem comentario definido em COMENTARIOS]_")
        linhas.append(f"**Comentario:** {comentario}")
        linhas.append("")

    with open("respostas.md", "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))
    print("\nSalvo em agente/respostas.md")


if __name__ == "__main__":
    main()
