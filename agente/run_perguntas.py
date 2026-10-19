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
        "Na primeira rodada essa pergunta falhou -- mas por um bug meu no roteiro de "
        "teste, nao do agente: eu tinha escrito \"Gerencia\" sem o acento circunflexo "
        "aqui no script, e a area no banco e \"Gerencia de Marketing\". ILIKE normaliza "
        "maiusculas/minusculas mas nao remove acento, entao \"Gerencia\" nunca batia com "
        "\"Gerencia\". O comportamento do agente diante da falha foi o certo mesmo assim: "
        "nao achou, nao chutou pra area parecida, pediu confirmacao do nome -- o mesmo "
        "padrao correto da pergunta 5, so que aqui o erro de origem era meu. Corrigi o "
        "typo e a resposta ficou certa: score_direto = score_consolidado = 84,43 "
        "(conferido direto no CSV), area sem subarea. O que fica como licao: resolucao "
        "de nome por ILIKE e sensivel a acento, e isso nao estava documentado como "
        "limitacao conhecida -- devia estar no README."
    ),
    2: (
        "Acertou. Conferi contra os CSVs de forma independente: a Sofia Oliveira tem 12 "
        "subordinados diretos, e exatamente 3 ficaram abaixo de 90 (Sabrina Cardoso "
        "54,85, Manuela Oliveira 63,67, Gabriela Ferraz 89,30), valores batendo na casa "
        "decimal. O agente tambem devolveu a elegibilidade R10 de cada um sem eu pedir "
        "-- a tool inclui esse campo de proposito, pra transparencia, e o agente usou bem."
    ),
    3: (
        "Acertou. Diretoria Financeira (103,30) na frente de Comercial (95,08) e "
        "Operacoes (93,19), conferido direto no vw_score_area.csv. Pergunta sem "
        "ambiguidade (ja pede \"consolidado\" explicitamente), e o ranking_areas "
        "resolveu em uma chamada."
    ),
    4: (
        "Os dados estao certos nas duas rodadas que rodei (2 metas, atingimento e peso "
        "batendo com vw_nota_meta.csv), mas a EXPLICACAO mudou entre uma rodada e outra "
        "pro mesmo resultado: numa vez o agente disse \"nota zero... provavelmente por "
        "estarem abaixo de algum limiar minimo\" (tratando como suposicao uma regra "
        "deterministica), e noutra citou a R6 explicitamente e com certeza. Mesmos "
        "dados, mesma tool, explicacao diferente -- porque o system prompt nunca deu as "
        "regras de negocio ao agente, so os numeros ja calculados; quando ele tenta "
        "explicar o porque, as vezes acerta por inferencia, as vezes specula. Melhoria "
        "clara: colocar um resumo das regras-chave (pelo menos R6) no system prompt, pra "
        "tirar essa variancia e ele responder com certeza sempre, nao por sorte."
    ),
    5: (
        "Acertou, e e o teste mais importante dos 5. \"Vendas Oeste\" nao existe na base "
        "-- as areas de Vendas reais sao Coordenacao Vendas Sul e Coordenacao Vendas "
        "Norte (conferido direto contra area no SQL Server e contra area.csv). O agente "
        "nao alucinou um numero pra Sul ou Norte, nao arredondou pro nome mais parecido "
        "-- disse que nao encontrou e, numa das rodadas, foi ainda mais conservador: "
        "disse explicitamente que nao tinha como sugerir um nome parecido \"com "
        "seguranca\" porque nao tinha consultado as outras areas de vendas naquela "
        "conversa, em vez de supor Sul/Norte/Leste sem checar. E a prova de que a "
        "decisao de desenho (resolver_por_nome nunca \"pega o primeiro\", status "
        "nao_encontrado tratado explicitamente no prompt) funciona na pratica."
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
