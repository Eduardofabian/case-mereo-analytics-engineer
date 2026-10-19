"""
Prototipo (Streamlit) - Case Mereo / Grupo Aurora
3 layouts do mesmo resultado, todos num canvas fixo 1280x720 sem rolagem
(painel de sala/TV), escolhidos pela barra lateral (ou ?opcao=final|a|b na URL):

- Final: replica do painel aprovado (painel_mereo_final.html) - layout,
  cores, tipografia e conteudo; ancora das outras duas.
- A: cards executivos (KPIs grandes, areas em barras, zona critica, gestores).
- B: narrativa compacta (as 6 secoes do memo numa grade 3x2, uma linha de
  leitura por secao).

Streamlit nao controla grid/flex por pixel, entao cada opcao e HTML/CSS bruto
via st.html, com o chrome do Streamlit (header, toolbar, padding) escondido.

Fonte: views oficiais do pipeline (vw_score_colaborador, vw_score_area,
vw_score_gestor) enriquecidas em runtime com as dimensoes (dim_colaborador,
dim_area) via merge do pandas -- nao ha CSV "_enriquecido" pre-gerado, pra
nao depender de um passo manual fora do run_pipeline.py. Nada e recalculado
- so leitura, merge e exibicao.

Rodar: streamlit run painel/streamlit/prototipo_streamlit.py
"""
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Protótipo — Resultados Ciclo 2025", layout="wide",
                   initial_sidebar_state="expanded")

DATA_DIR = Path(__file__).resolve().parent.parent / "dados"

NOTA_QUALIDADE = (
    "O menor score individual (18.17, Paula Cardoso) é de uma colaboradora "
    "desligada em 13/11/2025, ainda elegível por admissão anterior a 30/09/2025. "
    "Isso distorce a média do time dela: sem esse caso, o score médio do time "
    "sobe de 83.56 para 91.74. Tratado como achado de qualidade, não como "
    "avaliação de gestão."
)


@st.cache_data
def carregar():
    """Só lê, enriquece (merge com as dimensões) e agrega o que já foi
    apurado - não recalcula regra de negócio nenhuma."""
    dim_colaborador = pd.read_csv(DATA_DIR / "dim_colaborador.csv")
    dim_area = pd.read_csv(DATA_DIR / "dim_area.csv")

    # inner join: só colaboradores elegíveis (R10) entram em P1 — vw_score_colaborador
    # tem score de todo mundo (81), mas só 72 são elegíveis, igual a respostas/.
    p1 = pd.read_csv(DATA_DIR / "vw_score_colaborador.csv").merge(
        dim_colaborador[dim_colaborador["flag_elegivel_r10"] == 1][
            ["id_colaborador", "nome", "id_area", "id_gestor"]
        ],
        on="id_colaborador", how="inner",
    )
    p2 = pd.read_csv(DATA_DIR / "vw_score_area.csv").merge(
        dim_area[["id_area", "nome", "id_area_pai", "nivel"]],
        on="id_area", how="left",
    )
    p3 = pd.read_csv(DATA_DIR / "vw_score_gestor.csv").merge(
        dim_colaborador[["id_colaborador", "nome"]].rename(columns={"id_colaborador": "id_gestor"}),
        on="id_gestor", how="left",
    )
    n_total = len(dim_colaborador)

    n = len(p1)
    critico = p1[p1["score"] < 80].sort_values("score")
    intermediario = p1[(p1["score"] >= 80) & (p1["score"] < 100)]
    gestores = p3.sort_values("score_medio_time", ascending=False)
    top5 = p1.nlargest(5, "score").merge(
        p2[["id_area", "nome"]].rename(columns={"nome": "area"}), on="id_area", how="left")

    return dict(
        p2=p2, n_elegiveis=n, n_total=n_total,
        score_medio=p1["score"].mean(),
        score_mediano=p1["score"].median(),
        critico=critico,
        n_critico=len(critico), n_inter=len(intermediario),
        n_ok=n - len(critico) - len(intermediario),
        pct_critico=100 * len(critico) / n,
        pct_inter=100 * len(intermediario) / n,
        pct_ok=100 * (n - len(critico) - len(intermediario)) / n,
        pct_abaixo_100=100 * (len(critico) + len(intermediario)) / n,
        areas_arvore=arvore_areas(p2),
        areas_rank=p2.sort_values("score_consolidado", ascending=False),
        top3=gestores.head(3),
        bottom3=gestores.sort_values("score_medio_time").head(3),
        top5=top5,
    )


