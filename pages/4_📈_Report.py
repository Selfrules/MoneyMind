"""
Report Page - Monthly AI-generated financial report
Modern Minimal Dark Theme
"""

import streamlit as st
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database import get_transactions, get_budgets, get_spending_by_category
from ai.reporter import generate_monthly_report
from styles import get_custom_css, COLORS
from datetime import datetime
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Report - MoneyMind", page_icon="📈", layout="wide")

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Header
st.markdown("""
<h1 style="font-size: 2rem; font-weight: 700; color: #FAFAFA; margin-bottom: 0.5rem;">
    Report Mensile
</h1>
<p style="color: #71717A; margin-bottom: 2rem;">
    Analisi dettagliata e insights AI delle tue finanze
</p>
""", unsafe_allow_html=True)

# Month selector
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    selected_year = st.selectbox(
        "Anno",
        options=list(range(datetime.now().year, 2020, -1)),
        index=0
    )

with col2:
    months_it = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
                 "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
    selected_month_idx = st.selectbox(
        "Mese",
        options=list(range(1, 13)),
        index=datetime.now().month - 1,
        format_func=lambda x: months_it[x-1]
    )

month_str = f"{selected_year}-{selected_month_idx:02d}"

# Spacer
st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

# Get data
filters = {"month": month_str}
transactions = get_transactions(filters)
budgets = get_budgets(month_str)
spending = get_spending_by_category(month_str)

if transactions:
    df = pd.DataFrame(transactions)
    df["date"] = pd.to_datetime(df["date"])

    # Summary metrics
    total_income = df[df["amount"] > 0]["amount"].sum()
    total_expenses = abs(df[df["amount"] < 0]["amount"].sum())
    savings = total_income - total_expenses
    savings_rate = (savings / total_income * 100) if total_income > 0 else 0

    # Summary cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">Entrate</div>
            <div class="value positive">€{total_income:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">Uscite</div>
            <div class="value negative">€{total_expenses:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">Risparmio</div>
            <div class="value {'positive' if savings >= 0 else 'negative'}">€{savings:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">Tasso Risparmio</div>
            <div class="value">{savings_rate:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    # Spacer
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    # Charts row
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <h3 style="font-size: 1rem; font-weight: 600; color: #FAFAFA; margin-bottom: 1rem;">
            🍩 Spese per Categoria
        </h3>
        """, unsafe_allow_html=True)

        if spending:
            spending_df = pd.DataFrame(spending)
            spending_df = spending_df[spending_df["total_spent"] > 0]
            spending_df = spending_df.sort_values("total_spent", ascending=False)

            if not spending_df.empty:
                fig = go.Figure(data=[go.Pie(
                    labels=spending_df["category_name"],
                    values=spending_df["total_spent"],
                    hole=0.6,
                    marker=dict(colors=[
                        COLORS["chart_green"], COLORS["chart_blue"],
                        COLORS["chart_purple"], COLORS["chart_orange"],
                        COLORS["chart_pink"], COLORS["chart_cyan"],
                    ]),
                    textinfo="percent",
                    textfont=dict(color=COLORS["text_secondary"]),
                )])

                fig.update_layout(
                    paper_bgcolor=COLORS["bg_secondary"],
                    font=dict(family="Inter", color=COLORS["text_secondary"]),
                    showlegend=True,
                    legend=dict(font=dict(color=COLORS["text_muted"], size=10)),
                    margin=dict(l=20, r=20, t=20, b=20),
                    annotations=[dict(
                        text=f"€{spending_df['total_spent'].sum():,.0f}",
                        x=0.5, y=0.5,
                        font=dict(size=18, color=COLORS["text_primary"]),
                        showarrow=False
                    )]
                )
                st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("""
        <h3 style="font-size: 1rem; font-weight: 600; color: #FAFAFA; margin-bottom: 1rem;">
            📅 Andamento Giornaliero
        </h3>
        """, unsafe_allow_html=True)

        daily = df.groupby(df["date"].dt.day).agg(
            spese=("amount", lambda x: abs(x[x < 0].sum()))
        ).reset_index()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily["date"],
            y=daily["spese"],
            mode="lines+markers",
            line=dict(color=COLORS["accent"], width=2),
            fill="tozeroy",
            fillcolor=f"{COLORS['accent']}20",
            marker=dict(size=6, color=COLORS["accent"])
        ))

        fig.update_layout(
            paper_bgcolor=COLORS["bg_secondary"],
            plot_bgcolor=COLORS["bg_secondary"],
            font=dict(family="Inter", color=COLORS["text_secondary"]),
            xaxis=dict(
                title="Giorno",
                gridcolor=COLORS["border"],
                tickfont=dict(color=COLORS["text_muted"])
            ),
            yaxis=dict(
                title="Spese (€)",
                gridcolor=COLORS["border"],
                tickfont=dict(color=COLORS["text_muted"])
            ),
            margin=dict(l=40, r=20, t=20, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Spacer
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    # Top expenses
    st.markdown("""
    <h3 style="font-size: 1rem; font-weight: 600; color: #FAFAFA; margin-bottom: 1rem;">
        💸 Top 5 Spese
    </h3>
    """, unsafe_allow_html=True)

    top_expenses = df[df["amount"] < 0].nsmallest(5, "amount")

    for _, row in top_expenses.iterrows():
        st.markdown(f"""
        <div class="tx-row">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <span style="color: {COLORS['text_muted']};">
                    {row['date'].strftime('%d/%m')}
                </span>
                <span style="color: {COLORS['text_primary']}; font-weight: 500;">
                    {str(row['description'])[:40]}
                </span>
            </div>
            <span style="color: {COLORS['danger']}; font-weight: 600;">
                €{abs(row['amount']):,.2f}
            </span>
        </div>
        """, unsafe_allow_html=True)

    # Spacer
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    # AI Report section
    st.markdown("""
    <h3 style="font-size: 1rem; font-weight: 600; color: #FAFAFA; margin-bottom: 1rem;">
        🤖 Analisi AI
    </h3>
    """, unsafe_allow_html=True)

    if st.button("✨ Genera Report con Claude", type="primary"):
        with st.spinner("🤖 Claude sta analizzando le tue finanze..."):
            try:
                report = generate_monthly_report(
                    transactions=transactions,
                    budgets=budgets,
                    spending_by_category={s["category_name"]: s["total_spent"] for s in spending}
                )

                st.session_state.last_report = report

            except Exception as e:
                st.error(f"Errore nella generazione del report: {e}")

    # Display report if available
    if "last_report" in st.session_state and st.session_state.last_report:
        st.markdown(f"""
        <div class="ai-card">
            <div class="icon">✨</div>
            <div class="title">Insights di Claude</div>
            <div class="content">
                {st.session_state.last_report.replace(chr(10), '<br>')}
            </div>
        </div>
        """, unsafe_allow_html=True)

else:
    st.markdown(f"""
    <div style="
        background: {COLORS['bg_secondary']};
        border: 1px dashed {COLORS['border']};
        border-radius: 12px;
        padding: 3rem;
        text-align: center;
        margin: 2rem 0;
    ">
        <div style="font-size: 2rem; margin-bottom: 1rem;">📊</div>
        <p style="color: {COLORS['text_muted']};">
            Nessuna transazione trovata per {months_it[selected_month_idx-1]} {selected_year}
        </p>
    </div>
    """, unsafe_allow_html=True)
