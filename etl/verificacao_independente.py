"""
Verificação independente de P1/P2/P3.

Reimplementa R1-R11 do enunciado em pandas, direto do SQLite original
(material_original/dados/case_metas.db), SEM usar nenhuma view/SQL do projeto.
Depois compara com respostas/*.csv e roda a sensibilidade (pós-desligamento)
nos três níveis, usando os filtros oficiais de P3.

Uso: python etl/verificacao_independente.py [raiz_do_projeto]  (sem argumento, usa a raiz do repo)
"""
import sqlite3
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent  # raiz do projeto
DB = ROOT / "material_original" / "dados" / "case_metas.db"
RESP = ROOT / "respostas"

con = sqlite3.connect(DB)
area = pd.read_sql("select * from area", con)
colab = pd.read_sql("select * from colaborador", con, parse_dates=["data_admissao", "data_desligamento"])
meta = pd.read_sql("select * from meta", con)
mvm = pd.read_sql("select * from meta_valor_mensal", con, parse_dates=["data_lancamento"])


def calcular(excluir_pos_desligamento: bool = False):
    # R1 — só metas do ciclo 2025
    m = meta[meta.id_ciclo == 2025].copy()

    # R7 — meta compartilhada herda lançamentos/polaridade/acumulação da referência
    ref = meta.set_index("id_meta")[["polaridade", "tipo_acumulacao"]]
    m["id_lanc"] = np.where(m.tipo_meta == "Compartilhada", m.id_meta_referencia, m.id_meta).astype(int)
    m["pol"] = m.id_lanc.map(ref.polaridade)
    m["acum"] = m.id_lanc.map(ref.tipo_acumulacao)
    m["peso_ef"] = m.peso.abs()  # decisão documentada: peso negativo -> ABS

    # R2 — duplicata (id_meta, mes): vale o data_lancamento mais recente
    l = mvm.sort_values(["id_meta", "mes", "data_lancamento", "id_lancamento"])
    l = l.drop_duplicates(["id_meta", "mes"], keep="last")

    # R3 — mês conta: nao_se_aplica = 0 e previsto/realizado preenchidos
    l = l[(l.nao_se_aplica == 0) & l.previsto.notna() & l.realizado.notna()]

    j = m.merge(l, left_on="id_lanc", right_on="id_meta", suffixes=("", "_l"))
    j = j.merge(colab[["id_colaborador", "data_desligamento"]], on="id_colaborador", how="left")

    if excluir_pos_desligamento:
        inicio_mes = pd.to_datetime(dict(year=2025, month=j.mes, day=1))
        pos = j.data_desligamento.notna() & (inicio_mes > j.data_desligamento)
        j = j[~pos]

    # R5 — razão mensal conforme polaridade (denominador 0 -> NaN)
    with np.errstate(divide="ignore", invalid="ignore"):
        cima = j.realizado / j.previsto.replace(0, np.nan)
        baixo = j.previsto / j.realizado.replace(0, np.nan)
    j["ating_mes"] = np.where(j.pol == "Melhor para cima", cima, baixo)

    rows = []
    for id_meta, g in j.groupby("id_meta"):
        mm = m[m.id_meta == id_meta].iloc[0]
        if mm.acum == "Soma":
            sp, sr = g.previsto.sum(), g.realizado.sum()
            if mm.pol == "Melhor para cima":
                at = sr / sp if sp != 0 else np.nan
            else:
                at = sp / sr if sr != 0 else np.nan
        else:  # Média dos atingimentos mensais
            at = g.ating_mes.mean()  # NaN ignorados
        rows.append((id_meta, mm.id_colaborador, mm.peso_ef, at))
    n = pd.DataFrame(rows, columns=["id_meta", "id_colaborador", "peso", "ating"])

    # R6 — nota
    def nota(a):
        if pd.isna(a):
            return np.nan
        if a < 0.8:
            return 0.0
        if a <= 1.2:
            return a * 100
        return 120.0

    n["nota"] = n.ating.map(nota)

    # R8/R9 — só metas com nota; score = sum(nota*peso)/sum(peso)
    v = n.dropna(subset=["nota"])
    score = (
        v.assign(np_=v.nota * v.peso).groupby("id_colaborador").apply(lambda d: d.np_.sum() / d.peso.sum())
    ).rename("score")
    return score


def elegiveis():
    ok = (colab.data_admissao <= "2025-09-30") & ~(colab.data_desligamento < "2025-07-01")
    return set(colab.loc[ok, "id_colaborador"])


def p1(score):
    el = elegiveis()
    s = score[score.index.isin(el)]
    return s.round(2).rename("score").reset_index().sort_values("id_colaborador").reset_index(drop=True)


def descendentes():
    filhos = area.groupby("id_area_pai").id_area.apply(list).to_dict()
    out = {}
    for a in area.id_area:
        stack, acc = [a], []
        while stack:
            x = stack.pop()
            acc.append(x)
            stack.extend(filhos.get(x, []))
        out[a] = acc
    return out


def p2(score):
    el = elegiveis()
    c = colab[colab.id_colaborador.isin(el)].merge(score.reset_index(), on="id_colaborador")
    desc = descendentes()
    rows = []
    for a in area.id_area:
        d = c[c.id_area == a].score
        cons = c[c.id_area.isin(desc[a])].score
        rows.append((a, d.mean(), cons.mean()))
    return pd.DataFrame(rows, columns=["id_area", "score_direto", "score_consolidado"])


