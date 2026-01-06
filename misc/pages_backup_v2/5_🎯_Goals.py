"""
Goals & Debt Tracker v2.0 - Calm Finance Theme
Focus on debt freedom journey with clear priorities
"""

import streamlit as st
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database import (
    get_debts, add_debt, update_debt, delete_debt, get_total_debt,
    get_goals, add_goal, update_goal, delete_goal,
    get_user_profile, init_db
)
from analytics import compare_payoff_strategies, calculate_net_worth
from styles import (
    get_custom_css, COLORS, section_header, debt_card, goal_card
)
from datetime import datetime

# Ensure database is initialized
init_db()

st.set_page_config(page_title="Obiettivi - MoneyMind", page_icon="🎯", layout="wide")

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Initialize session state
if "show_add_debt" not in st.session_state:
    st.session_state.show_add_debt = False
if "show_add_goal" not in st.session_state:
    st.session_state.show_add_goal = False

# =============================================================================
# DATA
# =============================================================================
debts = get_debts(active_only=True)
goals = get_goals(status="active")
total_debt = get_total_debt()
profile = get_user_profile()

# Calculate total original debt for progress
total_original = sum(d.get("original_amount", d["current_balance"]) for d in debts) if debts else 0
total_paid = total_original - total_debt if total_original > 0 else 0
debt_progress = (total_paid / total_original * 100) if total_original > 0 else 0

# Get payoff strategy
if debts:
    strategy = compare_payoff_strategies(extra_payment=0)
    months_to_freedom = strategy['avalanche']['total_months']
    total_interest = strategy['avalanche']['total_interest']

    # Calculate estimated completion date
    from datetime import timedelta
    completion_date = datetime.now() + timedelta(days=int(months_to_freedom * 30.44))
    completion_str = completion_date.strftime("%B %Y")
else:
    months_to_freedom = 0
    total_interest = 0
    completion_str = "Ora! 🎉"

