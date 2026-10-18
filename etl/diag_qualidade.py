"""
diag_qualidade.py — Diagnóstico de qualidade de dados, Case Mereo (Grupo Aurora)

Lê as tabelas de staging.* no SQL Server, roda uma bateria de checks
declarativos (cada um isolado, auditável, com amostra de linhas problemáticas)
e gera um relatório em markdown + saída no terminal.

Uso:
    python etl/diag_qualidade.py
"""
import pyodbc
import pandas as pd
import datetime
import pathlib

SQLSERVER_CONN_STR = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=CaseMereo;"
    "Trusted_Connection=yes;"
)

REPORT_PATH = pathlib.Path(r"C:\Users\Fabian\Desktop\MEREO CASE\qualidade\relatorio_diagnostico.md")

ELEGIBILIDADE_ADM_LIMITE = datetime.date(2025, 9, 30)
ELEGIBILIDADE_DESLIG_LIMITE = datetime.date(2025, 7, 1)


# ---------------------------------------------------------------------------
# Carga
# ---------------------------------------------------------------------------
def load_data(conn):
    tables = {}
    for t in ["area", "ciclo", "colaborador", "meta", "meta_valor_mensal"]:
        tables[t] = pd.read_sql(f"SELECT * FROM staging.{t}", conn)
    return tables


# ---------------------------------------------------------------------------
# Helpers genéricos
# ---------------------------------------------------------------------------
def check(nome, severidade, df_problema, descricao):
    """Empacota o resultado de um check num formato padrão."""
    return {
        "nome": nome,
        "severidade": severidade,   # "info" | "atencao" | "critico"
        "qtd": len(df_problema),
        "amostra": df_problema.head(10),
        "descricao": descricao,
    }


def elegivel(adm, deslig):
    if pd.isna(adm):
        return False
    adm_d = adm.date() if hasattr(adm, "date") else adm
    if adm_d > ELEGIBILIDADE_ADM_LIMITE:
        return False
    if pd.notna(deslig):
        deslig_d = deslig.date() if hasattr(deslig, "date") else deslig
        if deslig_d < ELEGIBILIDADE_DESLIG_LIMITE:
            return False
    return True


def resolver_meta(m):
    """Aplica R7: para Compartilhada, usa polaridade/acumulação/lançamentos
    da meta referenciada. Devolve m com 3 colunas novas. Usado por mais de
    um check, então fica centralizado aqui em vez de duplicado."""
    m = m.copy()
    ref = m.set_index("id_meta")

    def pol(r):
        if r["tipo_meta"] == "Compartilhada" and pd.notna(r["id_meta_referencia"]) and r["id_meta_referencia"] in ref.index:
            return ref.loc[r["id_meta_referencia"], "polaridade"]
        return r["polaridade"]

    def acum(r):
        if r["tipo_meta"] == "Compartilhada" and pd.notna(r["id_meta_referencia"]) and r["id_meta_referencia"] in ref.index:
            return ref.loc[r["id_meta_referencia"], "tipo_acumulacao"]
        return r["tipo_acumulacao"]

    def lanc_id(r):
        if r["tipo_meta"] == "Compartilhada" and pd.notna(r["id_meta_referencia"]):
            return r["id_meta_referencia"]
        return r["id_meta"]

    m["polaridade_efetiva"] = m.apply(pol, axis=1)
    m["acumulacao_efetiva"] = m.apply(acum, axis=1)
    m["id_meta_lancamentos"] = m.apply(lanc_id, axis=1)
    return m


# ---------------------------------------------------------------------------
# Checks — estrutura / integridade referencial
# ---------------------------------------------------------------------------
def c_pk_duplicada(t):
    out = []
    for nome, col in [("area", "id_area"), ("ciclo", "id_ciclo"),
                       ("colaborador", "id_colaborador"), ("meta", "id_meta"),
                       ("meta_valor_mensal", "id_lancamento")]:
        dup = t[nome][t[nome][col].duplicated(keep=False)]
        out.append(check(f"PK duplicada em {nome}", "critico", dup,
                          f"{col} deveria ser único em {nome}"))
    return out


