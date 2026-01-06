"""
Transactions Page - View and manage all transactions
Modern Minimal Dark Theme
"""

import streamlit as st
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database import get_transactions, get_categories, update_transaction_category
from styles import get_custom_css, COLORS
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Transazioni - MoneyMind", page_icon="📋", layout="wide")

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Header
st.markdown("""
<h1 style="font-size: 2rem; font-weight: 700; color: #FAFAFA; margin-bottom: 0.5rem;">
    Transazioni
</h1>
<p style="color: #71717A; margin-bottom: 2rem;">
    Visualizza e gestisci tutte le tue transazioni
</p>
""", unsafe_allow_html=True)

# Filters section
st.markdown("""
<h3 style="font-size: 1rem; font-weight: 600; color: #FAFAFA; margin-bottom: 1rem;">
    🔍 Filtri
</h3>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    date_from = st.date_input(
        "Da",
        value=(datetime.now() - timedelta(days=30)).date()
    )

with col2:
    date_to = st.date_input(
        "A",
        value=datetime.now().date()
    )

with col3:
    categories = get_categories()
    category_options = ["Tutte"] + [c["name"] for c in categories]
    selected_category = st.selectbox("Categoria", category_options)

with col4:
    bank_options = ["Tutte", "revolut", "illimity"]
    selected_bank = st.selectbox("Banca", bank_options)

# Build filters
filters = {
    "start_date": date_from.isoformat(),
    "end_date": date_to.isoformat()
}

if selected_category != "Tutte":
    cat = next((c for c in categories if c["name"] == selected_category), None)
    if cat:
        filters["category_id"] = cat["id"]

if selected_bank != "Tutte":
    filters["bank"] = selected_bank

# Spacer
st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

# Get transactions
transactions = get_transactions(filters)

if transactions:
    df = pd.DataFrame(transactions)

    # Summary cards
    col1, col2, col3 = st.columns(3)

    total_in = df[df["amount"] > 0]["amount"].sum()
    total_out = abs(df[df["amount"] < 0]["amount"].sum())
    balance = total_in - total_out

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">Entrate</div>
            <div class="value positive">+€{total_in:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">Uscite</div>
            <div class="value negative">-€{total_out:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">Bilancio</div>
            <div class="value {'positive' if balance >= 0 else 'negative'}">
                {'+'if balance >= 0 else ''}€{balance:,.2f}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Spacer
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Transaction list
    st.markdown("""
    <h3 style="font-size: 1rem; font-weight: 600; color: #FAFAFA; margin-bottom: 1rem;">
        📝 Lista Transazioni
    </h3>
    """, unsafe_allow_html=True)

    # Format for display
    df["date"] = pd.to_datetime(df["date"])

    # Display transactions
    for _, row in df.iterrows():
        amount_color = COLORS["success"] if row["amount"] >= 0 else COLORS["danger"]
        amount_sign = "+" if row["amount"] >= 0 else ""
        date_str = row["date"].strftime("%d/%m/%Y")
        category = row["category_name"] or "Non categorizzato"

        st.markdown(f"""
        <div class="tx-row">
            <div style="display: flex; align-items: center; gap: 1rem; flex: 1;">
                <span style="color: {COLORS['text_muted']}; font-size: 0.875rem; min-width: 80px;">
                    {date_str}
                </span>
                <div style="flex: 1;">
                    <div style="color: {COLORS['text_primary']}; font-weight: 500;">
                        {str(row['description'])[:50]}{'...' if len(str(row['description'])) > 50 else ''}
                    </div>
                    <div style="display: flex; gap: 0.5rem; margin-top: 0.25rem;">
                        <span class="category-badge">{category}</span>
                        <span style="font-size: 0.75rem; color: {COLORS['text_muted']};">
                            {row['bank'].title()}
                        </span>
                    </div>
                </div>
            </div>
            <span style="color: {amount_color}; font-weight: 600; font-size: 1rem;">
                {amount_sign}€{abs(row['amount']):,.2f}
            </span>
        </div>
        """, unsafe_allow_html=True)

    # Spacer
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    # Edit category section
    st.markdown("""
    <h3 style="font-size: 1rem; font-weight: 600; color: #FAFAFA; margin-bottom: 1rem;">
        ✏️ Modifica Categoria
    </h3>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        tx_options = [
            f"{row['date'].strftime('%d/%m')} - {str(row['description'])[:30]}..."
            for _, row in df.iterrows()
        ]
        if tx_options:
            selected_tx_idx = st.selectbox(
                "Seleziona transazione",
                range(len(tx_options)),
                format_func=lambda x: tx_options[x]
            )

    with col2:
        new_category = st.selectbox(
            "Nuova categoria",
            [c["name"] for c in categories],
            key="new_cat"
        )

    with col3:
        st.markdown("<div style='height: 1.75rem;'></div>", unsafe_allow_html=True)
        if st.button("Aggiorna"):
            tx_id = df.iloc[selected_tx_idx]["id"]
            cat = next((c for c in categories if c["name"] == new_category), None)
            if cat:
                update_transaction_category(tx_id, cat["id"])
                st.success(f"✅ Categoria aggiornata a {new_category}")
                st.rerun()

    # Spacer
    st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

    # Export section
    st.markdown("""
    <h3 style="font-size: 1rem; font-weight: 600; color: #FAFAFA; margin-bottom: 1rem;">
        📥 Esporta
    </h3>
    """, unsafe_allow_html=True)

    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Scarica CSV",
        data=csv,
        file_name=f"transactions_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

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
        <div style="font-size: 2rem; margin-bottom: 1rem;">🔍</div>
        <p style="color: {COLORS['text_muted']};">
            Nessuna transazione trovata con i filtri selezionati
        </p>
    </div>
    """, unsafe_allow_html=True)