def arvore_areas(p2):
    """Linhas da hierarquia em ordem de leitura (Diretoria -> Gerência -> Coordenação).
    Irmãs com subordinadas vêm antes das folhas; dentro disso, maior consolidado primeiro
    (reproduz a ordem do painel aprovado)."""
    filhos = {pai: g for pai, g in p2.groupby(p2["id_area_pai"].fillna(0).astype(int))}
    tem_filho = set(filhos) - {0}
    linhas = []

    def visitar(pai):
        if pai not in filhos:
            return
        irmas = filhos[pai].assign(folha=lambda g: ~g["id_area"].isin(tem_filho))
        for _, r in irmas.sort_values(["folha", "score_consolidado"], ascending=[True, False]).iterrows():
            linhas.append(r)
            visitar(int(r["id_area"]))

    visitar(0)
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------
# Helpers de HTML
# ---------------------------------------------------------------------------
def faixa(score):
    """Mesmos cortes do painel: vermelho <80, laranja 80-100, verde >=100."""
    return "bad" if score < 80 else "mid" if score < 100 else "good"


def cor(score):
    f = faixa(score)
    return f"background:var(--{f}-soft); color:var(--{f});"


def topbar(titulo):
    return f"""
<div class="topbar">
  <div class="topbar-left">
    <div class="logo-dot">M</div>
    <div class="topbar-title">{titulo}</div>
    <div class="topbar-sub">· Mereo Metas</div>
  </div>
  <div class="topbar-right">Grupo Aurora &nbsp;·&nbsp; Ciclo 2025</div>
</div>"""


def barra_distribuicao(d):
    return f"""
<div class="dist-bar">
  <div class="dist-seg" style="width:{d['pct_critico']:.1f}%; background:var(--bad);">{d['pct_critico']:.1f}%</div>
  <div class="dist-seg" style="width:{d['pct_inter']:.1f}%; background:var(--mid);">{d['pct_inter']:.1f}%</div>
  <div class="dist-seg" style="width:{d['pct_ok']:.1f}%; background:var(--good);">{d['pct_ok']:.1f}%</div>
</div>"""


def legenda_distribuicao(d):
    return f"""
<div class="dist-legend">
  <span><span class="dot" style="background:var(--bad);"></span>Crítico &lt;80 ({d['n_critico']})</span>
  <span><span class="dot" style="background:var(--mid);"></span>80–100 ({d['n_inter']})</span>
  <span><span class="dot" style="background:var(--good);"></span>≥100 ({d['n_ok']})</span>
</div>"""


def lista_gestores(df, classe_badge=None):
    itens = ""
    for _, r in df.iterrows():
        estilo = cor(r["score_medio_time"]) if classe_badge is None else classe_badge
        itens += f"""
<div class="gestor-item">
  <span class="gestor-name">{r['nome']} <span class="gestor-n">(n={int(r['n_subordinados_diretos_elegiveis'])})</span></span>
  <span class="gestor-badge" style="{estilo}">{r['score_medio_time']:.2f}</span>
</div>"""
    return itens


VERDE = "background:var(--good-soft); color:var(--good);"
VERMELHO = "background:var(--bad-soft); color:var(--bad);"


