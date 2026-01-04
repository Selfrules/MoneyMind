"""
MoneyMind - Personal Finance Dashboard
======================================
Modern Minimal Dark Theme with Emerald Green accents
"""

import streamlit as st
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database import init_db, get_latest_balances, get_transactions, get_spending_by_category
from styles import get_custom_css, get_plotly_theme, COLORS, metric_card
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Page config
st.set_page_config(
    page_title="MoneyMind",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Initialize database
init_db()

# Plotly theme
plotly_theme = get_plotly_theme()

# Sidebar
with st.sidebar:
    st.markdown("""
    <div style="padding: 1rem 0;">
        <h1 style="font-size: 1.5rem; font-weight: 700; margin: 0; color: #FAFAFA;">
            💰 MoneyMind
        </h1>
        <p style="font-size: 0.75rem; color: #71717A; margin-top: 0.25rem;">
            Personal Finance Dashboard
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Navigation
    st.page_link("app.py", label="Overview", icon="📊")
    st.page_link("pages/1_📊_Transactions.py", label="Transazioni", icon="📋")
    st.page_link("pages/2_💰_Budget.py", label="Budget", icon="💰")
    st.page_link("pages/3_📥_Import.py", label="Import", icon="📥")
    st.page_link("pages/4_📈_Report.py", label="Report", icon="📈")

    st.markdown("---")

    # Quick stats in sidebar
    st.markdown("""
    <p style="font-size: 0.75rem; color: #71717A; text-transform: uppercase; letter-spacing: 0.05em;">
        Quick Stats
    </p>
    """, unsafe_allow_html=True)

    now = datetime.now()
    st.caption(f"📅 {now.strftime('%d %B %Y')}")

# Main content
st.markdown("""
<h1 style="font-size: 2rem; font-weight: 700; color: #FAFAFA; margin-bottom: 0.5rem;">
    Overview
</h1>
<p style="color: #71717A; margin-bottom: 2rem;">
    Il tuo riepilogo finanziario
</p>
""", unsafe_allow_html=True)

# Get data
balances_list = get_latest_balances()
current_month = datetime.now().strftime("%Y-%m")

# Convert balances list to dict by bank
balances = {b["bank"]: b for b in balances_list}

# Calculate totals
total_balance = sum(b.get("balance", 0) or 0 for b in balances.values())
revolut_balance = balances.get("revolut", {}).get("balance", 0) or 0
illimity_balance = balances.get("illimity", {}).get("balance", 0) or 0

# Balance cards
col1, col2, col3 = st.columns(3)

with col1:
    delta_type = "positive" if total_balance >= 0 else "negative"
    st.markdown(metric_card(
        label="Saldo Totale",
        value=f"€{total_balance:,.2f}",
        delta_type=delta_type
    ), unsafe_allow_html=True)

with col2:
    st.markdown(metric_card(
        label="Revolut",
        value=f"€{revolut_balance:,.2f}",
    ), unsafe_allow_html=True)

with col3:
    st.markdown(metric_card(
        label="Illimity",
        value=f"€{illimity_balance:,.2f}",
    ), unsafe_allow_html=True)

# Spacer
st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

# Get transactions for charts
transactions = get_transactions()

if transactions:
    df = pd.DataFrame(transactions)
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)

    # Last 6 months
    months = df["month"].unique()
    last_6_months = sorted(months)[-6:] if len(months) >= 6 else sorted(months)
    df_recent = df[df["month"].isin(last_6_months)]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <h3 style="font-size: 1rem; font-weight: 600; color: #FAFAFA; margin-bottom: 1rem;">
            📊 Entrate vs Uscite
        </h3>
        """, unsafe_allow_html=True)

        # Aggregate by month
        monthly = df_recent.groupby("month").agg(
            entrate=("amount", lambda x: x[x > 0].sum()),
            uscite=("amount", lambda x: abs(x[x < 0].sum()))
        ).reset_index()

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Entrate",
            x=monthly["month"],
            y=monthly["entrate"],
            marker_color=COLORS["success"],
            marker_line_width=0,
        ))
        fig.add_trace(go.Bar(
            name="Uscite",
            x=monthly["month"],
            y=monthly["uscite"],
            marker_color=COLORS["danger"],
            marker_line_width=0,
        ))

        fig.update_layout(
            barmode="group",
            paper_bgcolor=COLORS["bg_secondary"],
            plot_bgcolor=COLORS["bg_secondary"],
            font=dict(family="Inter", color=COLORS["text_secondary"]),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(0,0,0,0)",
                font=dict(color=COLORS["text_muted"])
            ),
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(
                gridcolor=COLORS["border"],
                tickfont=dict(color=COLORS["text_muted"]),
            ),
            yaxis=dict(
                gridcolor=COLORS["border"],
                tickfont=dict(color=COLORS["text_muted"]),
            ),
            bargap=0.3,
            bargroupgap=0.1,
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("""
        <h3 style="font-size: 1rem; font-weight: 600; color: #FAFAFA; margin-bottom: 1rem;">
            🍩 Spese per Categoria
        </h3>
        """, unsafe_allow_html=True)

        # Current month spending
        spending = get_spending_by_category(current_month)

        if spending:
            spending_df = pd.DataFrame(spending)
            spending_df = spending_df[spending_df["total_spent"] > 0]

            if not spending_df.empty:
                fig = go.Figure(data=[go.Pie(
                    labels=spending_df["category_name"],
                    values=spending_df["total_spent"],
                    hole=0.6,
                    marker=dict(
                        colors=[
                            COLORS["chart_green"],
                            COLORS["chart_blue"],
                            COLORS["chart_purple"],
                            COLORS["chart_orange"],
                            COLORS["chart_pink"],
                            COLORS["chart_cyan"],
                            COLORS["chart_yellow"],
                            COLORS["chart_red"],
                        ]
                    ),
                    textinfo="percent",
                    textposition="outside",
                    textfont=dict(color=COLORS["text_secondary"]),
                )])

                fig.update_layout(
                    paper_bgcolor=COLORS["bg_secondary"],
                    plot_bgcolor=COLORS["bg_secondary"],
                    font=dict(family="Inter", color=COLORS["text_secondary"]),
                    showlegend=True,
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.05,
                        bgcolor="rgba(0,0,0,0)",
                        font=dict(color=COLORS["text_muted"], size=11)
                    ),
                    margin=dict(l=20, r=100, t=20, b=20),
                    annotations=[dict(
                        text=f"€{spending_df['total_spent'].sum():,.0f}",
                        x=0.5, y=0.5,
                        font=dict(size=20, color=COLORS["text_primary"], family="Inter"),
                        showarrow=False
                    )]
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Nessuna spesa questo mese")
        else:
            st.info("Nessuna spesa questo mese")

    # Spacer
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    # Recent transactions
    st.markdown("""
    <h3 style="font-size: 1rem; font-weight: 600; color: #FAFAFA; margin-bottom: 1rem;">
        📝 Ultime Transazioni
    </h3>
    """, unsafe_allow_html=True)

    # Last 10 transactions
    recent_tx = df.nlargest(10, "date")[["date", "description", "amount", "bank", "category_name"]].copy()
    recent_tx["date"] = recent_tx["date"].dt.strftime("%d/%m")

    # Display as styled cards
    for _, row in recent_tx.iterrows():
        amount_color = COLORS["success"] if row["amount"] >= 0 else COLORS["danger"]
        amount_sign = "+" if row["amount"] >= 0 else ""

        st.markdown(f"""
        <div class="tx-row">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <span style="color: {COLORS['text_muted']}; font-size: 0.875rem; min-width: 40px;">
                    {row['date']}
                </span>
                <div>
                    <div style="color: {COLORS['text_primary']}; font-weight: 500;">
                        {row['description'][:40]}{'...' if len(str(row['description'])) > 40 else ''}
                    </div>
                    <div style="font-size: 0.75rem; color: {COLORS['text_muted']};">
                        {row['bank'].title()} • {row['category_name'] or 'Non categorizzato'}
                    </div>
                </div>
            </div>
            <span style="color: {amount_color}; font-weight: 600; font-size: 1rem;">
                {amount_sign}€{abs(row['amount']):,.2f}
            </span>
        </div>
        """, unsafe_allow_html=True)

else:
    # Empty state
    st.markdown(f"""
    <div style="
        background: {COLORS['bg_secondary']};
        border: 1px dashed {COLORS['border']};
        border-radius: 12px;
        padding: 3rem;
        text-align: center;
        margin: 2rem 0;
    ">
        <div style="font-size: 3rem; margin-bottom: 1rem;">📥</div>
        <h3 style="color: {COLORS['text_primary']}; margin-bottom: 0.5rem;">
            Nessuna transazione
        </h3>
        <p style="color: {COLORS['text_muted']}; margin-bottom: 1.5rem;">
            Importa i tuoi file bancari per iniziare
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("📥 Vai a Import", type="primary"):
        st.switch_page("pages/3_📥_Import.py")