# =============================================================================
# PAGE HEADER
# =============================================================================
st.markdown(f"""
<div style="margin-bottom: 2rem;">
    <h1 style="font-size: 1.75rem; font-weight: 700; color: {COLORS['text_primary']}; margin-bottom: 0.25rem;">
        I Tuoi Obiettivi
    </h1>
    <p style="color: {COLORS['text_muted']}; margin: 0;">
        Il tuo percorso verso la libertà finanziaria
    </p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# HERO CARD - DEBT FREEDOM PROGRESS
# =============================================================================
if debts:
    status_text = "In corso"
    status_color = COLORS["warning"]
else:
    status_text = "Completato! 🎉"
    status_color = COLORS["income"]

# Build hero card HTML
debt_color = COLORS['expense'] if total_debt > 0 else COLORS['income']
hero_html = f'''<div style="background: linear-gradient(135deg, {COLORS['bg_secondary']} 0%, {COLORS['bg_tertiary']} 100%); border: 1px solid {COLORS['border']}; border-radius: 16px; padding: 1.5rem; margin-bottom: 2rem;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
<div style="display: flex; align-items: center; gap: 0.75rem;">
<span style="font-size: 2rem;">🏆</span>
<span style="font-size: 1.25rem; font-weight: 700; color: {COLORS['text_primary']};">LIBERTÀ DAL DEBITO</span>
</div>
<span style="font-size: 0.875rem; color: {status_color}; background: {status_color}15; padding: 0.25rem 0.75rem; border-radius: 999px; font-weight: 500;">{status_text}</span>
</div>
<div style="margin-bottom: 1rem;">
<div style="font-size: 0.875rem; color: {COLORS['text_muted']};">Debito Totale</div>
<div style="font-size: 2rem; font-weight: 700; color: {debt_color};">€{total_debt:,.0f}</div>
</div>
<div style="background: {COLORS['debt_track']}; border-radius: 999px; height: 12px; margin-bottom: 0.75rem; overflow: hidden;">
<div style="background: linear-gradient(90deg, {COLORS['accent']} 0%, {COLORS['income']} 100%); height: 100%; width: {min(debt_progress, 100)}%; border-radius: 999px;"></div>
</div>
<div style="display: flex; justify-content: space-between; color: {COLORS['text_muted']}; font-size: 0.875rem;">
<span>{debt_progress:.0f}% ripagato</span>
<span>Stima completamento: {completion_str} ({months_to_freedom:.0f} mesi)</span>
</div>
</div>'''
st.markdown(hero_html, unsafe_allow_html=True)

# =============================================================================
# DEBTS SECTION (Avalanche Strategy)
# =============================================================================
st.markdown(section_header("Debiti (Strategia Avalanche)", "+ Aggiungi" if not st.session_state.show_add_debt else "Chiudi"), unsafe_allow_html=True)

# Toggle add form
col_toggle, _ = st.columns([1, 5])
with col_toggle:
    if st.button("➕ Nuovo Debito" if not st.session_state.show_add_debt else "✕ Chiudi"):
        st.session_state.show_add_debt = not st.session_state.show_add_debt
        st.experimental_rerun()

# Add Debt Form
if st.session_state.show_add_debt:
    st.markdown(f"""
    <div style="background: {COLORS['bg_secondary']}; border: 1px solid {COLORS['border']};
                border-radius: 12px; padding: 1.25rem; margin: 1rem 0;">
    """, unsafe_allow_html=True)

    with st.form("add_debt_form"):
        col1, col2 = st.columns(2)

        with col1:
            debt_name = st.text_input("Nome", placeholder="es. Prestito Auto")
            original_amount = st.number_input("Importo Originale (€)", min_value=0.0, step=100.0)
            interest_rate = st.number_input("Tasso Interesse Annuo (%)", min_value=0.0, max_value=100.0, step=0.1)

        with col2:
            current_balance = st.number_input("Saldo Attuale (€)", min_value=0.0, step=100.0)
            monthly_payment = st.number_input("Rata Mensile (€)", min_value=0.0, step=10.0)

        if st.form_submit_button("Salva Debito"):
            if debt_name and current_balance > 0:
                add_debt({
                    "name": debt_name,
                    "type": "personal_loan",
                    "original_amount": original_amount or current_balance,
                    "current_balance": current_balance,
                    "interest_rate": interest_rate if interest_rate > 0 else None,
                    "monthly_payment": monthly_payment if monthly_payment > 0 else None,
                    "payment_day": 15
                })
                st.success(f"Debito '{debt_name}' aggiunto!")
                st.session_state.show_add_debt = False
                st.experimental_rerun()
            else:
                st.error("Inserisci nome e saldo attuale")

    st.markdown("</div>", unsafe_allow_html=True)

# Debt List - Sorted by interest rate (Avalanche order)
if debts:
    # Sort by interest rate descending
    sorted_debts = sorted(debts, key=lambda d: d.get("interest_rate", 0) or 0, reverse=True)

    st.markdown(f'<div style="background: {COLORS["bg_secondary"]}; border: 1px solid {COLORS["border"]}; border-radius: 12px; overflow: hidden;">', unsafe_allow_html=True)

    for i, debt in enumerate(sorted_debts):
        original = debt.get("original_amount", debt["current_balance"])
        is_priority = (i == 0)  # First one (highest rate) is priority

        # Calculate months left
        monthly = debt.get("monthly_payment", 0) or 0
        months_left = int(debt["current_balance"] / monthly) if monthly > 0 else 0

        st.markdown(debt_card(
            name=debt["name"],
            balance=debt["current_balance"],
            original=original,
            rate=debt.get("interest_rate", 0) or 0,
            monthly=monthly,
            months_left=months_left,
            priority=is_priority
        ), unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Interest Savings Tip
    if strategy.get('avalanche_interest_saved', 0) > 0:
        st.markdown(f"""
        <div style="
            background: {COLORS['accent_muted']};
            border-left: 4px solid {COLORS['accent']};
            border-radius: 0 8px 8px 0;
            padding: 1rem;
            margin-top: 1rem;
        ">
            <div style="display: flex; gap: 0.75rem; align-items: center;">
                <span style="font-size: 1.25rem;">💡</span>
                <div>
                    <div style="color: {COLORS['text_primary']}; font-weight: 600;">Strategia Avalanche</div>
                    <div style="color: {COLORS['text_secondary']}; font-size: 0.875rem;">
                        Pagando prima il debito con tasso più alto, risparmierai
                        <strong>€{strategy['avalanche_interest_saved']:,.0f}</strong> in interessi
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

else:
    st.markdown(f"""
    <div style="
        background: {COLORS['bg_secondary']};
        border: 1px dashed {COLORS['border']};
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
    ">
        <div style="font-size: 2.5rem; margin-bottom: 0.75rem;">🎉</div>
        <h3 style="color: {COLORS['text_primary']}; margin-bottom: 0.5rem;">Nessun Debito!</h3>
        <p style="color: {COLORS['text_muted']};">Sei libero dal debito. Complimenti!</p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# GOALS SECTION
# =============================================================================
st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)
st.markdown(section_header("Prossimi Obiettivi"), unsafe_allow_html=True)

# Toggle add goal form
col_toggle2, _ = st.columns([1, 5])
with col_toggle2:
    if st.button("➕ Nuovo Obiettivo" if not st.session_state.show_add_goal else "✕ Chiudi"):
        st.session_state.show_add_goal = not st.session_state.show_add_goal
        st.experimental_rerun()

# Add Goal Form
if st.session_state.show_add_goal:
    st.markdown(f"""
    <div style="background: {COLORS['bg_secondary']}; border: 1px solid {COLORS['border']};
                border-radius: 12px; padding: 1.25rem; margin: 1rem 0;">
    """, unsafe_allow_html=True)

    with st.form("add_goal_form"):
        col1, col2 = st.columns(2)

        with col1:
            goal_name = st.text_input("Nome Obiettivo", placeholder="es. Fondo Emergenza")
            goal_type = st.selectbox("Tipo", [
                "emergency_fund", "savings", "investment", "purchase", "other"
            ], format_func=lambda x: {
                "emergency_fund": "🛡️ Fondo Emergenza",
                "savings": "💰 Risparmio",
                "investment": "📈 Investimento",
                "purchase": "🛒 Acquisto",
                "other": "📦 Altro"
            }.get(x, x))

        with col2:
            target_amount = st.number_input("Obiettivo (€)", min_value=0.0, step=100.0)
            current_amount = st.number_input("Già Risparmiato (€)", min_value=0.0, step=50.0, value=0.0)

        if st.form_submit_button("Salva Obiettivo"):
            if goal_name and target_amount > 0:
                add_goal({
                    "name": goal_name,
                    "type": goal_type,
                    "target_amount": target_amount,
                    "current_amount": current_amount,
                    "priority": 2
                })
                st.success(f"Obiettivo '{goal_name}' creato!")
                st.session_state.show_add_goal = False
                st.experimental_rerun()
            else:
                st.error("Inserisci nome e importo obiettivo")

    st.markdown("</div>", unsafe_allow_html=True)

# Calculate monthly income for emergency fund target
monthly_income = 0
if profile:
    monthly_income = profile.get("monthly_net_income", 0) or 0
emergency_target = monthly_income * 3 if monthly_income > 0 else 6000

# Display existing goals
if goals:
    for goal in goals:
        type_icons = {
            "emergency_fund": "🛡️",
            "savings": "💰",
            "investment": "📈",
            "purchase": "🛒",
            "other": "🎯"
        }
        icon = type_icons.get(goal.get("type", "other"), "🎯")

        current = goal.get("current_amount", 0)
        target = goal.get("target_amount", 0)
        progress = (current / target * 100) if target > 0 else 0

        # Determine status
        if progress >= 100:
            status = "completed"
        elif progress > 0:
            status = "in_progress"
        else:
            status = "pending"

        # Check if blocked (debt not yet paid)
        if total_debt > 0 and goal.get("type") == "investment" and current == 0:
            status = "blocked"

        st.markdown(goal_card(
            name=goal["name"],
            current=current,
            target=target,
            icon=icon,
            status=status
        ), unsafe_allow_html=True)

        # Quick add buttons for in-progress goals
        if status in ["pending", "in_progress"]:
            col1, col2, col3 = st.columns([1, 1, 4])
            with col1:
                if st.button(f"+€50", key=f"add50_{goal['id']}"):
                    update_goal(goal['id'], {"current_amount": current + 50})
                    st.experimental_rerun()
            with col2:
                if st.button(f"+€100", key=f"add100_{goal['id']}"):
                    update_goal(goal['id'], {"current_amount": current + 100})
                    st.experimental_rerun()

# Suggested Goals (if none exist)
if not goals:
    st.markdown(f"""
    <div style="color: {COLORS['text_muted']}; font-size: 0.875rem; margin-bottom: 1rem;">
        Obiettivi suggeriti per te:
    </div>
    """, unsafe_allow_html=True)

    suggested_goals = [
        ("🛡️ Fondo Emergenza 3 Mesi", "emergency_fund", emergency_target,
         "Copri 3 mesi di spese per imprevisti"),
        ("🔥 FIRE", "investment", 450000,
         "Indipendenza finanziaria (25x spese annuali)")
    ]

    for name, gtype, target, desc in suggested_goals:
        # Check if blocked
        is_blocked = (gtype == "investment" and total_debt > 0)

        st.markdown(f"""
        <div style="
            background: {COLORS['bg_secondary']};
            border: 1px solid {COLORS['border']};
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 0.75rem;
            opacity: {0.6 if is_blocked else 1};
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="color: {COLORS['text_primary']}; font-weight: 600;">{name}</div>
                    <div style="color: {COLORS['text_muted']}; font-size: 0.75rem;">{desc}</div>
                </div>
                <div style="text-align: right;">
                    <div style="color: {COLORS['text_secondary']}; font-size: 0.875rem;">€0 / €{target:,.0f}</div>
                    {'<div style="color: ' + COLORS["text_muted"] + '; font-size: 0.75rem;">🔒 Prima estingui i debiti</div>' if is_blocked else ''}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if not is_blocked:
            if st.button("Inizia", key=f"start_{name}"):
                add_goal({
                    "name": name,
                    "type": gtype,
                    "target_amount": target,
                    "current_amount": 0,
                    "priority": 1 if gtype == "emergency_fund" else 3
                })
                st.experimental_rerun()

# =============================================================================
# FOOTER TIP
# =============================================================================
st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

if debts and not goals:
    st.markdown(f"""
    <div style="
        background: {COLORS['bg_tertiary']};
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    ">
        <span style="color: {COLORS['text_muted']}; font-size: 0.875rem;">
            💡 <strong>Consiglio:</strong> Concentrati prima sull'estinzione del debito,
            poi inizia a costruire il fondo emergenza
        </span>
    </div>
    """, unsafe_allow_html=True)
