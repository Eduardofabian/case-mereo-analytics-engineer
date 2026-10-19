"""
Prototipo rapido (Streamlit) - Case Mereo / Grupo Aurora
Objetivo: comparar 3 layouts do mesmo resultado antes de comprometer o
layout final. NAO e o entregavel final da Parte 3 - e descartavel.

3 opcoes de layout (A, B, C) num arquivo so, escolhidas pela barra lateral.

Fonte: p1/p2/p3_enriquecido.csv, derivados das views oficiais do pipeline
(dim_colaborador, dim_area, vw_score_colaborador/area/gestor) so com colunas
extras (nome, area, gestor) pra exibicao -- os numeros sao os mesmos dos
CSVs finais de respostas/ (p1_score_colaborador.csv etc.), reconciliados
contra eles.

Rodar: streamlit run painel/prototipo_streamlit.py
"""
from pathlib import Path

import pandas as pd
import streamlit as st

# set_page_config so pode ser chamado uma vez: "wide" serve as 3 opcoes
# (a B limita a largura por CSS).
st.set_page_config(page_title="Protótipo — Resultados Ciclo 2025", layout="wide")

DATA_DIR = Path(__file__).resolve().parent

# Paleta provisória (neutra, profissional)
COR_PRIMARIA = "#2E3192"
COR_PRIMARIA_CLARA = "#5B5FD6"
COR_ALERTA = "#D64550"
COR_ATENCAO = "#E6A23C"
COR_OK = "#2F9E5B"
COR_FUNDO_CARD = "#F7F7FB"
COR_TEXTO_SECUNDARIO = "#6B6F85"

NOTA_QUALIDADE = (
    "O menor score individual (18.17, Paula Cardoso) é de uma colaboradora "
    "desligada em 13/11/2025, ainda elegível por admissão anterior a 30/09/2025. "
    "Isso distorce a média do time dela: sem esse caso, o score médio do time "
    "sobe de 83.56 para 91.74. Tratado como achado de qualidade, não como "
    "avaliação de gestão."
)


@st.cache_data
def carregar():
    """Só lê e agrega o que já foi apurado - não recalcula regra de negócio."""
    p1 = pd.read_csv(DATA_DIR / "p1_enriquecido.csv")
    p2 = pd.read_csv(DATA_DIR / "p2_enriquecido.csv")
    p3 = pd.read_csv(DATA_DIR / "p3_enriquecido.csv")

    n_elegiveis = len(p1)
    critico = p1[p1["score"] < 80].sort_values("score")
    intermediario = p1[(p1["score"] >= 80) & (p1["score"] < 100)]
    gestores = p3.sort_values("score_medio_time", ascending=False)

    return dict(
        p1=p1, p2=p2, p3=p3,
        n_elegiveis=n_elegiveis,
        score_medio=p1["score"].mean(),
        score_mediano=p1["score"].median(),
        critico=critico,
        intermediario=intermediario,
        acima_meta=p1[p1["score"] >= 100],
        pct_critico=100 * len(critico) / n_elegiveis,
        pct_intermediario=100 * len(intermediario) / n_elegiveis,
        pct_abaixo_100=100 * (len(critico) + len(intermediario)) / n_elegiveis,
        areas=p2.sort_values("score_consolidado", ascending=False),
        top3=gestores.head(3),
        bottom3=gestores.sort_values("score_medio_time").head(3),
    )


def tabela_gestores(df, label_n="n"):
    return df[["nome", "score_medio_time", "n_subordinados_diretos_elegiveis"]].rename(
        columns={"nome": "Gestor", "score_medio_time": "Score médio",
                 "n_subordinados_diretos_elegiveis": label_n}
    )