# ---------------------------------------------------------------------------
# CSS: chrome do Streamlit + tokens/classes do painel_mereo_final.html
# ---------------------------------------------------------------------------
CSS = """
<style>
  /* --- sem chrome nem scroll do Streamlit; sidebar fixa, painel centralizado --- */
  html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    overflow: hidden !important;
  }
  [data-testid="stMain"] { background: #E9EAEF !important; }
  header[data-testid="stHeader"], [data-testid="stDecoration"], [data-testid="stStatusWidget"],
  [data-testid="stSidebarCollapseButton"], [data-testid="stExpandSidebarButton"],
  [data-testid="stSidebar"] [data-testid="stSidebarResizer"], #MainMenu, footer { display: none !important; }
  [data-testid="stMainBlockContainer"], .block-container {
    padding: 0 !important; max-width: none !important; margin: 0 !important;
    height: 100vh; display: flex !important; align-items: center; justify-content: center;
  }
  [data-testid="stMain"] [data-testid="stVerticalBlock"] { gap: 0 !important; width: auto !important; flex: 0 0 auto; }

  /* --- sidebar: menu de opções com hover --- */
  [data-testid="stSidebar"] { background: #FFFFFF !important; border-right: 1px solid #ECECF0; }
  /* sempre aberta, mesmo se o navegador lembrar "recolhida" (localStorage stSidebarCollapsed-) */
  [data-testid="stSidebar"], [data-testid="stSidebar"][aria-expanded="false"] {
    transform: none !important; width: 300px !important; min-width: 300px !important; max-width: 300px !important;
  }
  [data-testid="stSidebar"] [role="radiogroup"] { gap: 6px; }
  [data-testid="stSidebar"] [role="radiogroup"] label {
    width: 100%; padding: 10px 12px; border-radius: 10px; border: 1px solid #ECECF0;
    cursor: pointer; transition: background .15s, border-color .15s, transform .15s, box-shadow .15s;
  }
  [data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: #F1EBFD; border-color: #6227EA; transform: translateX(3px);
    box-shadow: 0 2px 6px rgba(98,39,234,.15);
  }
  [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
    background: #F1EBFD; border-color: #6227EA; color: #6227EA; font-weight: 600;
  }

  :root {
    --mereo-purple: #6227EA; --mereo-purple-soft: #F1EBFD;
    --mereo-orange: #FF5C39; --mereo-orange-soft: #FFE8E2;
    --ink: #1C1C1C; --ink-soft: #6B7280;
    --bg-page: #F7F7F9; --bg-card: #FFFFFF; --bg-dark: #212529;
    --border: #ECECF0;
    --good: #1F9254; --good-soft: #E6F6ED;
    --mid: #FF5C39;  --mid-soft: #FFE8E2;
    --bad: #E5484D;  --bad-soft: #FDEAEA;
    --radius-lg: 14px; --radius-md: 10px; --radius-pill: 999px;
  }
  .frame, .frame * { box-sizing: border-box; }
  .frame {
    box-shadow: 0 10px 30px rgba(16,24,40,.12);
    width: 1280px; height: 720px; overflow: hidden;
    display: flex; flex-direction: column; background: var(--bg-page); color: var(--ink);
    font-family: "Inter", "Manrope", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    -webkit-font-smoothing: antialiased; line-height: normal;
  }
  .frame p { margin: 0; }

  /* ---------- Topbar ---------- */
  .topbar { background: var(--bg-dark); color: #fff; padding: 11px 28px; display: flex;
            align-items: center; justify-content: space-between; flex: 0 0 auto; }
  .topbar-left { display: flex; align-items: center; gap: 10px; }
  .logo-dot { width: 24px; height: 24px; border-radius: 6px; background: var(--mereo-purple);
              display: flex; align-items: center; justify-content: center;
              font-weight: 800; font-size: 12px; color: #fff; flex: 0 0 auto; }
  .topbar-title { font-weight: 700; font-size: 13.5px; }
  .topbar-sub { font-weight: 400; font-size: 11.5px; color: #B9BBC2; margin-left: 4px; }
  .topbar-right { font-size: 12px; color: #B9BBC2; font-weight: 500; }

  .content { flex: 1 1 auto; min-height: 0; display: flex; flex-direction: column; padding: 16px 28px 16px; }

  /* ---------- KPI row ---------- */
  .kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 12px; flex: 0 0 auto; }
  .kpi-card { background: var(--bg-card); border: 1px solid var(--border);
              border-top: 3px solid var(--kpi-accent, var(--mereo-purple));
              border-radius: var(--radius-lg); padding: 13px 18px; box-shadow: 0 1px 2px rgba(16,24,40,0.04); }
  .kpi-label { font-size: 10.5px; color: var(--ink-soft); font-weight: 700;
               text-transform: uppercase; letter-spacing: .04em; margin-bottom: 6px !important; }
  .kpi-value { font-size: 23px; font-weight: 800; line-height: 1; margin-bottom: 4px !important; }
  .kpi-foot { font-size: 11px; color: var(--ink-soft); margin-bottom: 9px !important; }
  .kpi-pill { display: inline-block; font-size: 10.5px; font-weight: 700; padding: 2px 9px;
              border-radius: var(--radius-pill); margin-left: 5px; vertical-align: 2px; }
  .pill-bad { background: var(--bad-soft); color: var(--bad); }
  .pill-mid { background: var(--mid-soft); color: var(--mid); }
  .kpi-spark { height: 5px; border-radius: 3px; background: var(--kpi-accent, var(--mereo-purple)); opacity: .22; }
  .kpi-spark .fill { height: 100%; border-radius: 3px; background: var(--kpi-accent, var(--mereo-purple)); }

  /* ---------- Distribuição ---------- */
  .dist-panel { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg);
                padding: 11px 18px; box-shadow: 0 1px 2px rgba(16,24,40,0.04); margin-bottom: 12px;
                flex: 0 0 auto; display: flex; align-items: center; gap: 18px; }
  .dist-title { font-size: 11.5px; font-weight: 700; white-space: nowrap; flex: 0 0 auto; }
  .dist-bar { height: 24px; border-radius: 6px; display: flex; overflow: hidden; flex: 1 1 auto; }
  .dist-seg { display: flex; align-items: center; justify-content: center; color: #fff; font-size: 10.5px; font-weight: 700; }
  .dist-legend { display: flex; gap: 16px; font-size: 11px; color: var(--ink-soft); flex: 0 0 auto; white-space: nowrap; }
  .dist-legend span.dot { display: inline-block; width: 7px; height: 7px; border-radius: 50%; margin-right: 4px; }

  /* ---------- Painéis ---------- */
  .grid-2x2 { display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 14px; flex: 1 1 auto; min-height: 0; }
  .panel { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-lg);
           padding: 13px 18px; box-shadow: 0 1px 2px rgba(16,24,40,0.04);
           overflow: hidden; display: flex; flex-direction: column; min-height: 0; }
  .panel-title { font-size: 12.5px; font-weight: 700; margin: 0 0 2px 0 !important; }
  .panel-sub { font-size: 10px; color: var(--ink-soft); margin: 0 0 6px 0 !important; line-height: 1.25; }

  /* ---------- Área (nome | direto | consolidado) ---------- */
  .area-tree { flex: 1 1 auto; overflow: hidden; display: flex; flex-direction: column; }
  .area-head { display: grid; grid-template-columns: 1fr 70px 86px; gap: 6px; font-size: 8px; font-weight: 700;
               text-transform: uppercase; letter-spacing: .03em; color: var(--ink-soft);
               padding-bottom: 3px; border-bottom: 1px solid var(--border); margin-bottom: 2px !important; }
  .area-head .col-r { text-align: center; }
  .area-row { display: grid; grid-template-columns: 1fr 70px 86px; align-items: center; gap: 6px;
              padding: 0.5px 0; border-bottom: 1px solid var(--border); line-height: 1; }
  .area-row:last-child { border-bottom: none; }
  .area-name { font-size: 8.5px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .area-name.lvl1 { padding-left: 12px; }
  .area-name.lvl2 { padding-left: 24px; }
  .area-name.lvl1::before, .area-name.lvl2::before { content: "↳ "; color: var(--ink-soft); }
  .score-badge, .score-badge-single { min-width: 38px; text-align: center; font-size: 8.5px; font-weight: 800;
               padding: 0.5px 6px; border-radius: var(--radius-pill); justify-self: center; }
  .score-badge-single { grid-column: 2 / span 2; }

  /* ---------- Tabelas ---------- */
  .frame table { border: none !important; margin: 0 !important; }
  .frame th, .frame td { border: none; background: none; }
  .frame tr { background: none !important; }
  table.crit-table { width: 100%; border-collapse: collapse; font-size: 9.5px; flex: 1 1 auto; line-height: 1.1; }
  table.crit-table th { text-align: left; font-size: 8px; color: var(--ink-soft); text-transform: uppercase;
                        letter-spacing: .03em; font-weight: 700; padding: 0 0 3px 0; border-bottom: 1px solid var(--border); }
  table.crit-table td { padding: 0.8px 0; border-bottom: 1px solid var(--border); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  table.crit-table tr:last-child td { border-bottom: none; }
  .mini-badge { display: inline-block; font-size: 10px; font-weight: 800; padding: 1px 7px;
                border-radius: var(--radius-pill); background: var(--bad-soft); color: var(--bad); }

  /* ---------- Gestores ---------- */
  .gestor-cols { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; flex: 1 1 auto; min-height: 0; }
  .gestor-list-title { font-size: 9.5px; font-weight: 700; text-transform: uppercase; letter-spacing: .03em;
                       color: var(--ink-soft); margin: 0 0 6px 0 !important; }
  .gestor-item { display: flex; align-items: center; justify-content: space-between; padding: 5px 0;
                 border-bottom: 1px solid var(--border); font-size: 11px; }
  .gestor-item:last-child { border-bottom: none; }
  .gestor-name { font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .gestor-n { font-size: 10px; color: var(--ink-soft); margin-left: 4px; }
  .gestor-badge { min-width: 44px; text-align: center; font-size: 10.5px; font-weight: 800;
                  padding: 1.5px 8px; border-radius: var(--radius-pill); flex: 0 0 auto; }

  /* ---------- Top 5 ---------- */
  table.top5-table { width: 100%; border-collapse: collapse; font-size: 10px; flex: 1 1 auto; }
  table.top5-table td { padding: 2.8px 0; border-bottom: 1px solid var(--border); vertical-align: middle; }
  table.top5-table tr:last-child td { border-bottom: none; }
  .rank-badge { display: inline-flex; align-items: center; justify-content: center; width: 15px; height: 15px;
                border-radius: 50%; background: var(--mereo-purple-soft); color: var(--mereo-purple);
                font-size: 8.5px; font-weight: 800; margin-right: 7px; }
  .top5-nome { font-weight: 600; font-size: 10px; }
  .top5-area { font-size: 8.5px; color: var(--ink-soft); display: block; margin-left: 22px; line-height: 1.2; }
  .top5-score { font-size: 10.5px; font-weight: 800; color: var(--good); text-align: right; }

  /* ---------- Opção A: cards executivos ---------- */
  .a-kpi { background: var(--bg-card); border: 1px solid var(--border); border-left: 5px solid var(--kpi-accent, var(--mereo-purple));
           border-radius: var(--radius-lg); padding: 16px 20px; box-shadow: 0 1px 2px rgba(16,24,40,0.04); }
  .a-kpi .v { font-size: 32px; font-weight: 800; line-height: 1.05; }
  .a-kpi .l { font-size: 11.5px; color: var(--ink-soft); margin-top: 4px !important; }
  .a-main { display: grid; grid-template-columns: 3fr 2fr; gap: 14px; flex: 1 1 auto; min-height: 0; margin-bottom: 12px; }
  .a-bottom { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; flex: 0 0 auto; }
  .bars { flex: 1 1 auto; display: flex; flex-direction: column; justify-content: space-between; min-height: 0; }
  .bar-row { display: grid; grid-template-columns: 170px 1fr 46px; align-items: center; gap: 10px; font-size: 10.5px; }
  .bar-row .nm { font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .bar-row .track { display: flex; flex-direction: column; gap: 2px; }
  .bar-row .b { height: 7px; border-radius: 4px; }
  .bar-row .val { font-weight: 800; text-align: right; }
  .legend-inline { font-size: 10px; color: var(--ink-soft); }
  .legend-inline i { display: inline-block; width: 10px; height: 6px; border-radius: 3px; margin: 0 4px 0 10px; }
  .crit-list .row { display: flex; justify-content: space-between; align-items: center; padding: 5px 0;
                    border-bottom: 1px solid var(--border); font-size: 11.5px; }
  .crit-list .row:last-child { border-bottom: none; }
  .note { font-size: 10px; color: var(--ink-soft); margin-top: 10px !important; flex: 0 0 auto;
          white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

  /* ---------- Opção B: narrativa compacta ---------- */
  .b-grid { display: grid; grid-template-columns: repeat(3, 1fr); grid-template-rows: 1fr 1fr; gap: 14px; flex: 1 1 auto; min-height: 0; }
  .b-num { color: var(--mereo-purple); font-weight: 800; margin-right: 4px; }
  .b-big { display: flex; gap: 26px; margin: 10px 0 4px 0 !important; }
  .b-big .v { font-size: 38px; font-weight: 800; line-height: 1; }
  .b-big .l { font-size: 10.5px; color: var(--ink-soft); margin-top: 4px !important; }
  .leitura { font-size: 10.5px; color: var(--ink-soft); border-left: 3px solid var(--border);
             padding-left: 10px; margin-top: auto !important; line-height: 1.35; }
  .b-list .row { display: flex; justify-content: space-between; align-items: center; padding: 3px 0;
                 border-bottom: 1px solid var(--border); font-size: 10.5px; }
  .b-list .row:last-child { border-bottom: none; }
  .b-text { font-size: 11px; line-height: 1.5; color: var(--ink); }

  /* ---------- Hover no painel (cards sobem, linhas destacam) ---------- */
  .kpi-card, .a-kpi, .panel, .dist-panel, .dist-seg { transition: transform .15s, box-shadow .15s, filter .15s; }
  .kpi-card:hover, .a-kpi:hover, .panel:hover, .dist-panel:hover {
    transform: translateY(-2px); box-shadow: 0 6px 16px rgba(16,24,40,.10);
  }
  .dist-seg:hover { filter: brightness(1.12); }
  .area-row, .gestor-item, .crit-list .row, .b-list .row, .bar-row, table.crit-table td, table.top5-table td {
    transition: background .12s;
  }
  .area-row:hover, .gestor-item:hover, .crit-list .row:hover, .b-list .row:hover, .bar-row:hover,
  table.crit-table tr:hover td, table.top5-table tr:hover td { background: var(--mereo-purple-soft); }
</style>
"""