def c_fk_orfa(t):
    out = []
    orfaos = t["area"][~t["area"]["id_area_pai"].isna() &
                        ~t["area"]["id_area_pai"].isin(t["area"]["id_area"])]
    out.append(check("area.id_area_pai órfão", "critico", orfaos, "área pai inexistente"))

    orfaos = t["colaborador"][~t["colaborador"]["id_area"].isin(t["area"]["id_area"])]
    out.append(check("colaborador.id_area órfão", "critico", orfaos, "área inexistente"))

    orfaos = t["colaborador"][~t["colaborador"]["id_gestor"].isna() &
                               ~t["colaborador"]["id_gestor"].isin(t["colaborador"]["id_colaborador"])]
    out.append(check("colaborador.id_gestor órfão", "critico", orfaos, "gestor inexistente"))

    orfaos = t["meta"][~t["meta"]["id_colaborador"].isin(t["colaborador"]["id_colaborador"])]
    out.append(check("meta.id_colaborador órfão", "critico", orfaos, "colaborador inexistente"))

    orfaos = t["meta_valor_mensal"][~t["meta_valor_mensal"]["id_meta"].isin(t["meta"]["id_meta"])]
    out.append(check("meta_valor_mensal.id_meta órfão", "critico", orfaos, "meta inexistente"))
    return out


def c_hierarquia_gestor(t):
    edges = dict(zip(t["colaborador"]["id_colaborador"], t["colaborador"]["id_gestor"]))
    ciclos = []
    for start in edges:
        seen, cur = set(), start
        while cur is not None and not pd.isna(cur):
            if cur in seen:
                ciclos.append({"id_colaborador": start, "ciclo_em": cur})
                break
            seen.add(cur)
            cur = edges.get(cur)
    df = pd.DataFrame(ciclos)
    auto = t["colaborador"][t["colaborador"]["id_colaborador"] == t["colaborador"]["id_gestor"]]
    return [
        check("Ciclo na cadeia de gestores (multi-nível)", "critico", df,
              "colaborador é seu próprio gestor em algum nível acima"),
        check("Auto-gestor direto", "critico", auto, "id_gestor = id_colaborador"),
    ]


def c_gestor_fora_hierarquia(t):
    area_pai = dict(zip(t["area"]["id_area"], t["area"]["id_area_pai"]))

    def ancestrais(a):
        out = set()
        while a is not None and not pd.isna(a):
            out.add(a)
            a = area_pai.get(a)
        return out

    colab = t["colaborador"].set_index("id_colaborador")
    susp = []
    for cid, row in colab.iterrows():
        g = row["id_gestor"]
        if pd.isna(g) or g not in colab.index:
            continue
        garea = colab.loc[g, "id_area"]
        carea = row["id_area"]
        if garea != carea and garea not in ancestrais(carea):
            susp.append({"id_colaborador": cid, "area": carea, "id_gestor": g, "area_gestor": garea})
    df = pd.DataFrame(susp)
    return [check("Gestor fora da hierarquia de área do subordinado", "atencao", df,
                   "área do gestor não é a mesma nem ancestral da área do subordinado")]


# ---------------------------------------------------------------------------
# Checks — formatação / categorias
# ---------------------------------------------------------------------------
def c_espaco_em_branco(t):
    out = []
    for nome, col in [("area", "nome"), ("colaborador", "nome"), ("meta", "nome_meta")]:
        s = t[nome][col].astype(str)
        mask = (s != s.str.strip()) | s.str.contains("  ")
        out.append(check(f"{nome}.{col} com espaço extra", "atencao", t[nome][mask],
                          "nome com espaço no início/fim ou duplo espaço interno"))
    return out


def c_categorias(t):
    out = []
    m = t["meta"]
    for col, esperado in [("tipo_meta", {"Individual", "Compartilhada"}),
                           ("polaridade", {"Melhor para cima", "Melhor para baixo", None}),
                           ("tipo_acumulacao", {"Soma", "Média", None})]:
        vals = set(m[col].dropna().unique()) | ({None} if m[col].isna().any() else set())
        inesperado = vals - esperado
        out.append(check(f"meta.{col} com valor fora do esperado", "critico" if inesperado else "info",
                          m[m[col].isin(inesperado)] if inesperado else m.head(0),
                          f"valores encontrados: {vals}"))
    return out