# ---------------------------------------------------------------------------
# OPCAO A - Cards executivos
# KPIs no topo em card, corpo em duas colunas (área | zona crítica),
# rodapé com ranking de gestores e nota de qualidade.
# ---------------------------------------------------------------------------
def opcao_a(d):
    st.markdown(f"""
    <style>
    .block-container {{ padding-top: 2rem; max-width: 1200px; }}
    .kpi-card {{
        background: {COR_FUNDO_CARD}; border-radius: 12px; padding: 20px 22px;
        border-left: 5px solid {COR_PRIMARIA};
    }}
    .kpi-valor {{ font-size: 2.1rem; font-weight: 700; color: #1a1a2e; line-height: 1.1; }}
    .kpi-label {{ font-size: 0.85rem; color: {COR_TEXTO_SECUNDARIO}; margin-top: 4px; }}
    .kpi-card.alerta {{ border-left-color: {COR_ALERTA}; }}
    .kpi-card.ok {{ border-left-color: {COR_OK}; }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("### Resultado do Ciclo 2025 — Grupo Aurora")
    st.caption("Visão executiva · 72 colaboradores elegíveis de 81 (9 fora por R10)")

    kpis = [
        ("", f'{d["score_medio"]:.2f}', "Score médio do ciclo"),
        ("", f'{d["score_mediano"]:.2f}', "Score mediano"),
        ("alerta", f'{len(d["critico"])} ({d["pct_critico"]:.1f}%)', "Zona crítica (&lt;80)"),
        ("", f'{d["pct_abaixo_100"]:.1f}%', "Abaixo da meta (100)"),
    ]
    for col, (classe, valor, label) in zip(st.columns(4), kpis):
        col.markdown(f'<div class="kpi-card {classe}"><div class="kpi-valor">{valor}</div>'
                     f'<div class="kpi-label">{label}</div></div>', unsafe_allow_html=True)

    st.write("")
    col_esq, col_dir = st.columns([3, 2])
    with col_esq:
        st.markdown("##### Score por área — direto vs. consolidado")
        chart_df = d["areas"].set_index("nome")[["score_direto", "score_consolidado"]]
        st.bar_chart(chart_df, color=[COR_PRIMARIA, "#A9ABE8"], height=320)
    with col_dir:
        st.markdown("##### Zona crítica — ação imediata")
        st.dataframe(
            d["critico"][["nome", "score"]].rename(columns={"nome": "Colaborador", "score": "Score"}),
            hide_index=True, width="stretch", height=320,
        )

    st.write("")
    st.markdown("##### Gestores — melhores e piores médias de time")
    g1, g2 = st.columns(2)
    with g1:
        st.caption("Top 3")
        st.dataframe(tabela_gestores(d["top3"]), hide_index=True, width="stretch")
    with g2:
        st.caption("Bottom 3")
        st.dataframe(tabela_gestores(d["bottom3"]), hide_index=True, width="stretch")

    st.divider()
    with st.expander("Nota de qualidade de dados"):
        st.caption(NOTA_QUALIDADE)


# ---------------------------------------------------------------------------
# OPCAO B - Narrativa vertical (estilo relatório)
# Rolagem vertical, uma seção por vez, cada visual com uma linha de leitura.
# Pensada pra ser lida de cima pra baixo como um memo.
# ---------------------------------------------------------------------------
def opcao_b(d):
    st.markdown(f"""
    <style>
    .block-container {{ max-width: 760px; padding-top: 2.5rem; }}
    .leitura {{ font-size: 0.92rem; color: {COR_TEXTO_SECUNDARIO}; border-left: 3px solid #ddd; padding-left: 12px; margin: 6px 0 28px 0; }}
    .faixa-barra {{ height: 26px; border-radius: 6px; display: flex; overflow: hidden; margin-bottom: 6px; }}
    </style>
    """, unsafe_allow_html=True)

    def leitura(texto):
        st.markdown(f'<div class="leitura">{texto}</div>', unsafe_allow_html=True)

    st.markdown("## Resultado do Ciclo 2025")
    st.markdown("Grupo Aurora · leitura para a diretoria")
    st.write("")

    st.markdown("### 1. Onde o ciclo fechou")
    c1, c2 = st.columns(2)
    c1.metric("Score médio", f'{d["score_medio"]:.2f}')
    c2.metric("Score mediano", f'{d["score_mediano"]:.2f}')
    leitura("Média e mediana abaixo de 100 no agregado — não é só exceção individual, "
            "é sinal de calibração de meta para o próximo ciclo.")

    st.markdown("### 2. Como o resultado se distribui")
    pct_ok = 100 - d["pct_critico"] - d["pct_intermediario"]
    st.markdown(
        f'<div class="faixa-barra">'
        f'<div style="width:{d["pct_critico"]}%; background:{COR_ALERTA};"></div>'
        f'<div style="width:{d["pct_intermediario"]}%; background:{COR_ATENCAO};"></div>'
        f'<div style="width:{pct_ok}%; background:{COR_OK};"></div>'
        f'</div>', unsafe_allow_html=True)
    st.caption(
        f'🔴 Crítico &lt;80: {d["pct_critico"]:.1f}%  ·  🟠 80–100: {d["pct_intermediario"]:.1f}%  ·  🟢 ≥100: {pct_ok:.1f}%'
    )
    leitura(f'{d["pct_abaixo_100"]:.1f}% da base ficou abaixo da meta — quase metade. '
            f'São dois problemas diferentes: {len(d["critico"])} pessoas em zona crítica pedem ação individual; '
            f'o restante abaixo de 100 pede revisão de calibração, não plano de ação.')

    st.markdown("### 3. Quem está em zona crítica")
    st.dataframe(
        d["critico"][["nome", "score"]].rename(columns={"nome": "Colaborador", "score": "Score"}),
        hide_index=True, width="stretch",
    )
    leitura("Lista nominal — é a única ação imediata e individual deste painel.")

    st.markdown("### 4. Score por área")
    chart_df = d["areas"].set_index("nome")[["score_direto", "score_consolidado"]]
    st.bar_chart(chart_df, color=[COR_PRIMARIA, "#A9ABE8"], height=280)
    leitura("Consolidado abaixo de direto aponta problema que vem de baixo na hierarquia — "
            "muda quem a diretoria chama pra conversa.")

    st.markdown("### 5. Gestores — melhores e piores médias de time")
    st.markdown("**Top 3**")
    st.dataframe(tabela_gestores(d["top3"], "n subordinados"), hide_index=True, width="stretch")
    st.markdown("**Bottom 3**")
    st.dataframe(tabela_gestores(d["bottom3"], "n subordinados"), hide_index=True, width="stretch")
    leitura("O n de subordinados elegíveis vai junto do score de propósito: "
            "compara-se com cuidado um time de 3 pessoas contra um de 12.")

    st.markdown("### 6. Achado de qualidade")
    st.info(NOTA_QUALIDADE)


# ---------------------------------------------------------------------------
# OPCAO C - Grade densa (painel de sala / TV)
# Grade compacta, tudo numa tela sem rolagem, leitura rápida à distância.
# ---------------------------------------------------------------------------
def opcao_c(d):
    st.markdown(f"""
    <style>
    .block-container {{ padding-top: 1.2rem; padding-bottom: 1rem; max-width: 1400px; }}
    .cel {{
        background: {COR_FUNDO_CARD}; border-radius: 10px; padding: 14px 16px; height: 100%;
    }}
    .cel h5 {{ margin: 0 0 8px 0; font-size: 0.78rem; text-transform: uppercase; letter-spacing: .04em; color: {COR_TEXTO_SECUNDARIO}; }}
    .cel .big {{ font-size: 1.9rem; font-weight: 800; color: #1a1a2e; }}
    .cel .sub {{ font-size: 0.78rem; color: {COR_TEXTO_SECUNDARIO}; }}
    .badge {{ display:inline-block; padding: 2px 8px; border-radius: 999px; font-size: 0.72rem; font-weight: 700; color:#fff; }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("##### GRUPO AURORA · CICLO 2025 · PAINEL DE RESULTADOS")

    pct_ok = 100 - d["pct_critico"] - d["pct_intermediario"]
    celulas = [
        ("SCORE MÉDIO", f'{d["score_medio"]:.2f}', f'mediana {d["score_mediano"]:.2f}'),
        ("ELEGÍVEIS", f'{d["n_elegiveis"]}', "de 81 (9 fora por R10)"),
        ("ZONA CRÍTICA", f'{len(d["critico"])}', f'{d["pct_critico"]:.1f}% da base'),
        ("ABAIXO DA META", f'{d["pct_abaixo_100"]:.1f}%', f'{pct_ok:.1f}% bateu ≥100'),
    ]
    for col, (label, big, sub) in zip(st.columns(4), celulas):
        col.markdown(f'<div class="cel"><h5>{label}</h5><div class="big">{big}</div><div class="sub">{sub}</div></div>',
                     unsafe_allow_html=True)

    st.write("")
    row2 = st.columns([2, 2, 1.3])

    with row2[0]:
        st.markdown('<div class="cel"><h5>SCORE POR ÁREA (CONSOLIDADO)</h5></div>', unsafe_allow_html=True)
        st.bar_chart(d["areas"].set_index("nome")[["score_consolidado"]], color=COR_PRIMARIA, height=230)

    with row2[1]:
        st.markdown('<div class="cel"><h5>GESTORES — TOP 3 / BOTTOM 3</h5></div>', unsafe_allow_html=True)
        for col, titulo, df, cor in zip(st.columns(2), ["Top", "Bottom"],
                                        [d["top3"], d["bottom3"]], [COR_OK, COR_ALERTA]):
            with col:
                st.caption(titulo)
                for _, r in df.iterrows():
                    st.markdown(f'<span class="badge" style="background:{cor}">{r["score_medio_time"]:.1f}</span> '
                                f'{r["nome"]} <span class="sub" style="color:{COR_TEXTO_SECUNDARIO}">'
                                f'(n={int(r["n_subordinados_diretos_elegiveis"])})</span>',
                                unsafe_allow_html=True)

    with row2[2]:
        st.markdown('<div class="cel"><h5>ZONA CRÍTICA</h5></div>', unsafe_allow_html=True)
        for _, r in d["critico"].iterrows():
            st.markdown(f'<span class="sub">{r["nome"]}</span> — <b>{r["score"]:.1f}</b>', unsafe_allow_html=True)

    st.write("")
    st.markdown(f'<div class="cel"><h5>ACHADO DE QUALIDADE</h5><span class="sub">{NOTA_QUALIDADE}</span></div>',
                unsafe_allow_html=True)


OPCOES = {
    "A — Cards executivos": opcao_a,
    "B — Narrativa vertical": opcao_b,
    "C — Grade densa (TV)": opcao_c,
}

escolha = st.sidebar.radio("Layout", list(OPCOES))
st.sidebar.caption("Protótipo descartável — comparar layouts antes do painel final.")
OPCOES[escolha](carregar())
