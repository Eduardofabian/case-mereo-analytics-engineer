"""Matriz de sensibilidade pós-desligamento (4 definições). Uso: python etl/sensibilidade_matriz.py <raiz_do_projeto>
Depende de etl/verificacao_independente.py (mesma pasta)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np, pandas as pd
import verificacao_independente as V

def calc(modo=None, limite="inicio"):
    m = V.meta[V.meta.id_ciclo == 2025].copy()
    ref = V.meta.set_index("id_meta")[["polaridade", "tipo_acumulacao"]]
    m["id_lanc"] = np.where(m.tipo_meta == "Compartilhada", m.id_meta_referencia, m.id_meta).astype(int)
    m["pol"] = m.id_lanc.map(ref.polaridade); m["acum"] = m.id_lanc.map(ref.tipo_acumulacao); m["peso_ef"] = m.peso.abs()
    l = V.mvm.sort_values(["id_meta","mes","data_lancamento","id_lancamento"]).drop_duplicates(["id_meta","mes"], keep="last")
    l = l[(l.nao_se_aplica==0) & l.previsto.notna() & l.realizado.notna()]
    j = m.merge(l, left_on="id_lanc", right_on="id_meta", suffixes=("", "_l"))
    desl = V.colab.set_index("id_colaborador").data_desligamento
    owner = V.meta.set_index("id_meta").id_colaborador
    if modo:
        d = j.id_colaborador.map(desl) if modo=="holder" else j.id_lanc.map(owner).map(desl)
        r = pd.to_datetime(dict(year=2025, month=j.mes, day=1))
        if limite=="fim": r = r + pd.offsets.MonthEnd(0)
        j = j[~(d.notna() & (r > d))]
    with np.errstate(divide="ignore", invalid="ignore"):
        cima = j.realizado/j.previsto.replace(0,np.nan); baixo = j.previsto/j.realizado.replace(0,np.nan)
    j["am"] = np.where(j.pol=="Melhor para cima", cima, baixo)
    rows=[]
    for id_meta,g in j.groupby("id_meta"):
        mm=m[m.id_meta==id_meta].iloc[0]
        if mm.acum=="Soma":
            sp,sr=g.previsto.sum(),g.realizado.sum()
            at=(sr/sp if sp else np.nan) if mm.pol=="Melhor para cima" else (sp/sr if sr else np.nan)
        else: at=g.am.mean()
        rows.append((id_meta,mm.id_colaborador,mm.peso_ef,at))
    n=pd.DataFrame(rows,columns=["id_meta","id_colaborador","peso","ating"])
    n["nota"]=n.ating.map(lambda a: np.nan if pd.isna(a) else 0.0 if a<.8 else a*100 if a<=1.2 else 120.0)
    v=n.dropna(subset=["nota"])
    return v.assign(x=v.nota*v.peso).groupby("id_colaborador").apply(lambda d:d.x.sum()/d.peso.sum()).rename("score")

base = calc(None); el = V.elegiveis()
b2, b3 = V.p2(base), V.p3_tabela(base)
rank_base = V.p3(base)[["grupo","posicao","id_gestor"]]
print(f"{'definição':22s} {'colab':>5s} {'max|d| colab':>12s} {'max|d| area_dir':>15s} {'max|d| area_cons':>16s} {'max|d| gestor':>13s} {'top3/bot3 igual':>15s}")
for modo in ["owner","holder"]:
    for lim in ["inicio","fim"]:
        s = calc(modo, lim)
        d = (base - s)[lambda x: x.index.isin(el)].fillna(0)
        a = b2.merge(V.p2(s), on="id_area", suffixes=("_a","_s"))
        dd=(a.score_direto_a-a.score_direto_s).abs().max(); dc=(a.score_consolidado_a-a.score_consolidado_s).abs().max()
        g = b3.merge(V.p3_tabela(s), on="id_gestor", suffixes=("_a","_s"))
        dg=(g.score_medio_time_a-g.score_medio_time_s).abs().max()
        same = rank_base.equals(V.p3(s)[["grupo","posicao","id_gestor"]])
        tag = f"{modo}/{lim}" + (" <-README" if (modo,lim)==("owner","inicio") else "")
        print(f"{tag:22s} {(d.abs()>1e-9).sum():>5d} {d.abs().max():>12.2f} {dd:>15.3f} {dc:>16.3f} {dg:>13.3f} {str(same):>15s}")
print("\nGESTOR (9 oficiais), owner/inicio (a checagem pendente):")
s = calc("owner","inicio"); g = b3.merge(V.p3_tabela(s), on="id_gestor", suffixes=("_atual","_sem"))
g["dif"]=g.score_medio_time_atual-g.score_medio_time_sem
print(g.round(3).sort_values("id_gestor").to_string(index=False))
print("\nAREA owner/inicio:"); a=b2.merge(V.p2(s),on="id_area",suffixes=("_a","_s"))
a["dif_dir"]=a.score_direto_a-a.score_direto_s; a["dif_cons"]=a.score_consolidado_a-a.score_consolidado_s
print(a[["id_area","dif_dir","dif_cons"]].round(4).to_string(index=False))