def c_nome_duplicado_colaborador(t):
    dup = t["colaborador"][t["colaborador"]["nome"].duplicated(keep=False)]
    return [check("colaborador.nome duplicado", "info", dup, "mesmo nome em mais de um colaborador")]


# ---------------------------------------------------------------------------
# Checks — regras de negócio (achados já documentados + novos)
# ---------------------------------------------------------------------------
def c_peso(t):
    m = t["meta"][t["meta"]["id_ciclo"] == 2025].copy()
    out = []
    neg = m[m["peso"] < 0]
    out.append(check("meta.peso negativo", "atencao", neg, "ABS() aplicado em intermediate"))

    soma = m.groupby("id_colaborador")["peso"].sum().reset_index()
    diff = soma[soma["peso"] != 100]
    out.append(check("soma de peso por colaborador != 100", "info", diff,
                      "não quebra R9 (normaliza por soma de peso), mas documentar"))
    return out


def c_meta_compartilhada(t):
    m = t["meta"]
    ref = m.set_index("id_meta")
    comp = m[m["tipo_meta"] == "Compartilhada"].copy()
    comp["ref_tipo"] = comp["id_meta_referencia"].map(ref["tipo_meta"])
    comp["ref_ciclo"] = comp["id_meta_referencia"].map(ref["id_ciclo"])
    comp["ref_nome"] = comp["id_meta_referencia"].map(ref["nome_meta"])

    out = []
    out.append(check("Compartilhada apontando p/ outra Compartilhada", "critico",
                      comp[comp["ref_tipo"] == "Compartilhada"], "R7 assume referência direta a uma Individual"))
    out.append(check("Compartilhada sem id_meta_referencia", "critico",
                      comp[comp["id_meta_referencia"].isna()], "quebra o join de R7"))
    out.append(check("Compartilhada referenciando outro ciclo", "atencao",
                      comp[comp["id_ciclo"] != comp["ref_ciclo"]], "referência cruzada de ciclo"))
    out.append(check("Compartilhada com nome_meta divergente da referência", "atencao",
                      comp[comp["nome_meta"] != comp["ref_nome"]], "nome deveria ser igual ao da meta referenciada"))
    out.append(check("Individual com id_meta_referencia preenchido", "atencao",
                      m[(m["tipo_meta"] == "Individual") & (~m["id_meta_referencia"].isna())],
                      "campo deveria ser nulo"))
    return out


def c_compartilhada_lancamento_proprio(t):
    """ACHADO #5 — R7 diz que a Compartilhada usa os lançamentos da
    referência, não os próprios. Se a própria id_meta da Compartilhada
    aparece em meta_valor_mensal, é um sinal de carga incorreta (ou de uma
    regra não documentada). Esses lançamentos são ignorados no cálculo por
    construção (a view de meta resolvida nunca busca pelo id_meta original
    da Compartilhada), mas a presença deles merece registro."""
    m = t["meta"]
    comp_ids = set(m[m["tipo_meta"] == "Compartilhada"]["id_meta"])
    proprios = t["meta_valor_mensal"][t["meta_valor_mensal"]["id_meta"].isin(comp_ids)]
    return [check("Meta Compartilhada com lançamento mensal PRÓPRIO", "atencao", proprios,
                   "R7: deveria usar só os lançamentos da referência. Ignorado no cálculo, "
                   "mas é achado de carga a documentar")]


def c_meta_sem_lancamento(t):
    """ACHADO #6 — meta do ciclo 2025 sem NENHUMA linha em meta_valor_mensal.
    Resolve R7 antes de checar: para Compartilhada, o lançamento esperado
    está sob o id_meta DA REFERÊNCIA, não sob o id_meta da própria
    Compartilhada (que, corretamente, nunca tem linha própria — isso não é
    o achado #6, é o comportamento esperado por R7; o achado #5 é o
    inverso, quando ELA TEM linha própria por engano)."""
    m = resolver_meta(t["meta"][t["meta"]["id_ciclo"] == 2025])
    mv_ids = set(t["meta_valor_mensal"]["id_meta"].unique())
    sem = m[~m["id_meta_lancamentos"].isin(mv_ids)]
    return [check("Meta sem NENHUM lançamento mensal (zero linhas)", "atencao", sem,
                   "R8 cobre o efeito (sem nota, fora do score), mas aqui não há lançamento "
                   "algum, nem inválido — diferente do caso de lançamento nulo. Checado contra "
                   "o id_meta_lancamentos resolvido (R7), não o id_meta bruto")]


