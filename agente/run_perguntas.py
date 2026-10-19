"""
run_perguntas.py -- Roda as 5 perguntas obrigatorias do case e salva as
respostas em agente/respostas.md, com um placeholder de comentario pra
cada uma (onde o agente acertou/errou, o que melhorar -- exigencia
explicita do enunciado, Eduardo completa a mao).
"""
from agent import agent, Deps
import db

PERGUNTAS = [
    "Qual o score da Gerencia de Marketing?",
    "Quais colaboradores do time da Sofia Oliveira ficaram com score abaixo de 90?",
    "Qual diretoria teve o melhor resultado consolidado?",
    "Quais metas do Nicolas Vasconcelos ficaram abaixo de 80% de atingimento?",
    "Qual o score da area Vendas Oeste?",
]


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
        linhas.append("**Comentario:** _[Eduardo completa aqui: onde o agente acertou, onde errou, o que melhoraria]_")
        linhas.append("")

    with open("respostas.md", "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))
    print("\nSalvo em agente/respostas.md")


if __name__ == "__main__":
    main()
