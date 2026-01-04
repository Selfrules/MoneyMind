"""
Budget Page - Set and track monthly budgets
Modern Minimal Dark Theme
"""

import streamlit as st
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database import get_categories, get_budgets, set_budget, get_spending_by_category
from styles import get_custom_css, COLORS
from datetime import datetime

st.set_page_config(page_title="Budget - MoneyMind", page_icon="💰", layout="wide")

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Header
st.markdown("""
<h1 style="font-size: 2rem; font-weight: 700; color: #FAFAFA; margin-bottom: 0.5rem;">
    Budget
</h1>
<p style="color: #71717A; margin-bottom: 2rem;">
    Imposta e monitora i tuoi limiti di spesa mensili
</p>
""", unsafe_allow_html=True)

# Month selector
col1, col2 = st.columns([1, 3])
with col1:
    selected_month = st.text_input(
        "Mese (YYYY-MM)",
        value=datetime.now().strftime("%Y-%m")
    )

# Spacer
st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)

# Get data
categories = get_categories()
budgets = get_budgets(selected_month)
spending = get_spending_by_category(selected_month)

# Create lookup dicts
budget_lookup = {b["category_id"]: b["amount"] for b in budgets}
spending_lookup = {s["category_id"]: s["total_spent"] for s in spending if s["total_spent"] > 0}

# Summary cards
total_budgeted = sum(budget_lookup.values())
total_spent = sum(spending_lookup.values())
remaining = total_budgeted - total_spent

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Budget Totale</div>
        <div class="value">€{total_budgeted:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Speso</div>
        <div class="value negative">€{total_spent:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="label">Rimanente</div>
        <div class="value {'positive' if remaining >= 0 else 'negative'}">€{remaining:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

# Spacer
st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

# Budget status
st.markdown("""
<h3 style="font-size: 1rem; font-weight: 600; color: #FAFAFA; margin-bottom: 1rem;">
    📊 Stato Budget per Categoria
</h3>
""", unsafe_allow_html=True)

# Grid of budget cards
cols = st.columns(2)
col_idx = 0

for category in categories:
    if category["name"] in ["Stipendio", "Trasferimenti"]:
        continue

    cat_id = category["id"]
    budget_amount = budget_lookup.get(cat_id, 0)
    spent_amount = spending_lookup.get(cat_id, 0)

    # Calculate percentage
    if budget_amount > 0:
        percentage = min((spent_amount / budget_amount) * 100, 100)
        overflow = spent_amount > budget_amount
    else:
        percentage = 0
        overflow = False

    # Determine status
    if overflow or percentage >= 100:
        status_color = COLORS["danger"]
        status_text = "Superato"
    elif percentage >= 80:
        status_color = COLORS["warning"]
        status_text = "Attenzione"
    else:
        status_color = COLORS["success"]
        status_text = "OK"

    with cols[col_idx % 2]:
        st.markdown(f"""
        <div class="budget-item">
            <div class="header">
                <span style="font-weight: 600; color: {COLORS['text_primary']};">
                    {category['icon']} {category['name']}
                </span>
                <span style="font-size: 0.75rem; color: {status_color}; font-weight: 500;">
                    {status_text}
                </span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill {'danger' if overflow or percentage >= 100 else 'warning' if percentage >= 80 else 'ok'}"
                     style="width: {percentage}%;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 0.5rem; font-size: 0.875rem;">
                <span style="color: {COLORS['text_secondary']};">
                    €{spent_amount:,.2f} spesi
                </span>
                <span style="color: {COLORS['text_muted']};">
                    / €{budget_amount:,.2f}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    col_idx += 1

# Spacer
st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

# Set budget section
st.markdown("""
<h3 style="font-size: 1rem; font-weight: 600; color: #FAFAFA; margin-bottom: 1rem;">
    ⚙️ Imposta Budget
</h3>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    budget_categories = [c for c in categories if c["name"] not in ["Stipendio", "Trasferimenti"]]
    selected_cat = st.selectbox(
        "Categoria",
        budget_categories,
        format_func=lambda x: f"{x['icon']} {x['name']}"
    )

with col2:
    current_budget = budget_lookup.get(selected_cat["id"], 0) if selected_cat else 0
    budget_value = st.number_input(
        "Limite mensile (€)",
        min_value=0.0,
        step=50.0,
        value=float(current_budget)
    )

with col3:
    st.markdown("<div style='height: 1.75rem;'></div>", unsafe_allow_html=True)
    if st.button("💾 Salva Budget", type="primary", use_container_width=True):
        set_budget(selected_cat["id"], budget_value, selected_month)
        st.success(f"✅ Budget impostato: {selected_cat['name']} → €{budget_value:,.2f}")
        st.rerun()