def c_denominador_zero(t):
    """ACHADO #3/#7 generalizado — risco de divisão por zero em R4, resolvido
    de forma genérica (qualquer meta nova com esse padrão já cai aqui, não
    só a 5094 que achamos manualmente). Resolve R7 antes de calcular, porque
    o denominador relevante é o da meta REFERENCIADA quando é Compartilhada."""
    m = resolver_meta(t["meta"][t["meta"]["id_ciclo"] == 2025])
    mv = t["meta_valor_mensal"].copy()
    mv["valido"] = (mv["nao_se_aplica"] == 0) & mv["previsto"].notna() & mv["realizado"].notna()
    mv_valido = mv[mv["valido"]]

    soma_zero, media_zero = [], []
    for _, meta_row in m.iterrows():
        linhas = mv_valido[mv_valido["id_meta"] == meta_row["id_meta_lancamentos"]]
        if linhas.empty:
            continue
        if meta_row["acumulacao_efetiva"] == "Soma":
            denom_col = "previsto" if meta_row["polaridade_efetiva"] == "Melhor para cima" else "realizado"
            denom = linhas[denom_col].sum()
            if denom == 0:
                soma_zero.append({"id_meta": meta_row["id_meta"], "nome_meta": meta_row["nome_meta"],
                                   "colaborador": meta_row["id_colaborador"],
                                   "polaridade": meta_row["polaridade_efetiva"],
                                   "denominador": denom_col, "soma": denom})
        else:  # Média
            denom_col = "previsto" if meta_row["polaridade_efetiva"] == "Melhor para cima" else "realizado"
            zeros = linhas[linhas[denom_col] == 0]
            for _, z in zeros.iterrows():
                media_zero.append({"id_meta": meta_row["id_meta"], "nome_meta": meta_row["nome_meta"],
                                    "colaborador": meta_row["id_colaborador"],
                                    "mes": z["mes"], "denominador_zero_em": denom_col})

    return [
        check("Meta com denominador=0 em Acumulação Soma (R4 — divisão por zero)", "critico",
              pd.DataFrame(soma_zero), "soma(previsto) ou soma(realizado)=0 dependendo da polaridade — "
              "atingimento indefinido, tratado como sem nota (extensão de R8, não regra literal)"),
        check("Mês com denominador=0 dentro de meta Acumulação Média", "critico",
              pd.DataFrame(media_zero), "um mês específico tem o lado-denominador zerado — "
              "atingimento daquele mês fica indefinido"),
    ]


def c_lancamento_mensal(t):
    mv = t["meta_valor_mensal"]
    out = []
    out.append(check("mes fora de 1-12", "critico", mv[~mv["mes"].between(1, 12)], ""))
    out.append(check("previsto negativo", "atencao", mv[mv["previsto"] < 0], ""))
    out.append(check("realizado negativo", "atencao", mv[mv["realizado"] < 0], ""))

    dup = mv[mv.duplicated(subset=["id_meta", "mes"], keep=False)]
    out.append(check("lançamento duplicado (id_meta, mes)", "info", dup,
                      "R2 resolve via data_lancamento mais recente — aqui é só a contagem bruta"))

    inv = mv[(mv["nao_se_aplica"] == 0) & (mv["previsto"].isna() | mv["realizado"].isna())]
    out.append(check("nao_se_aplica=0 mas previsto/realizado nulo", "atencao", inv,
                      "R3 já exclui do cálculo, mas documentar"))
    return out