def gestores_validos_base():
    """Gestores ativos em 31/12/2025 (sem desligamento, ou desligados depois)."""
    ativo = colab.data_desligamento.isna() | (colab.data_desligamento > "2025-12-31")
    return set(colab.loc[ativo, "id_colaborador"])


def p3_tabela(score):
    el = elegiveis()
    ativos = gestores_validos_base()
    sub = colab[colab.id_colaborador.isin(el)].merge(score.reset_index(), on="id_colaborador")
    g = sub.groupby("id_gestor").score.agg(["mean", "count"]).reset_index()
    g = g[g.id_gestor.isin(ativos) & (g["count"] >= 3)]
    return g.rename(columns={"id_gestor": "id_gestor", "mean": "score_medio_time", "count": "n_sub"})


def p3(score):
    g = p3_tabela(score).sort_values("score_medio_time", ascending=False)
    top = g.head(3).assign(grupo="top", posicao=[1, 2, 3])
    bot = g.sort_values("score_medio_time").head(3).assign(grupo="bottom", posicao=[1, 2, 3])
    out = pd.concat([top, bot])
    out["score_medio_time"] = out.score_medio_time.round(2)
    return out[["grupo", "posicao", "id_gestor", "score_medio_time"]].reset_index(drop=True)


def cmp(nome, mine, theirs, keys, cols, tol=0.005):
    t = theirs.copy()
    m = mine.copy()
    mg = m.merge(t, on=keys, how="outer", suffixes=("_py", "_csv"), indicator=True)
    solo = mg[mg._merge != "both"]
    ok = True
    print(f"[{nome}] linhas py={len(m)} csv={len(t)}  só-em-um-lado={len(solo)}")
    if len(solo):
        ok = False
        print(solo.to_string())
    both = mg[mg._merge == "both"]
    for c in cols:
        diff = (both[f"{c}_py"].astype(float) - both[f"{c}_csv"].astype(float)).abs()
        bad = both[diff > tol]
        print(f"   {c}: máx |diff| = {diff.max():.4f}  divergentes(>{tol}) = {len(bad)}")
        if len(bad):
            ok = False
            print(bad.to_string())
    print(f"[{nome}] => {'OK, idêntico' if ok else 'DIVERGE'}\n")
    return ok


if __name__ == "__main__":
    lit = calcular(False)
    exc = calcular(True)

    r1 = pd.read_csv(RESP / "p1_score_colaborador.csv")
    r2 = pd.read_csv(RESP / "p2_score_area.csv")
    r3 = pd.read_csv(RESP / "p3_gestores.csv")

    a = cmp("P1", p1(lit), r1, ["id_colaborador"], ["score"])
    p2m = p2(lit).round(2)
    b = cmp("P2", p2m, r2, ["id_area"], ["score_direto", "score_consolidado"])
    c = cmp("P3", p3(lit), r3, ["grupo", "posicao"], ["id_gestor", "score_medio_time"])

    print("=== universo de P3 (gestores válidos) ===")
    print(p3_tabela(lit).sort_values("score_medio_time").round(2).to_string(index=False))
    print(f"n gestores válidos = {len(p3_tabela(lit))}\n")

    print("=== SENSIBILIDADE pós-desligamento (início do mês) ===")
    el = elegiveis()
    d = pd.concat([lit.rename("atual"), exc.rename("sem_pos")], axis=1)
    d = d[d.index.isin(el)]
    d["dif"] = d.atual - d.sem_pos
    chg = d[d.dif.abs() > 1e-9].round(2)
    print("colaboradores que mudam:\n", chg.to_string(), "\n")
    print("colaboradores sem score no cenário exclusão:", sorted(set(d.index[d.sem_pos.isna()])), "\n")

    A, B = p2(lit), p2(exc)
    s = A.merge(B, on="id_area", suffixes=("_atual", "_sem"))
    for k in ["score_direto", "score_consolidado"]:
        s[f"dif_{k}"] = (s[f"{k}_atual"] - s[f"{k}_sem"]).round(4)
    print("ÁREA (diferenças):\n", s[["id_area", "dif_score_direto", "dif_score_consolidado"]].to_string(index=False), "\n")

    G1, G2 = p3_tabela(lit), p3_tabela(exc)
    g = G1.merge(G2, on="id_gestor", how="outer", suffixes=("_atual", "_sem"))
    g["dif"] = (g.score_medio_time_atual - g.score_medio_time_sem).round(4)
    print("GESTOR (só os válidos de P3; diferenças):\n",
          g[["id_gestor", "n_sub_atual", "score_medio_time_atual", "score_medio_time_sem", "dif"]]
          .round(2).sort_values("id_gestor").to_string(index=False))
    # ranking muda?
    r_a = p3(lit)[["grupo", "posicao", "id_gestor"]]
    r_b = p3(exc)[["grupo", "posicao", "id_gestor"]]
    print("\ntop3/bottom3 de P3 idênticos no cenário exclusão?", r_a.equals(r_b))
    print("\nRESULTADO GERAL:", "TUDO CONFERE" if (a and b and c) else "HÁ DIVERGÊNCIA")