# ---------------------------------------------------------------------------
# FINAL - réplica do painel aprovado (painel_mereo_final.html)
# ---------------------------------------------------------------------------
def opcao_final(d):
    kpis = f"""
<div class="kpi-row">
  <div class="kpi-card" style="--kpi-accent: var(--mereo-purple);">
    <div class="kpi-label">Score médio do ciclo</div>
    <div class="kpi-value">{d['score_medio']:.2f}</div>
    <div class="kpi-foot">Mediana {d['score_mediano']:.2f}</div>
    <div class="kpi-spark"><div class="fill" style="width:{d['score_medio'] / 120 * 100:.0f}%;"></div></div>
  </div>
  <div class="kpi-card" style="--kpi-accent: #9CA3AF;">
    <div class="kpi-label">Elegíveis</div>
    <div class="kpi-value">{d['n_elegiveis']}</div>
    <div class="kpi-foot">de {d['n_total']} colaboradores</div>
    <div class="kpi-spark"><div class="fill" style="width:{100 * d['n_elegiveis'] / d['n_total']:.0f}%;"></div></div>
  </div>
  <div class="kpi-card" style="--kpi-accent: var(--bad);">
    <div class="kpi-label">Zona crítica (&lt;80)</div>
    <div class="kpi-value">{d['n_critico']} <span class="kpi-pill pill-bad">{d['pct_critico']:.1f}%</span></div>
    <div class="kpi-foot">ação individual imediata</div>
    <div class="kpi-spark"><div class="fill" style="width:{d['pct_critico']:.1f}%;"></div></div>
  </div>
  <div class="kpi-card" style="--kpi-accent: var(--mereo-orange);">
    <div class="kpi-label">Abaixo da meta (100)</div>
    <div class="kpi-value">{d['pct_abaixo_100']:.1f}% <span class="kpi-pill pill-mid">quase metade</span></div>
    <div class="kpi-foot">{d['n_critico']} críticos + {d['n_inter']} intermediários</div>
    <div class="kpi-spark"><div class="fill" style="width:{d['pct_abaixo_100']:.1f}%;"></div></div>
  </div>
</div>"""

    linhas_area = ""
    for _, r in d["areas_arvore"].iterrows():
        nivel = int(r["nivel"])
        classe = f"area-name lvl{nivel}" if nivel else "area-name"
        folha = r["id_area"] not in set(d["p2"]["id_area_pai"].dropna().astype(int))
        if folha:
            badges = f'<div class="score-badge-single" style="{cor(r["score_direto"])}">{r["score_direto"]:.2f}</div>'
        else:
            badges = (f'<div class="score-badge" style="{cor(r["score_direto"])}">{r["score_direto"]:.2f}</div>'
                      f'<div class="score-badge" style="{cor(r["score_consolidado"])}">{r["score_consolidado"]:.2f}</div>')
        linhas_area += f'<div class="area-row"><div class="{classe}">{r["nome"]}</div>{badges}</div>'

    linhas_crit = "".join(
        f'<tr><td>{r["nome"]}</td><td style="text-align:right;"><span class="mini-badge">{r["score"]:.2f}</span></td></tr>'
        for _, r in d["critico"].iterrows())

    linhas_top5 = "".join(
        f'<tr><td><span class="rank-badge">{i}</span><span class="top5-nome">{r["nome"]}</span>'
        f'<span class="top5-area">{r["area"]}</span></td><td class="top5-score">{r["score"]:.2f}</td></tr>'
        for i, (_, r) in enumerate(d["top5"].iterrows(), start=1))

    return f"""
<div class="frame">
{topbar("Painel de Performance")}
<div class="content">
{kpis}
<div class="dist-panel">
  <div class="dist-title">Distribuição de Score</div>
  {barra_distribuicao(d)}
  {legenda_distribuicao(d)}
</div>
<div class="grid-2x2">
  <div class="panel">
    <div class="panel-title">Score por Área — Direto vs. Consolidado</div>
    <div class="panel-sub">Áreas-folha têm valor único (Direto = Consolidado); as 5 áreas com subordinadas mostram os dois</div>
    <div class="area-tree">
      <div class="area-head"><div></div><div class="col-r">Direto</div><div class="col-r">Consolidado</div></div>
      {linhas_area}
    </div>
  </div>
  <div class="panel">
    <div class="panel-title">Zona Crítica</div>
    <div class="panel-sub">{d['n_critico']} colaboradores com score &lt; 80 — ação imediata, do menor para o maior</div>
    <table class="crit-table">
      <thead><tr><th>Colaborador</th><th style="text-align:right;">Score</th></tr></thead>
      <tbody>{linhas_crit}</tbody>
    </table>
  </div>
  <div class="panel">
    <div class="panel-title">Gestores — Melhores e Piores</div>
    <div class="panel-sub">n de subordinados elegíveis ao lado do score</div>
    <div class="gestor-cols">
      <div><div class="gestor-list-title">Top 3</div>{lista_gestores(d['top3'], VERDE)}</div>
      <div><div class="gestor-list-title">Bottom 3</div>{lista_gestores(d['bottom3'], VERMELHO)}</div>
    </div>
  </div>
  <div class="panel">
    <div class="panel-title">Top 5 Colaboradores</div>
    <div class="panel-sub">Maiores scores individuais do ciclo</div>
    <table class="top5-table"><tbody>{linhas_top5}</tbody></table>
  </div>
</div>
</div>
</div>"""