def c_meses_pre_pos_vinculo(t):
    mv = t["meta_valor_mensal"].copy()
    # R2: aplica dedup ANTES de checar validade/data — mesma ordem de regras da SQL
    mv = mv.sort_values(["id_meta", "mes", "data_lancamento", "id_lancamento"],
                         ascending=[True, True, False, False])
    mv = mv.drop_duplicates(subset=["id_meta", "mes"], keep="first")

    mv = mv.merge(t["meta"][["id_meta", "id_ciclo", "id_colaborador"]], on="id_meta")
    mv = mv[mv["id_ciclo"] == 2025]
    mv = mv.merge(t["colaborador"][["id_colaborador", "data_admissao", "data_desligamento"]], on="id_colaborador")
    mv["elegivel"] = mv.apply(lambda r: elegivel(r["data_admissao"], r["data_desligamento"]), axis=1)
    mv["valido"] = (mv["nao_se_aplica"] == 0) & mv["previsto"].notna() & mv["realizado"].notna()
    # ... resto igual

    adm = mv["data_admissao"].dt.date if hasattr(mv["data_admissao"], "dt") else mv["data_admissao"]
    pre = mv[mv["elegivel"] & mv["valido"] &
             (((adm.apply(lambda d: d.year) == 2025) & (mv["mes"] < adm.apply(lambda d: d.month))) |
              (adm.apply(lambda d: d.year) > 2025))]

    desl = mv["data_desligamento"]
    tem_desl = desl.notna()
    # Convenção: mês considerado "pós-desligamento" se o PRIMEIRO DIA do mês
    # é posterior à data_desligamento (dá benefício da dúvida ao mês em que
    # o desligamento de fato ocorreu). Documentar essa convenção no README —
    # usar o ÚLTIMO dia do mês em vez do primeiro dá uma contagem diferente.
    mes_date = mv["mes"].apply(lambda m: datetime.date(2025, m, 1))
    pos_mask = tem_desl & mv["valido"] & (mes_date > desl.apply(lambda d: d.date() if pd.notna(d) and hasattr(d, "date") else d))

    pos_elegivel = mv[pos_mask & mv["elegivel"]]
    pos_inelegivel = mv[pos_mask & ~mv["elegivel"]]

    return [
        check("Lançamento válido ANTES da admissão (colaborador elegível)", "critico", pre,
              "mês de referência é anterior ao mês de admissão — afeta o score se não tratado"),
        check("Lançamento válido APÓS desligamento — colaborador ELEGÍVEL (R10)", "critico", pos_elegivel,
              "afeta diretamente P1/P2/P3 — decisão: manter literal no cálculo, documentar no README "
              "(ver análise de sensibilidade)"),
        check("Lançamento válido APÓS desligamento — colaborador NÃO elegível (R10)", "info", pos_inelegivel,
              "não afeta P1/P2/P3 (colaborador já sai por R10 de qualquer forma), mas é o mesmo "
              "padrão de dado — registrado por completude"),
    ]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------
def main():
    conn = pyodbc.connect(SQLSERVER_CONN_STR, autocommit=True)
    t = load_data(conn)
    conn.close()

    all_checks = []
    for fn in [c_pk_duplicada, c_fk_orfa, c_hierarquia_gestor, c_gestor_fora_hierarquia,
               c_espaco_em_branco, c_categorias, c_nome_duplicado_colaborador,
               c_peso, c_meta_compartilhada, c_compartilhada_lancamento_proprio,
               c_meta_sem_lancamento, c_denominador_zero, c_lancamento_mensal,
               c_meses_pre_pos_vinculo]:
        all_checks.extend(fn(t))

    sev_order = {"critico": 0, "atencao": 1, "info": 2}
    all_checks.sort(key=lambda c: (sev_order[c["severidade"]], -c["qtd"]))

    linhas_md = ["# Relatório de diagnóstico de qualidade — Case Mereo\n"]
    for c in all_checks:
        marca = {"critico": "🔴", "atencao": "🟡", "info": "⚪"}[c["severidade"]]
        print(f"{marca} [{c['severidade'].upper():8}] {c['nome']}: {c['qtd']} linha(s)")
        if c["qtd"] > 0:
            print(f"   {c['descricao']}")

        linhas_md.append(f"## {marca} {c['nome']} ({c['qtd']} linha(s))")
        linhas_md.append(f"{c['descricao']}\n")
        if c["qtd"] > 0:
            linhas_md.append(c["amostra"].to_markdown(index=False))
        linhas_md.append("")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(linhas_md), encoding="utf-8")
    print(f"\nRelatório salvo em: {REPORT_PATH}")


if __name__ == "__main__":
    main()