"""
Import Page - Upload and import bank files
Modern Minimal Dark Theme
"""

import streamlit as st
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database import insert_transactions, get_connection, get_category_by_name
from parsers.revolut import parse_revolut
from parsers.illimity import parse_illimity
from ai.categorizer import categorize_transactions
from styles import get_custom_css, COLORS
import pandas as pd

st.set_page_config(page_title="Import - MoneyMind", page_icon="📥", layout="wide")

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Header
st.markdown("""
<h1 style="font-size: 2rem; font-weight: 700; color: #FAFAFA; margin-bottom: 0.5rem;">
    Import
</h1>
<p style="color: #71717A; margin-bottom: 2rem;">
    Carica i file delle tue banche per importare le transazioni
</p>
""", unsafe_allow_html=True)

# Initialize session state
if "parsed_transactions" not in st.session_state:
    st.session_state.parsed_transactions = []

# File uploaders
col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    <div style="
        background: {COLORS['bg_secondary']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    ">
        <h3 style="color: {COLORS['text_primary']}; font-size: 1rem; margin-bottom: 0.5rem;">
            💳 Revolut
        </h3>
        <p style="color: {COLORS['text_muted']}; font-size: 0.875rem;">
            Carica il file .parquet o .csv esportato
        </p>
    </div>
    """, unsafe_allow_html=True)
    revolut_file = st.file_uploader(
        "Revolut",
        type=["parquet", "csv"],
        key="revolut"
    )

with col2:
    st.markdown(f"""
    <div style="
        background: {COLORS['bg_secondary']};
        border: 1px solid {COLORS['border']};
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    ">
        <h3 style="color: {COLORS['text_primary']}; font-size: 1rem; margin-bottom: 0.5rem;">
            🏦 Illimity
        </h3>
        <p style="color: {COLORS['text_muted']}; font-size: 0.875rem;">
            Carica il file .xlsx esportato
        </p>
    </div>
    """, unsafe_allow_html=True)
    illimity_file = st.file_uploader(
        "Illimity",
        type=["xlsx", "xls"],
        key="illimity"
    )

# Spacer
st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

# Parse button
if st.button("🔍 Analizza File"):
    all_transactions = []

    if revolut_file:
        with st.spinner("Parsing Revolut..."):
            try:
                revolut_txs = parse_revolut(revolut_file)
                all_transactions.extend(revolut_txs)
                st.success(f"✅ Revolut: {len(revolut_txs)} transazioni trovate")
            except Exception as e:
                st.error(f"❌ Errore Revolut: {e}")

    if illimity_file:
        with st.spinner("Parsing Illimity..."):
            try:
                illimity_txs = parse_illimity(illimity_file)
                all_transactions.extend(illimity_txs)
                st.success(f"✅ Illimity: {len(illimity_txs)} transazioni trovate")
            except Exception as e:
                st.error(f"❌ Errore Illimity: {e}")

    if all_transactions:
        # Check for duplicates
        conn = get_connection()
        existing_ids = set(row[0] for row in conn.execute("SELECT id FROM transactions").fetchall())
        conn.close()

        new_transactions = [t for t in all_transactions if t["id"] not in existing_ids]
        duplicate_count = len(all_transactions) - len(new_transactions)

        st.session_state.parsed_transactions = new_transactions

        st.info(f"📊 **{len(new_transactions)}** nuove transazioni da importare ({duplicate_count} duplicati esclusi)")

# Preview section
if st.session_state.parsed_transactions:
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    st.markdown("""
    <h3 style="font-size: 1rem; font-weight: 600; color: #FAFAFA; margin-bottom: 1rem;">
        📝 Anteprima
    </h3>
    """, unsafe_allow_html=True)

    df = pd.DataFrame(st.session_state.parsed_transactions)
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%d/%m/%Y")
    df["amount"] = df["amount"].apply(lambda x: f"€{x:+,.2f}")

    # Show first 10 as styled rows
    for _, row in df.head(10).iterrows():
        st.markdown(f"""
        <div class="tx-row">
            <div style="display: flex; align-items: center; gap: 1rem; flex: 1;">
                <span style="color: {COLORS['text_muted']}; font-size: 0.875rem; min-width: 80px;">
                    {row['date']}
                </span>
                <div style="flex: 1;">
                    <div style="color: {COLORS['text_primary']}; font-weight: 500;">
                        {str(row['description'])[:50]}
                    </div>
                    <span style="font-size: 0.75rem; color: {COLORS['text_muted']};">
                        {row['bank'].title()}
                    </span>
                </div>
            </div>
            <span style="color: {COLORS['text_secondary']}; font-weight: 600;">
                {row['amount']}
            </span>
        </div>
        """, unsafe_allow_html=True)

    if len(st.session_state.parsed_transactions) > 10:
        st.caption(f"... e altre {len(st.session_state.parsed_transactions) - 10} transazioni")

    # Spacer
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

    # Import button
    if st.button("🚀 Importa e Categorizza con AI"):
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Step 1: Categorize with AI
            status_text.markdown(f"""
            <p style="color: {COLORS['accent']};">
                🤖 Categorizzazione con Claude AI...
            </p>
            """, unsafe_allow_html=True)
            progress_bar.progress(10)

            categories_map = categorize_transactions(st.session_state.parsed_transactions)

            progress_bar.progress(50)
            status_text.markdown(f"""
            <p style="color: {COLORS['accent']};">
                💾 Salvataggio transazioni...
            </p>
            """, unsafe_allow_html=True)

            # Step 2: Update transactions with category IDs
            for tx in st.session_state.parsed_transactions:
                category_name = categories_map.get(tx["id"], "Altro")
                category = get_category_by_name(category_name)
                tx["category_id"] = category["id"] if category else None

            progress_bar.progress(70)

            # Step 3: Insert into database
            insert_transactions(st.session_state.parsed_transactions)

            progress_bar.progress(100)
            status_text.empty()

            st.success(f"🎉 **{len(st.session_state.parsed_transactions)}** transazioni importate e categorizzate!")

            # Clear session state
            st.session_state.parsed_transactions = []

        except Exception as e:
            st.error(f"❌ Errore durante l'import: {e}")
            progress_bar.progress(0)

# Help section
st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

st.markdown("""
<h3 style="font-size: 1rem; font-weight: 600; color: #FAFAFA; margin-bottom: 1rem;">
    ❓ Come esportare i file
</h3>
""", unsafe_allow_html=True)

with st.expander("💳 Revolut"):
    st.markdown("""
    1. Apri l'app Revolut o vai su revolut.com
    2. Vai su **Profilo** → **Estratti conto**
    3. Seleziona il periodo desiderato
    4. Esporta come **CSV** o **Parquet**
    5. Carica il file qui
    """)

with st.expander("🏦 Illimity"):
    st.markdown("""
    1. Accedi a illimity.com
    2. Vai su **Movimenti** → **Esporta**
    3. Seleziona il formato **Excel (.xlsx)**
    4. Scarica e carica il file qui
    """)