# ---------------------------------------------------------------------------
# A - Cards executivos: KPIs grandes, áreas em barras | zona crítica,
# gestores no rodapé, nota de qualidade numa linha.
# ---------------------------------------------------------------------------
def opcao_a(d):
    kpis = [
        ("var(--mereo-purple)", f"{d['score_medio']:.2f}", "Score médio do ciclo"),
        ("var(--mereo-purple)", f"{d['score_mediano']:.2f}", "Score mediano"),
        ("var(--bad)", f"{d['n_critico']} <span style='font-size:18px;color:var(--bad)'>({d['pct_critico']:.1f}%)</span>",
         "Zona crítica (&lt;80)"),
        ("var(--mereo-orange)", f"{d['pct_abaixo_100']:.1f}%", "Abaixo da meta (100)"),
    ]
    html_kpis = "".join(
        f'<div class="a-kpi" style="--kpi-accent:{c};"><div class="v">{v}</div><div class="l">{l}</div></div>'
        for c, v, l in kpis)

    barras = "".join(f"""
<div class="bar-row">
  <div class="nm">{r['nome']}</div>
  <div class="track">
    <div class="b" style="width:{r['score_direto'] / 120 * 100:.1f}%; background:var(--mereo-purple);"></div>
    <div class="b" style="width:{r['score_consolidado'] / 120 * 100:.1f}%; background:#B9A3F5;"></div>
  </div>
  <div class="val" style="color:var(--{faixa(r['score_consolidado'])});">{r['score_consolidado']:.2f}</div>
</div>""" for _, r in d["areas_rank"].iterrows())

    crit = "".join(
        f'<div class="row"><span>{r["nome"]}</span><span class="mini-badge">{r["score"]:.2f}</span></div>'
        for _, r in d["critico"].iterrows())

    return f"""
<div class="frame">
{topbar("Resultado do Ciclo 2025")}
<div class="content">
  <div class="kpi-row">{html_kpis}</div>
  <div class="a-main">
    <div class="panel">
      <div class="panel-title">Score por área — direto vs. consolidado
        <span class="legend-inline"><i style="background:var(--mereo-purple)"></i>direto<i style="background:#B9A3F5"></i>consolidado (valor à direita)</span></div>
      <div class="panel-sub">Escala 0–120 · ordenado pelo consolidado</div>
      <div class="bars">{barras}</div>
    </div>
    <div class="panel">
      <div class="panel-title">Zona crítica — ação imediata</div>
      <div class="panel-sub">{d['n_critico']} colaboradores com score &lt; 80, do menor para o maior</div>
      <div class="crit-list">{crit}</div>
    </div>
  </div>
  <div class="a-bottom">
    <div class="panel"><div class="gestor-list-title">Gestores — Top 3</div>{lista_gestores(d['top3'], VERDE)}</div>
    <div class="panel"><div class="gestor-list-title">Gestores — Bottom 3</div>{lista_gestores(d['bottom3'], VERMELHO)}</div>
  </div>
  <div class="note" title="{NOTA_QUALIDADE}"><b>Qualidade de dados:</b> {NOTA_QUALIDADE}</div>
</div>
</div>"""


# ---------------------------------------------------------------------------
# B - Narrativa compacta: as 6 seções do memo numa grade 3x2,
# cada uma com uma linha de leitura curta.
# ---------------------------------------------------------------------------
def opcao_b(d):
    def secao(num, titulo, corpo, leitura=""):
        rodape = f'<div class="leitura">{leitura}</div>' if leitura else ""
        return (f'<div class="panel"><div class="panel-title"><span class="b-num">{num}.</span>{titulo}</div>'
                f'{corpo}{rodape}</div>')

    s1 = secao(1, "Onde o ciclo fechou", f"""
<div class="b-big">
  <div><div class="v">{d['score_medio']:.2f}</div><div class="l">score médio</div></div>
  <div><div class="v">{d['score_mediano']:.2f}</div><div class="l">score mediano</div></div>
</div>
<div class="panel-sub">{d['n_elegiveis']} elegíveis de {d['n_total']} colaboradores</div>""",
               "Média abaixo de 100 no agregado: sinal de calibração de meta para o próximo ciclo.")

    s2 = secao(2, "Como o resultado se distribui", f"""
<div style="margin:14px 0 8px 0;">{barra_distribuicao(d)}</div>
{legenda_distribuicao(d)}""",
               f"{d['pct_abaixo_100']:.1f}% abaixo da meta. Críticos pedem ação individual; "
               "o restante abaixo de 100 pede revisão de calibração.")

    s3 = secao(3, "Quem está em zona crítica", '<div class="b-list" style="margin-top:6px;">' + "".join(
        f'<div class="row"><span>{r["nome"]}</span><span class="mini-badge">{r["score"]:.2f}</span></div>'
        for _, r in d["critico"].iterrows()) + "</div>")

    s4 = secao(4, "Score consolidado por área", '<div class="b-list" style="margin-top:6px;">' + "".join(
        f'<div class="row"><span>{r["nome"]}</span>'
        f'<span class="gestor-badge" style="{cor(r["score_consolidado"])}">{r["score_consolidado"]:.2f}</span></div>'
        for _, r in d["areas_rank"].iterrows()) + "</div>")

    s5 = secao(5, "Gestores — melhores e piores médias", f"""
<div class="gestor-list-title" style="margin-top:6px !important;">Top 3</div>{lista_gestores(d['top3'], VERDE)}
<div class="gestor-list-title" style="margin-top:8px !important;">Bottom 3</div>{lista_gestores(d['bottom3'], VERMELHO)}""",
               "n de subordinados vai junto do score: time de 3 não se compara direto com time de 12.")

    s6 = secao(6, "Achado de qualidade", f'<div class="b-text" style="margin-top:8px;">{NOTA_QUALIDADE}</div>')

    return f"""
<div class="frame">
{topbar("Resultado do Ciclo 2025 · leitura para a diretoria")}
<div class="content">
  <div class="b-grid">{s1}{s2}{s3}{s4}{s5}{s6}</div>
</div>
</div>"""


OPCOES = {
    "C - Painel Minimalista": opcao_final,
    "A — Cards executivos": opcao_a,
    "B — Narrativa compacta": opcao_b,
}
ATALHOS = dict(zip(["final", "a", "b"], OPCOES))  # ?opcao=final|a|b

padrao = ATALHOS.get(st.query_params.get("opcao", "final").lower(), next(iter(OPCOES)))
st.sidebar.markdown("### Painel · Ciclo 2025")
escolha = st.sidebar.radio("Escolha o layout", list(OPCOES), index=list(OPCOES).index(padrao))
st.sidebar.caption("Canvas fixo 1280×720, centralizado. Em telas menores ele é reduzido "
                   "proporcionalmente pra caber inteiro, sem rolagem.")

# Encaixa o canvas na área ao lado da sidebar: escala <= 1 (nunca amplia), recalcula no resize.
AJUSTE_JS = """
<script>
(() => {
  const fit = () => {
    const m = document.querySelector('[data-testid="stMain"]');
    const f = document.querySelector('.frame');
    if (!m || !f) return;
    f.style.zoom = Math.min(1, (m.clientWidth - 48) / 1280, (m.clientHeight - 48) / 720);
  };
  fit(); requestAnimationFrame(fit);
  // observa a área principal (muda com a janela e com a sidebar), não só o resize da janela
  if (!window.__fitMereo) {
    const m = document.querySelector('[data-testid="stMain"]');
    if (m) { window.__fitMereo = new ResizeObserver(() => requestAnimationFrame(fit)); window.__fitMereo.observe(m); }
  }
})();
</script>"""
st.html(CSS + OPCOES[escolha](carregar()) + AJUSTE_JS, unsafe_allow_javascript=True)
