"""
MoneyMind v4.0 - Directive Financial Coach
==========================================
AI-First, Mobile-Native, Freedom-Focused
Full Auto Daily Actions + Smart Suggestions
Single-page app with bottom tab navigation
"""

import streamlit as st
from pathlib import Path
import sys
from datetime import datetime, date
import pandas as pd
from dateutil.relativedelta import relativedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database import (
    init_db, get_transactions, get_spending_by_category,
    get_user_profile, get_total_debt, get_debts, get_goals,
    get_categories, get_budgets, get_today_actions, get_pending_action_count,
    get_monthly_summary, complete_daily_action, add_decision, dismiss_daily_action,
    get_recurring_expenses,
    # v4.0 Chat persistence
    add_chat_message, get_chat_history, get_chat_sessions,
    # v4.0 Wizard
    save_user_profile, add_debt,
    # v4.0 Import
    insert_transactions
)
from analytics import (
    get_financial_snapshot, calculate_financial_health_score,
    get_top_spending_categories
)
from styles import (
    get_custom_css, COLORS,
    freedom_score_card, metric_card, transaction_row,
    insight_card, section_header, chat_bubble, suggested_question,
    phase_card, goal_progress_card, debt_card, timeline_item,
    profile_header, action_row, kpi_indicator, budget_row,
    # v4.0 Directive Components
    home_greeting, plan_vs_actual_card, daily_action_task,
    scenario_comparison_mini, daily_actions_header, empty_state,
    decision_confirmation_card, recurring_expense_card,
    # v4.0 Wizard
    wizard_step_indicator
)

# v4.0 Core Finance Imports
from core_finance.baseline import BaselineCalculator
from core_finance.debt_planner import DebtPlanner
from core_finance.replanner import MonthlyReplanner

# v4.0 AI Imports
from ai.advisor import get_financial_advice
from ai.categorizer import categorize_transactions

# v4.0 Import Parsers
from parsers.revolut import parse_revolut
from parsers.illimity import parse_illimity

# =============================================================================
# PAGE CONFIG - Mobile-First
# =============================================================================
st.set_page_config(
    page_title="MoneyMind",
    page_icon="🧠",
    layout="centered",  # Mobile-first, not wide
    initial_sidebar_state="collapsed"
)

# Apply custom CSS (hides sidebar, adds bottom nav space)
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Initialize database
init_db()

# =============================================================================
# SESSION STATE
# =============================================================================
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "home"

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# v4.0: Chat session persistence
if "chat_session_id" not in st.session_state:
    # Generate unique session ID for this chat session
    from datetime import datetime
    st.session_state.chat_session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

if "chat_loaded" not in st.session_state:
    st.session_state.chat_loaded = False

if "money_subtab" not in st.session_state:
    st.session_state.money_subtab = "transactions"

# v4.0: Decision confirmation state
if "pending_decision" not in st.session_state:
    st.session_state.pending_decision = None  # Stores action awaiting confirmation

# v4.0: Wizard state
if "wizard_step" not in st.session_state:
    st.session_state.wizard_step = 1

if "wizard_data" not in st.session_state:
    st.session_state.wizard_data = {
        "income": 0,
        "income_type": "employed",
        "debts": [],
        "aggressiveness": 3,
        "essential_expenses": 0,
    }

if "show_wizard" not in st.session_state:
    # Show wizard if no profile or income not set
    profile = get_user_profile()
    st.session_state.show_wizard = not profile or not profile.get("monthly_net_income")

# v4.0: Import state
if "import_transactions" not in st.session_state:
    st.session_state.import_transactions = []  # Parsed transactions awaiting import
if "import_categorized" not in st.session_state:
    st.session_state.import_categorized = False  # Whether AI categorization was run

# =============================================================================
# DATA LOADING
# =============================================================================
@st.cache(allow_output_mutation=True, ttl=60, suppress_st_warning=True)
def load_dashboard_data():
    """Load all data needed for dashboard."""
    current_month = datetime.now().strftime("%Y-%m")
    today = date.today().isoformat()

    transactions = get_transactions()
    profile = get_user_profile()
    debts = get_debts(active_only=True)
    goals = get_goals(status="active")
    health_score = calculate_financial_health_score()
    snapshot = get_financial_snapshot(current_month)
    top_spending = get_top_spending_categories(current_month)
    categories = get_categories()
    budgets = get_budgets(current_month)

    # v4.0: Daily Actions
    today_actions = get_today_actions(today)
    pending_action_count = get_pending_action_count()

    # v4.0: Baseline comparison
    baseline_calc = BaselineCalculator()
    baseline = baseline_calc.calculate_3mo_baseline(current_month)
    baseline_comparison = baseline_calc.compare_to_baseline(current_month)

    # v4.0: Scenario comparison
    debt_planner = DebtPlanner()
    scenario_comparison = debt_planner.calculate_scenario_comparison(extra_monthly=50)

    return {
        "transactions": transactions,
        "profile": profile,
        "debts": debts,
        "goals": goals,
        "health_score": health_score,
        "snapshot": snapshot,
        "top_spending": top_spending,
        "categories": categories,
        "budgets": budgets,
        "current_month": current_month,
        # v4.0 additions
        "today_actions": today_actions,
        "pending_action_count": pending_action_count,
        "baseline": baseline,
        "baseline_comparison": baseline_comparison,
        "scenario_comparison": scenario_comparison,
    }

data = load_dashboard_data()

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def get_user_name():
    """Get user's name from profile."""
    if data["profile"] and data["profile"].get("name"):
        return data["profile"]["name"]
    return "Marco"

def get_phase_info():
    """Determine current financial phase."""
    has_debt = len(data["debts"]) > 0 if data["debts"] else False
    if has_debt:
        return {
            "name": "Debt Payoff",
            "icon": "🎯",
            "focus": "Focus: Elimina i debiti",
            "tip": "Paga prima il debito con tasso più alto"
        }
    return {
        "name": "Wealth Building",
        "icon": "🚀",
        "focus": "Focus: Costruisci patrimonio",
        "tip": "Investi regolarmente per il futuro"
    }

def get_score_message(score):
    """Get motivational message based on score."""
    if score >= 80:
        return "Eccellente! Sei sulla strada giusta verso la libertà finanziaria."
    elif score >= 60:
        return "Stai andando bene! Continua a concentrarti sui tuoi obiettivi."
    elif score >= 40:
        return "Buon inizio! Focus sui debiti per migliorare."
    else:
        return "Non mollare! Ogni piccolo passo conta."

# =============================================================================
# WIZARD: Setup Guidato v4.0
# =============================================================================
def render_wizard():
    """Render the setup wizard for first-time users."""
    step = st.session_state.wizard_step
    wizard_data = st.session_state.wizard_data
    TOTAL_STEPS = 5

    # Wizard header
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 2rem;">
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">💰</div>
        <div style="font-size: 1.5rem; font-weight: 700; color: {COLORS['text_primary']};">
            Benvenuto in MoneyMind
        </div>
        <div style="color: {COLORS['text_muted']}; font-size: 0.875rem;">
            Configura il tuo percorso verso la libertà finanziaria
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Step indicator
    step_names = ["Benvenuto", "Reddito", "Debiti", "Obiettivi", "Piano"]
    st.markdown(wizard_step_indicator(step, TOTAL_STEPS, step_names[step - 1]), unsafe_allow_html=True)

    # Step 1: Welcome
    if step == 1:
        st.markdown(f"""
        <div style="background: {COLORS['bg_secondary']}; border-radius: {12}px; padding: 1.5rem; margin-bottom: 1rem;">
            <div style="font-size: 1.125rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 1rem;">
                🎯 Cosa farà MoneyMind per te
            </div>
            <div style="color: {COLORS['text_secondary']}; line-height: 1.8;">
                • <strong>Traccia</strong> automaticamente le tue spese<br>
                • <strong>Ottimizza</strong> il piano di pagamento debiti<br>
                • <strong>Suggerisce</strong> azioni quotidiane per risparmiare<br>
                • <strong>Mostra</strong> quanto tempo puoi guadagnare verso la libertà finanziaria
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Inizia la configurazione →", use_container_width=True):
            st.session_state.wizard_step = 2
            st.experimental_rerun()

    # Step 2: Income
    elif step == 2:
        st.markdown(f"<div style='color: {COLORS['text_secondary']}; margin-bottom: 1rem;'>Quanto guadagni ogni mese (al netto delle tasse)?</div>", unsafe_allow_html=True)

        income_type = st.selectbox(
            "Tipo di reddito",
            ["employed", "freelance", "mixed"],
            format_func=lambda x: {"employed": "Dipendente", "freelance": "Libero professionista", "mixed": "Misto"}[x],
            index=0
        )
        wizard_data["income_type"] = income_type

        income = st.number_input(
            "Reddito mensile netto (€)",
            min_value=0,
            max_value=50000,
            value=wizard_data.get("income", 2000),
            step=100
        )
        wizard_data["income"] = income

        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Indietro"):
                st.session_state.wizard_step = 1
                st.experimental_rerun()
        with col2:
            if st.button("Avanti →", disabled=income <= 0):
                st.session_state.wizard_step = 3
                st.experimental_rerun()

    # Step 3: Debts
    elif step == 3:
        st.markdown(f"<div style='color: {COLORS['text_secondary']}; margin-bottom: 1rem;'>Hai debiti da pagare? (Prestiti, finanziamenti, carte revolving)</div>", unsafe_allow_html=True)

        has_debts = st.radio("Hai debiti attivi?", ["Sì", "No"], horizontal=True)

        if has_debts == "Sì":
            st.markdown(f"<div style='color: {COLORS['text_muted']}; font-size: 0.875rem; margin: 1rem 0;'>Aggiungi i tuoi debiti (potrai aggiungerne altri dopo)</div>", unsafe_allow_html=True)

            with st.expander("➕ Aggiungi debito", expanded=len(wizard_data["debts"]) == 0):
                debt_name = st.text_input("Nome (es. Prestito Auto)", key="new_debt_name")
                debt_balance = st.number_input("Saldo residuo (€)", min_value=0, max_value=500000, value=0, step=100, key="new_debt_balance")
                debt_rate = st.number_input("Tasso interesse annuo (%)", min_value=0.0, max_value=30.0, value=5.0, step=0.1, key="new_debt_rate")
                debt_payment = st.number_input("Rata mensile (€)", min_value=0, max_value=10000, value=0, step=10, key="new_debt_payment")

                if st.button("Aggiungi debito"):
                    if debt_name and debt_balance > 0 and debt_payment > 0:
                        wizard_data["debts"].append({
                            "name": debt_name,
                            "balance": debt_balance,
                            "rate": debt_rate,
                            "payment": debt_payment
                        })
                        st.experimental_rerun()

            # Show added debts
            if wizard_data["debts"]:
                st.markdown(f"<div style='color: {COLORS['text_primary']}; font-weight: 600; margin-top: 1rem;'>Debiti aggiunti:</div>", unsafe_allow_html=True)
                for i, d in enumerate(wizard_data["debts"]):
                    col_d, col_x = st.columns([5, 1])
                    with col_d:
                        st.markdown(f"• **{d['name']}**: €{d['balance']:,.0f} @ {d['rate']}% (€{d['payment']}/mese)")
                    with col_x:
                        if st.button("❌", key=f"del_debt_{i}"):
                            wizard_data["debts"].pop(i)
                            st.experimental_rerun()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Indietro"):
                st.session_state.wizard_step = 2
                st.experimental_rerun()
        with col2:
            if st.button("Avanti →"):
                st.session_state.wizard_step = 4
                st.experimental_rerun()

    # Step 4: Aggressiveness
    elif step == 4:
        st.markdown(f"<div style='color: {COLORS['text_secondary']}; margin-bottom: 1rem;'>Quanto vuoi essere aggressivo nel ripagare i debiti?</div>", unsafe_allow_html=True)

        aggressiveness = st.slider(
            "Livello di aggressività",
            min_value=1,
            max_value=5,
            value=wizard_data.get("aggressiveness", 3),
            help="1 = Minimo (solo rate), 5 = Massimo (sacrifica tutto per i debiti)"
        )
        wizard_data["aggressiveness"] = aggressiveness

        labels = {
            1: "🐢 Tranquillo - Pago solo le rate minime",
            2: "🚶 Moderato - Aggiungo qualcosa quando posso",
            3: "🏃 Attivo - Cerco di pagare extra ogni mese",
            4: "🏎️ Aggressivo - Riduco spese non essenziali",
            5: "🚀 Massimo - Tutto sui debiti, minimo per vivere"
        }
        st.markdown(f"<div style='color: {COLORS['accent']}; font-weight: 600; text-align: center; margin: 1rem 0;'>{labels[aggressiveness]}</div>", unsafe_allow_html=True)

        # Essential expenses estimate
        st.markdown(f"<div style='color: {COLORS['text_secondary']}; margin: 1.5rem 0 0.5rem;'>Stima delle spese essenziali mensili:</div>", unsafe_allow_html=True)
        essential = st.number_input(
            "Spese essenziali (€) - affitto, utenze, cibo, trasporti",
            min_value=0,
            max_value=int(wizard_data["income"]),
            value=int(wizard_data["income"] * 0.5) if wizard_data.get("essential_expenses", 0) == 0 else wizard_data["essential_expenses"],
            step=50
        )
        wizard_data["essential_expenses"] = essential

        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Indietro"):
                st.session_state.wizard_step = 3
                st.experimental_rerun()
        with col2:
            if st.button("Avanti →"):
                st.session_state.wizard_step = 5
                st.experimental_rerun()

    # Step 5: Summary & Confirm
    elif step == 5:
        income = wizard_data["income"]
        debts = wizard_data["debts"]
        essential = wizard_data["essential_expenses"]
        aggressiveness = wizard_data["aggressiveness"]

        # Calculate projections
        total_debt = sum(d["balance"] for d in debts)
        total_payment = sum(d["payment"] for d in debts)
        available = income - essential - total_payment

        # Extra payment based on aggressiveness
        extra_multiplier = {1: 0, 2: 0.1, 3: 0.25, 4: 0.5, 5: 0.75}
        extra_payment = available * extra_multiplier[aggressiveness] if available > 0 else 0

        # Rough payoff estimate (simplified)
        if total_debt > 0 and (total_payment + extra_payment) > 0:
            months_to_payoff = total_debt / (total_payment + extra_payment)
            months_current = total_debt / total_payment if total_payment > 0 else 999
            months_saved = max(0, months_current - months_to_payoff)
        else:
            months_to_payoff = 0
            months_current = 0
            months_saved = 0

        st.markdown(f"""
        <div style="background: {COLORS['bg_secondary']}; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;">
            <div style="font-size: 1.125rem; font-weight: 600; color: {COLORS['text_primary']}; margin-bottom: 1rem;">
                📊 Il tuo piano
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div>
                    <div style="color: {COLORS['text_muted']}; font-size: 0.75rem;">Reddito</div>
                    <div style="color: {COLORS['income']}; font-weight: 700;">€{income:,.0f}/mese</div>
                </div>
                <div>
                    <div style="color: {COLORS['text_muted']}; font-size: 0.75rem;">Debito totale</div>
                    <div style="color: {COLORS['expense']}; font-weight: 700;">€{total_debt:,.0f}</div>
                </div>
                <div>
                    <div style="color: {COLORS['text_muted']}; font-size: 0.75rem;">Rate mensili</div>
                    <div style="color: {COLORS['text_primary']}; font-weight: 600;">€{total_payment:,.0f}</div>
                </div>
                <div>
                    <div style="color: {COLORS['text_muted']}; font-size: 0.75rem;">Extra suggerito</div>
                    <div style="color: {COLORS['accent']}; font-weight: 600;">+€{extra_payment:,.0f}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if total_debt > 0:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {COLORS['bg_secondary']} 0%, {COLORS['bg_tertiary']} 100%); border: 1px solid {COLORS['accent']}; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;">
                <div style="text-align: center;">
                    <div style="color: {COLORS['text_muted']}; font-size: 0.75rem; margin-bottom: 0.5rem;">Con MoneyMind sarai debt-free</div>
                    <div style="color: {COLORS['income']}; font-size: 1.5rem; font-weight: 700;">
                        {int(months_saved)} mesi prima! 🎉
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Indietro"):
                st.session_state.wizard_step = 4
                st.experimental_rerun()
        with col2:
            if st.button("✅ Attiva il piano", type="primary"):
                # Save profile
                save_user_profile({
                    "income_type": wizard_data["income_type"],
                    "monthly_net_income": wizard_data["income"],
                    "risk_tolerance": ["conservative", "moderate", "moderate", "aggressive", "aggressive"][aggressiveness - 1],
                    "financial_knowledge": "beginner",
                    "coaching_style": "guided"
                })

                # Save debts
                for d in wizard_data["debts"]:
                    add_debt({
                        "name": d["name"],
                        "type": "personal_loan",
                        "original_amount": d["balance"],
                        "current_balance": d["balance"],
                        "interest_rate": d["rate"],
                        "monthly_payment": d["payment"],
                        "payment_day": 1,
                        "is_active": True
                    })

                # Mark wizard as complete
                st.session_state.show_wizard = False
                st.session_state.wizard_step = 1
                st.experimental_rerun()


# =============================================================================
# TAB: HOME - v4.0 Directive Layout
# =============================================================================
def render_home_tab():
    """Render Home tab with directive layout: actions, baseline comparison, scenarios."""
    user_name = get_user_name()
    score_data = data["health_score"]
    score = score_data.get("total_score", 50)
    snapshot = data["snapshot"] or {}
    pending_count = data.get("pending_action_count", 0) or 0
    today_actions = data.get("today_actions", []) or []
    baseline_comparison = data.get("baseline_comparison", {}) or {}
    scenario = data.get("scenario_comparison")

    # v4.0: Greeting with pending actions badge
    st.markdown(home_greeting(
        name=user_name,
        pending_actions=pending_count
    ), unsafe_allow_html=True)

    # v4.0: Freedom Score (compact)
    st.markdown(freedom_score_card(
        score=int(score),
        message=get_score_message(score),
        grade=score_data.get("grade", "C")
    ), unsafe_allow_html=True)

    # v4.0: Plan vs Actual Cards
    st.markdown(section_header("Questo Mese vs Baseline"), unsafe_allow_html=True)

    current_savings = snapshot.get("net_cash_flow", 0) or 0
    # Handle dataclass comparison object
    if baseline_comparison and hasattr(baseline_comparison, 'savings_delta'):
        delta = baseline_comparison.savings_delta
        is_better = baseline_comparison.is_improving
    else:
        delta = current_savings
        is_better = current_savings >= 0

    # Determine on-track status
    has_debts = len(data["debts"] or []) > 0
    if has_debts:
        on_track_status = "on_track" if delta >= 0 else "behind"
        status_message = "Procedi secondo il piano" if delta >= 0 else f"€{abs(delta):.0f} sotto obiettivo"
    else:
        on_track_status = "completed"
        status_message = "Debt-free! Focus su risparmio"

    col1, col2 = st.columns(2)

    with col1:
        # Savings vs baseline card
        delta_sign = "+" if delta >= 0 else ""
        st.markdown(f"""
        <div style="
            background: {COLORS['bg_secondary']};
            border-radius: 16px;
            padding: 1rem;
            text-align: center;
            border-left: 4px solid {COLORS['income'] if delta >= 0 else COLORS['expense']};
        ">
            <div style="font-size: 0.75rem; color: {COLORS['text_muted']}; text-transform: uppercase;">
                vs Baseline
            </div>
            <div style="font-size: 1.5rem; font-weight: 700; color: {COLORS['income'] if delta >= 0 else COLORS['expense']};">
                {delta_sign}EUR{abs(delta):,.0f}
            </div>
            <div style="font-size: 0.75rem; color: {COLORS['text_secondary']};">
                risparmio mensile
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # On-track status card
        status_colors = {
            "on_track": COLORS["income"],
            "behind": COLORS["expense"],
            "ahead": COLORS["accent"],
            "completed": COLORS["accent"]
        }
        status_icons = {
            "on_track": "CHECK",
            "behind": "WARN",
            "ahead": "UP",
            "completed": "STAR"
        }
        status_color = status_colors.get(on_track_status, COLORS["text_muted"])

        st.markdown(f"""
        <div style="
            background: {COLORS['bg_secondary']};
            border-radius: 16px;
            padding: 1rem;
            text-align: center;
            border-left: 4px solid {status_color};
        ">
            <div style="font-size: 0.75rem; color: {COLORS['text_muted']}; text-transform: uppercase;">
                Stato Piano
            </div>
            <div style="font-size: 1.25rem; font-weight: 700; color: {status_color};">
                {"On Track" if on_track_status == "on_track" else "In Ritardo" if on_track_status == "behind" else "Debt-Free!"}
            </div>
            <div style="font-size: 0.75rem; color: {COLORS['text_secondary']};">
                {status_message}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # v4.0: Daily Actions Section
    today_str = date.today().strftime("%d %B %Y")
    completed_count = len([a for a in today_actions if a.get("status") == "completed"])
    pending_today = len([a for a in today_actions if a.get("status") == "pending"])

    st.markdown(daily_actions_header(
        date_str=today_str,
        pending_count=pending_today,
        completed_count=completed_count
    ), unsafe_allow_html=True)

    # v4.0: Decision Confirmation Modal (if pending)
    if st.session_state.pending_decision:
        action = st.session_state.pending_decision
        st.markdown(decision_confirmation_card(
            title=action.get("title", "Conferma Azione"),
            description=action.get("description", ""),
            impact_monthly=action.get("estimated_impact_monthly", 0),
            impact_days=action.get("estimated_impact_payoff_days", 0)
        ), unsafe_allow_html=True)

        col_accept, col_reject, col_later = st.columns(3)
        with col_accept:
            if st.button("Accetta", key="decision_accept"):
                # Create decision record
                decision_id = add_decision({
                    "decision_date": date.today().isoformat(),
                    "type": action.get("action_type", "generic"),
                    "category_id": action.get("category_id"),
                    "debt_id": action.get("debt_id"),
                    "recurring_expense_id": action.get("recurring_expense_id"),
                    "description": action.get("title"),
                    "status": "accepted",
                    "expected_impact_monthly": action.get("estimated_impact_monthly"),
                    "expected_impact_payoff_days": action.get("estimated_impact_payoff_days"),
                    "insight_id": action.get("insight_id"),
                })
                # Complete the action with decision link
                complete_daily_action(action.get("id"), decision_id)
                st.session_state.pending_decision = None
                st.experimental_rerun()
        with col_reject:
            if st.button("Rifiuta", key="decision_reject"):
                # Mark as dismissed, no decision record
                dismiss_daily_action(action.get("id"))
                st.session_state.pending_decision = None
                st.experimental_rerun()
        with col_later:
            if st.button("Rimanda", key="decision_later"):
                # Just close modal, keep action pending
                st.session_state.pending_decision = None
                st.experimental_rerun()

    # Display actions
    if today_actions:
        for action in today_actions[:3]:  # Max 3 actions per day
            impact_text = ""
            if action.get("estimated_impact_monthly"):
                impact_text = f"Risparmia EUR{action['estimated_impact_monthly']:.0f}/mese"
            elif action.get("estimated_impact_payoff_days"):
                impact_text = f"{action['estimated_impact_payoff_days']} giorni prima"

            st.markdown(daily_action_task(
                title=action.get("title", "Azione"),
                description=action.get("description", ""),
                impact_text=impact_text,
                is_completed=(action.get("status") == "completed"),
                priority=action.get("priority", 2),
                action_type=action.get("action_type", "generic")
            ), unsafe_allow_html=True)

            # Action buttons (only if not showing confirmation modal)
            if action.get("status") == "pending" and not st.session_state.pending_decision:
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("Completa", key=f"complete_{action.get('id', 0)}"):
                        # Show confirmation modal
                        st.session_state.pending_decision = action
                        st.experimental_rerun()
                with col_b:
                    if st.button("Rimanda", key=f"skip_{action.get('id', 0)}"):
                        dismiss_daily_action(action.get("id"))
                        st.experimental_rerun()
    else:
        st.markdown(empty_state(
            icon="✅",
            title="Nessuna azione per oggi",
            message="Ottimo lavoro! Tutte le azioni sono state completate o verranno generate domani.",
            action_text=None
        ), unsafe_allow_html=True)

    # v4.0: Scenario Comparison (only if debts exist)
    if scenario and scenario.months_saved > 0:
        st.markdown(section_header("Confronto Scenari"), unsafe_allow_html=True)

        # Parse dates from scenario dicts (ISO format strings)
        current_date_str = scenario.current_scenario.get("date")
        moneymind_date_str = scenario.moneymind_scenario.get("date")

        if current_date_str:
            from datetime import datetime as dt
            current_date = dt.fromisoformat(current_date_str).strftime("%b %Y")
        else:
            current_date = "N/A"

        if moneymind_date_str:
            from datetime import datetime as dt
            moneymind_date = dt.fromisoformat(moneymind_date_str).strftime("%b %Y")
        else:
            moneymind_date = "N/A"

        st.markdown(scenario_comparison_mini(
            current_payoff_date=current_date,
            moneymind_payoff_date=moneymind_date,
            months_saved=scenario.months_saved
        ), unsafe_allow_html=True)

    # v4.0: AI Insight (compact)
    st.markdown(section_header("AI Insight"), unsafe_allow_html=True)

    if data["top_spending"]:
        top_cat = data["top_spending"][0]

        # Simplified insight logic - show top spending
        st.markdown(insight_card(
            icon="💡",
            title=f"Spese {top_cat['category_name']}",
            message=f"Questo mese hai speso EUR{top_cat['amount']:,.0f} in {top_cat['category_name']}. "
                    f"Rappresenta il {top_cat['percentage']:.0f}% delle tue uscite.",
            severity="info",
            action_text="Parla con il Coach"
        ), unsafe_allow_html=True)
    else:
        st.markdown(insight_card(
            icon="👋",
            title="Benvenuto in MoneyMind!",
            message="Importa le tue transazioni per ricevere insight personalizzati e azioni quotidiane.",
            severity="info"
        ), unsafe_allow_html=True)


# =============================================================================
# TAB: MONEY
# =============================================================================
def render_money_tab():
    """Render Money tab with transactions, budget, trends, and recurring."""

    # Sub-tabs (v4.0: added Ricorrenti)
    tabs = st.tabs(["📋 Transazioni", "💰 Budget", "📈 Trend", "🔄 Ricorrenti"])

    with tabs[0]:
        render_transactions_subtab()

    with tabs[1]:
        render_budget_subtab()

    with tabs[2]:
        render_trends_subtab()

    with tabs[3]:
        render_recurring_subtab()


def render_transactions_subtab():
    """Render transactions list."""
    if not data["transactions"]:
        st.markdown(f"""
        <div style="text-align: center; padding: 3rem 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📥</div>
            <div style="color: {COLORS['text_primary']}; font-weight: 600; margin-bottom: 0.5rem;">
                Nessuna transazione
            </div>
            <div style="color: {COLORS['text_muted']}; font-size: 0.875rem;">
                Importa i tuoi file bancari per iniziare
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    df = pd.DataFrame(data["transactions"])
    df["date"] = pd.to_datetime(df["date"])

    # Month selector
    months = df["date"].dt.to_period("M").unique()
    month_options = [str(m) for m in sorted(months, reverse=True)[:6]]

    selected_month = st.selectbox("Mese", month_options)

    # Filter by month
    filtered = df[df["date"].dt.to_period("M").astype(str) == selected_month]
    filtered = filtered.sort_values("date", ascending=False)

    # Group by date
    for date in filtered["date"].dt.date.unique()[:10]:
        day_df = filtered[filtered["date"].dt.date == date]

        st.markdown(f"""
        <div style="color: {COLORS['text_muted']}; font-size: 0.75rem; margin: 1rem 0 0.5rem 0; text-transform: uppercase;">
            {date.strftime('%A %d %B')}
        </div>
        """, unsafe_allow_html=True)

        for _, row in day_df.iterrows():
            category = row.get("category_name") or "Altro"
            icons = {
                "Spesa": "🛒", "Ristoranti": "🍕", "Trasporti": "🚗",
                "Utenze": "⚡", "Stipendio": "💰", "Abbonamenti": "📱",
                "Shopping": "🛍️", "Salute": "💊", "Intrattenimento": "🎬",
                "Finanziamenti": "🏦", "Risparmi Automatici": "🐷", "Altro": "📦"
            }
            icon = icons.get(category, "📦")

            st.markdown(transaction_row(
                icon=icon,
                description=str(row["description"])[:35],
                date=row["date"].strftime("%H:%M") if pd.notna(row["date"]) else "",
                category=category,
                amount=row["amount"]
            ), unsafe_allow_html=True)


def render_budget_subtab():
    """Render budget progress."""
    budgets = data["budgets"]
    categories = {c["id"]: c for c in data["categories"]} if data["categories"] else {}

    if not budgets:
        st.markdown(f"""
        <div style="text-align: center; padding: 3rem 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🎯</div>
            <div style="color: {COLORS['text_primary']}; font-weight: 600; margin-bottom: 0.5rem;">
                Nessun budget impostato
            </div>
            <div style="color: {COLORS['text_muted']}; font-size: 0.875rem;">
                Crea budget per controllare le tue spese
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Get spending by category for current month
    spending = data["top_spending"] or []
    spending_by_cat = {s["category_name"]: s["amount"] for s in spending}

    for budget in budgets:
        cat_id = budget.get("category_id")
        cat = categories.get(cat_id, {})
        cat_name = cat.get("name", "Categoria")
        cat_icon = cat.get("icon", "📦")
        budget_amount = budget.get("amount", 0)
        spent = spending_by_cat.get(cat_name, 0)

        st.markdown(budget_row(
            category=cat_name,
            icon=cat_icon,
            spent=spent,
            budget=budget_amount
        ), unsafe_allow_html=True)


def render_trends_subtab():
    """Render spending trends."""
    import plotly.graph_objects as go

    if not data["transactions"]:
        st.info("Importa transazioni per vedere i trend")
        return

    df = pd.DataFrame(data["transactions"])
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)

    # Last 6 months
    months = sorted(df["month"].unique())[-6:]
    df = df[df["month"].isin(months)]

    monthly = df.groupby("month").agg(
        entrate=("amount", lambda x: x[x > 0].sum()),
        uscite=("amount", lambda x: abs(x[x < 0].sum()))
    ).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Entrate",
        x=monthly["month"],
        y=monthly["entrate"],
        marker_color=COLORS["income"],
    ))
    fig.add_trace(go.Bar(
        name="Uscite",
        x=monthly["month"],
        y=monthly["uscite"],
        marker_color=COLORS["expense"],
    ))

    fig.update_layout(
        barmode="group",
        paper_bgcolor=COLORS["bg_secondary"],
        plot_bgcolor=COLORS["bg_secondary"],
        font=dict(color=COLORS["text_secondary"]),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(gridcolor=COLORS["border"]),
        yaxis=dict(gridcolor=COLORS["border"]),
        height=250,
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_recurring_subtab():
    """Render recurring expenses with optimization suggestions."""
    recurring = get_recurring_expenses(active_only=True)

    # Calculate totals
    total_monthly = sum(r.get("avg_amount", 0) for r in recurring) if recurring else 0
    profile = data.get("profile") or {}
    monthly_income = profile.get("monthly_net_income", 2500) or 2500
    percent_of_income = (total_monthly / monthly_income * 100) if monthly_income > 0 else 0

    # Summary header
    st.markdown(f"""
    <div style="
        background: {COLORS['bg_secondary']};
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 1.5rem;
        text-align: center;
    ">
        <div style="font-size: 0.75rem; color: {COLORS['text_muted']}; text-transform: uppercase; margin-bottom: 0.25rem;">
            Spese Ricorrenti Totali
        </div>
        <div style="font-size: 2rem; font-weight: 700; color: {COLORS['text_primary']};">
            EUR{total_monthly:,.0f}/mese
        </div>
        <div style="font-size: 0.875rem; color: {COLORS['text_secondary']};">
            {percent_of_income:.0f}% del tuo reddito
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not recurring:
        st.markdown(empty_state(
            icon="🔄",
            title="Nessuna spesa ricorrente",
            message="Importa le tue transazioni per identificare automaticamente le spese ricorrenti.",
            action_text=None
        ), unsafe_allow_html=True)
        return

    # Group by category
    categories_map = {}
    for r in recurring:
        cat_name = r.get("category_name", "Altro")
        if cat_name not in categories_map:
            categories_map[cat_name] = []
        categories_map[cat_name].append(r)

    # Category icons
    cat_icons = {
        "Abbonamenti": "📱",
        "Utenze": "⚡",
        "Finanziamenti": "🏦",
        "Assicurazioni": "🛡️",
        "Altro": "📦"
    }

    # Display by category
    for cat_name, expenses in categories_map.items():
        cat_total = sum(e.get("avg_amount", 0) for e in expenses)
        icon = cat_icons.get(cat_name, "📦")

        st.markdown(f"""
        <div style="margin: 1.5rem 0 0.75rem 0;">
            <span style="font-size: 1.125rem; font-weight: 600; color: {COLORS['text_primary']};">
                {icon} {cat_name.upper()}
            </span>
            <span style="color: {COLORS['text_muted']}; margin-left: 0.5rem;">
                EUR{cat_total:,.0f}/mese
            </span>
        </div>
        """, unsafe_allow_html=True)

        for expense in expenses:
            provider = expense.get("provider") or expense.get("pattern_name", "Spesa")
            amount = expense.get("avg_amount", 0)
            trend = expense.get("trend_percent", 0) or 0
            opt_status = expense.get("optimization_status", "not_reviewed")

            # Determine optimization suggestion
            suggestion = None
            if opt_status == "not_reviewed" and not expense.get("is_essential"):
                potential = amount * 0.15
                if potential >= 5:
                    suggestion = f"Potenziale risparmio: EUR{potential:.0f}/mese"

            st.markdown(recurring_expense_card(
                provider=provider,
                amount=amount,
                category=cat_name,
                trend_percent=trend,
                optimization_potential="not_reviewed" if opt_status == "not_reviewed" else "optimized",
                suggestion=suggestion
            ), unsafe_allow_html=True)

            # Action button for non-essential, non-reviewed expenses
            if opt_status == "not_reviewed" and not expense.get("is_essential"):
                if st.button("Ottimizza", key=f"opt_{expense.get('id', 0)}"):
                    st.info(f"Analisi ottimizzazione per {provider} in arrivo...")

    # Optimization summary
    not_reviewed = [r for r in recurring if r.get("optimization_status") == "not_reviewed" and not r.get("is_essential")]
    if not_reviewed:
        potential_savings = sum(r.get("avg_amount", 0) * 0.15 for r in not_reviewed)

        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {COLORS['bg_secondary']} 0%, {COLORS['bg_tertiary']} 100%);
            border: 1px solid {COLORS['accent']};
            border-radius: 16px;
            padding: 1rem;
            margin-top: 1.5rem;
            text-align: center;
        ">
            <div style="font-size: 0.875rem; color: {COLORS['text_secondary']};">
                💡 Hai {len(not_reviewed)} spese da ottimizzare
            </div>
            <div style="font-size: 1.25rem; font-weight: 700; color: {COLORS['accent']}; margin-top: 0.25rem;">
                Risparmio potenziale: EUR{potential_savings:.0f}/mese
            </div>
        </div>
        """, unsafe_allow_html=True)


# =============================================================================
# TAB: COACH
# =============================================================================
def render_coach_tab():
    """Render AI Coach chat interface with persistence."""
    from datetime import datetime

    # v4.0: Load chat history from database on first load
    if not st.session_state.chat_loaded:
        history = get_chat_history(st.session_state.chat_session_id, limit=50)
        if history:
            st.session_state.chat_messages = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in history
            ]
        st.session_state.chat_loaded = True

    # Header with New Chat button
    col_header, col_new = st.columns([4, 1])
    with col_header:
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="width: 56px; height: 56px; background: {COLORS['accent']}; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 1.75rem; margin-bottom: 0.5rem;">🧠</div>
            <div style="font-size: 1.125rem; font-weight: 700; color: {COLORS['text_primary']};">MoneyMind Coach</div>
            <div style="color: {COLORS['text_muted']}; font-size: 0.8125rem;">Il tuo assistente finanziario personale</div>
        </div>
        """, unsafe_allow_html=True)
    with col_new:
        if st.button("🔄 Nuova", key="new_chat"):
            # Start new chat session
            st.session_state.chat_session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            st.session_state.chat_messages = []
            st.session_state.chat_loaded = True
            st.experimental_rerun()

    # Welcome message if no chat history
    if not st.session_state.chat_messages:
        user_name = get_user_name()
        welcome_msg = f"""Ciao {user_name}! 👋 Sono il tuo coach finanziario personale.

Posso aiutarti con:
• Analisi delle tue spese e consigli su come risparmiare
• Strategie per pagare i debiti più velocemente
• Pianificazione del fondo emergenza
• Obiettivi di risparmio e investimento

Come posso aiutarti oggi?"""

        st.markdown(chat_bubble(welcome_msg, is_ai=True), unsafe_allow_html=True)

    # Display chat history
    for msg in st.session_state.chat_messages:
        st.markdown(chat_bubble(
            msg["content"],
            is_ai=msg["role"] == "assistant"
        ), unsafe_allow_html=True)

    # Suggested questions
    if not st.session_state.chat_messages:
        st.markdown(section_header("Domande Suggerite"), unsafe_allow_html=True)

        questions = [
            "Come posso pagare i debiti più velocemente?",
            "Quanto dovrei risparmiare ogni mese?",
            "Dove sto spendendo troppo?",
            "Quando sarò debt-free?"
        ]

        cols = st.columns(2)
        for i, q in enumerate(questions):
            with cols[i % 2]:
                if st.button(q, key=f"q_{i}"):
                    _send_chat_message(q)
                    st.experimental_rerun()

    # Chat input (compatible with older Streamlit)
    st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input("", placeholder="Scrivi un messaggio...", key="chat_input")
    with col2:
        send_clicked = st.button("Invia")

    if send_clicked and user_input:
        _send_chat_message(user_input)
        st.experimental_rerun()


def _send_chat_message(message: str):
    """Send a chat message and save to database."""
    session_id = st.session_state.chat_session_id

    # Add user message to session and database
    st.session_state.chat_messages.append({"role": "user", "content": message})
    add_chat_message(session_id, "user", message)

    # Generate AI response
    response = generate_coach_response(message)

    # Add assistant message to session and database
    st.session_state.chat_messages.append({"role": "assistant", "content": response})
    add_chat_message(session_id, "assistant", response)


def generate_coach_response(question: str) -> str:
    """
    Generate AI coach response using Claude Opus 4.5.

    v4.0: Uses real AI advisor with financial context.
    Falls back to rule-based for simple greetings.
    """
    import os
    score = data["health_score"].get("total_score", 50)
    debts = data["debts"] or []
    snapshot = data["snapshot"] or {}
    top_spending = data["top_spending"] or []
    total_debt = get_total_debt()
    profile = data.get("profile") or {}

    q_lower = question.lower()

    # Simple greeting - no AI needed
    if any(g in q_lower for g in ["ciao", "hello", "buongiorno", "salve"]):
        user_name = get_user_name()
        return f"""Ciao {user_name}! 👋 Come posso aiutarti oggi?

Posso aiutarti con:
• Strategie per pagare i debiti più velocemente
• Analisi delle tue spese
• Pianificazione del risparmio
• Obiettivi finanziari personalizzati

Dimmi pure cosa ti interessa!"""

    # Check if API key is available
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        # Fallback to rule-based responses
        return _generate_rule_based_response(question, score, debts, snapshot, top_spending, total_debt, profile)

    # Build rich context for AI
    context = {
        "month": data.get("current_month", ""),
        "net_worth": snapshot.get("net_worth", 0),
        "total_assets": snapshot.get("total_assets", 0),
        "total_debt": total_debt,
        "total_income": snapshot.get("income", 0),
        "total_expenses": abs(snapshot.get("expenses", 0)),
        "net_cash_flow": snapshot.get("net_cash_flow", 0),
        "savings_rate": snapshot.get("savings_rate", 0),
        "dti_ratio": snapshot.get("dti_ratio", 0),
        "health_score": score,
        "debts": debts,
        "goals": data.get("goals", []),
        "top_spending": top_spending,
        "monthly_income": profile.get("monthly_net_income", 0),
        "pending_actions": data.get("pending_action_count", 0),
    }

    try:
        result = get_financial_advice(
            question=question,
            context=context,
            use_extended_thinking=False  # Use standard mode for faster responses
        )
        # Check if API returned an error - use fallback
        if result.get("error"):
            return _generate_rule_based_response(question, score, debts, snapshot, top_spending, total_debt, profile)
        return result.get("advice", _generate_rule_based_response(question, score, debts, snapshot, top_spending, total_debt, profile))
    except Exception as e:
        # Fallback on error
        return _generate_rule_based_response(question, score, debts, snapshot, top_spending, total_debt, profile)


def _generate_rule_based_response(question: str, score: int, debts: list, snapshot: dict,
                                   top_spending: list, total_debt: float, profile: dict) -> str:
    """Fallback rule-based responses when AI is unavailable."""
    q_lower = question.lower()

    # Debt payoff questions
    if "debit" in q_lower or "pagare" in q_lower or "debt" in q_lower:
        if debts:
            sorted_debts = sorted(debts, key=lambda d: d.get("interest_rate", 0) or 0, reverse=True)
            top_debt = sorted_debts[0]
            rate = top_debt.get("interest_rate", 0) or 0
            balance = top_debt.get("current_balance", 0)

            return f"""Ottima domanda! Con la tua situazione, ti consiglio la **strategia Avalanche**:

1. **Paga prima {top_debt['name']}** ({rate}% APR)
   - Saldo: EUR{balance:,.0f}
   - E il debito piu costoso

2. **Poi concentrati** sugli altri in ordine di tasso

Pro tip: Ogni EUR50 extra che paghi su {top_debt['name']} ti fa risparmiare circa EUR{50 * rate / 100:.0f} in interessi!

Vuoi che ti mostri una simulazione del piano di pagamento?"""
        else:
            return "Complimenti! Non hai debiti attivi. Ora puoi concentrarti sulla costruzione del tuo patrimonio."

    # Savings questions
    elif "risparm" in q_lower or "sav" in q_lower:
        savings_rate = snapshot.get("savings_rate", 0) or 0
        monthly_income = profile.get("monthly_net_income", 2500) or 2500
        target_savings = monthly_income * 0.20

        return f"""Il tuo tasso di risparmio attuale e **{savings_rate:.1f}%**.

L'obiettivo consigliato e **20%** del reddito, che per te significherebbe circa **EUR{target_savings:,.0f}/mese**.

Per aumentare il risparmio:
1. **Automatizza**: imposta un trasferimento automatico il giorno dello stipendio
2. **Taglia le spese non essenziali** dove possibile
3. **Usa la regola del 50/30/20**: 50% necessita, 30% desideri, 20% risparmio"""

    # Spending questions
    elif "spend" in q_lower or "spes" in q_lower or "spendendo" in q_lower:
        if top_spending:
            top = top_spending[0]
            return f"""Ho analizzato le tue spese di questo mese.

La categoria principale e **{top['category_name']}** con **EUR{top['amount']:,.0f}** ({top['percentage']:.0f}% del totale).

Top 3 categorie:
{chr(10).join([f"- {s['category_icon']} {s['category_name']}: EUR{s['amount']:,.0f}" for s in top_spending[:3]])}

Consiglio: Se vuoi tagliare, inizia dalle piccole spese ricorrenti come abbonamenti o caffe al bar."""
        else:
            return "Non ho ancora abbastanza dati sulle tue spese. Importa le tue transazioni bancarie per ricevere un'analisi dettagliata!"

    # Debt-free timeline
    elif "quando" in q_lower or "debt-free" in q_lower or "libero" in q_lower:
        if total_debt > 0:
            monthly_payment = sum(d.get("monthly_payment", 0) or 0 for d in debts)
            if monthly_payment > 0:
                months = int(total_debt / monthly_payment)
                years = months // 12
                remaining_months = months % 12

                return f"""Con il tuo piano attuale, sarai **debt-free in circa {years} anni e {remaining_months} mesi**.

Debito totale: **EUR{total_debt:,.0f}**
Pagamento mensile: **EUR{monthly_payment:,.0f}**

Vuoi accelerare? Se aggiungi solo EUR100/mese extra, risparmi mesi di interessi!"""
            else:
                return f"Hai EUR{total_debt:,.0f} di debito. Per calcolare quando sarai debt-free, dimmi quanto riesci a pagare ogni mese."
        else:
            return "Sei gia debt-free! Complimenti! Ora e il momento di costruire il tuo patrimonio."

    # Default response
    else:
        return f"""Grazie per la tua domanda!

In base alla tua situazione:
- Freedom Score: **{score}/100**
- Debito totale: **EUR{total_debt:,.0f}**
- Focus attuale: **{'Pagare i debiti' if total_debt > 0 else 'Costruire patrimonio'}**

Posso aiutarti con strategie per pagare i debiti, analisi delle spese, pianificazione del risparmio e obiettivi finanziari.

Cosa ti interessa approfondire?"""


# =============================================================================
# TAB: GOALS
# =============================================================================
def render_goals_tab():
    """Render Goals tab with debt journey and future goals."""

    total_debt = get_total_debt()
    debts = data["debts"] or []
    goals = data["goals"] or []
    profile = data["profile"] or {}

    # Main goal: Debt Freedom
    if total_debt > 0:
        # Calculate original total debt (sum of original amounts)
        original_total = sum(d.get("original_amount", d.get("current_balance", 0)) for d in debts)
        paid_off = original_total - total_debt

        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, {COLORS['bg_secondary']} 0%, {COLORS['bg_tertiary']} 100%);
            border: 2px solid {COLORS['accent']};
            border-radius: 20px;
            padding: 1.5rem;
            text-align: center;
            margin-bottom: 1.5rem;
        ">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🏆</div>
            <div style="font-size: 0.75rem; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 0.1em;">
                Obiettivo Principale
            </div>
            <div style="font-size: 1.25rem; font-weight: 700; color: {COLORS['text_primary']}; margin: 0.5rem 0;">
                Debt Freedom
            </div>
            <div style="font-size: 2rem; font-weight: 700; color: {COLORS['accent']};">
                €{total_debt:,.0f}
            </div>
            <div style="color: {COLORS['text_muted']}; font-size: 0.875rem; margin-bottom: 1rem;">
                rimanenti da pagare
            </div>
            <div style="
                background: {COLORS['track']};
                border-radius: 999px;
                height: 10px;
                overflow: hidden;
            ">
                <div style="
                    background: linear-gradient(90deg, {COLORS['accent']} 0%, {COLORS['income']} 100%);
                    height: 100%;
                    width: {min(100, (paid_off / original_total * 100) if original_total > 0 else 0)}%;
                    border-radius: 999px;
                "></div>
            </div>
            <div style="color: {COLORS['income']}; font-size: 0.875rem; margin-top: 0.5rem; font-weight: 600;">
                {(paid_off / original_total * 100) if original_total > 0 else 0:.0f}% completato
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Debt list (sorted by interest rate - Avalanche)
        st.markdown(section_header("I Tuoi Debiti"), unsafe_allow_html=True)

        sorted_debts = sorted(debts, key=lambda d: d.get("interest_rate", 0) or 0, reverse=True)

        for i, debt in enumerate(sorted_debts):
            st.markdown(debt_card(
                name=debt.get("name", "Debito"),
                balance=debt.get("current_balance", 0),
                original=debt.get("original_amount", debt.get("current_balance", 0)),
                rate=debt.get("interest_rate"),
                monthly=debt.get("monthly_payment"),
                is_priority=(i == 0)
            ), unsafe_allow_html=True)

        # Timeline
        st.markdown(section_header("Timeline"), unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background: {COLORS['bg_secondary']}; border-radius: 12px; padding: 1rem;">
        """, unsafe_allow_html=True)

        # Create simple timeline
        current_date = datetime.now()

        for i, debt in enumerate(sorted_debts[:3]):
            monthly = debt.get("monthly_payment", 100) or 100
            balance = debt.get("current_balance", 0)
            months = int(balance / monthly) if monthly > 0 else 12
            target_date = current_date.replace(month=((current_date.month + months - 1) % 12) + 1)

            st.markdown(timeline_item(
                date=target_date.strftime("%b %Y"),
                label=f"{debt.get('name', 'Debito')} completato",
                is_current=(i == 0)
            ), unsafe_allow_html=True)

        # Final milestone
        total_months = sum(
            int((d.get("current_balance", 0) / (d.get("monthly_payment", 100) or 100)))
            for d in debts
        )
        final_date = current_date.replace(month=((current_date.month + total_months - 1) % 12) + 1)

        st.markdown(timeline_item(
            date=final_date.strftime("%b %Y"),
            label="DEBT FREE! 🎉",
            is_completed=False
        ), unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    else:
        # No debt - show wealth building goals
        st.markdown(f"""
        <div style="text-align: center; padding: 2rem 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🎉</div>
            <div style="font-size: 1.25rem; font-weight: 700; color: {COLORS['income']}; margin-bottom: 0.5rem;">
                Sei Debt-Free!
            </div>
            <div style="color: {COLORS['text_muted']};">
                Ora concentrati sulla costruzione del patrimonio
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Future goals
    st.markdown(section_header("Prossimi Obiettivi"), unsafe_allow_html=True)

    # Emergency fund
    monthly_income = profile.get("monthly_net_income", 2500) or 2500
    ef_target = monthly_income * 3
    ef_current = profile.get("emergency_fund", 0) or 0

    st.markdown(goal_progress_card(
        name="Fondo Emergenza",
        current=ef_current,
        target=ef_target,
        icon="🛡️",
        subtitle="3 mesi di spese",
        is_locked=(total_debt > 0)
    ), unsafe_allow_html=True)

    # Custom goals
    for goal in goals[:3]:
        st.markdown(goal_progress_card(
            name=goal.get("name", "Obiettivo"),
            current=goal.get("current_amount", 0),
            target=goal.get("target_amount", 1000),
            icon=goal.get("icon", "🎯"),
            subtitle=goal.get("deadline"),
            is_locked=(total_debt > 0)
        ), unsafe_allow_html=True)


# =============================================================================
# TAB: PROFILE
# =============================================================================
def render_profile_tab():
    """Render Profile tab with settings and health KPIs."""

    profile = data["profile"] or {}
    score_data = data["health_score"]
    snapshot = data["snapshot"] or {}
    phase = get_phase_info()

    # Profile header
    st.markdown(profile_header(
        name=profile.get("name", "Utente"),
        income=profile.get("monthly_net_income", 0) or 0,
        phase=phase["name"]
    ), unsafe_allow_html=True)

    # Health KPIs
    st.markdown(section_header("Salute Finanziaria"), unsafe_allow_html=True)

    score = score_data.get("total_score", 50)
    st.markdown(f"""
    <div style="
        background: {COLORS['bg_secondary']};
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    ">
        <span style="color: {COLORS['text_secondary']};">Freedom Score</span>
        <span style="color: {COLORS['accent'] if score < 60 else COLORS['income']}; font-size: 1.5rem; font-weight: 700;">
            {score}/100
        </span>
    </div>
    """, unsafe_allow_html=True)

    # KPI indicators
    savings_rate = snapshot.get("savings_rate", 0) or 0
    dti_ratio = snapshot.get("dti_ratio", 0) or 0
    ef_months = snapshot.get("emergency_fund_months", 0) or 0

    st.markdown(kpi_indicator(
        label="Tasso di Risparmio",
        value=f"{savings_rate:.1f}%",
        target="Obiettivo: 20%",
        status="good" if savings_rate >= 20 else ("warning" if savings_rate >= 10 else "critical")
    ), unsafe_allow_html=True)

    st.markdown(kpi_indicator(
        label="Rapporto Debito/Reddito",
        value=f"{dti_ratio:.1f}%",
        target="Obiettivo: <36%",
        status="good" if dti_ratio < 20 else ("warning" if dti_ratio < 36 else "critical")
    ), unsafe_allow_html=True)

    st.markdown(kpi_indicator(
        label="Fondo Emergenza",
        value=f"{ef_months:.1f} mesi",
        target="Obiettivo: 3 mesi",
        status="good" if ef_months >= 3 else ("warning" if ef_months >= 1 else "critical")
    ), unsafe_allow_html=True)

    # v4.0: Monthly Review Section
    st.markdown(section_header("Revisione Mensile"), unsafe_allow_html=True)

    current_month = datetime.now().strftime("%Y-%m")
    replanner = MonthlyReplanner()

    with st.expander("📊 Analisi mese precedente", expanded=False):
        prev_month = (datetime.now() - relativedelta(months=1)).strftime("%Y-%m")
        performance = replanner.analyze_month_performance(prev_month)

        if performance.get("status") == "no_data":
            st.info("Nessun dato disponibile per il mese precedente.")
        else:
            status_colors = {
                "on_track": COLORS["income"],
                "slightly_over": COLORS["warning"],
                "over_budget": COLORS["expense"],
                "needs_review": COLORS["text_muted"]
            }
            status_color = status_colors.get(performance.get("status", "needs_review"), COLORS["text_muted"])

            st.markdown(f"""
            <div style="background: {COLORS['bg_secondary']}; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: {COLORS['text_muted']};">Stato</span>
                    <span style="color: {status_color}; font-weight: 600;">{performance.get('status_message', 'N/A')}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: {COLORS['text_muted']};">Entrate</span>
                    <span style="color: {COLORS['income']};">€{performance.get('total_income', 0):,.0f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: {COLORS['text_muted']};">Uscite</span>
                    <span style="color: {COLORS['expense']};">€{performance.get('total_expenses', 0):,.0f}</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: {COLORS['text_muted']};">Risparmio</span>
                    <span style="color: {COLORS['income'] if performance.get('actual_savings', 0) >= 0 else COLORS['expense']}; font-weight: 600;">
                        €{performance.get('actual_savings', 0):,.0f} ({performance.get('savings_rate', 0):.1f}%)
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Show categories over budget
            over_cats = performance.get("categories_over_budget", [])
            if over_cats:
                st.markdown(f"<div style='color: {COLORS['warning']}; font-weight: 600; margin-bottom: 0.5rem;'>⚠️ Categorie sopra budget:</div>", unsafe_allow_html=True)
                for cat in over_cats[:3]:
                    st.markdown(f"• **{cat['category_name']}**: +€{cat['over_by']:.0f} ({cat['percent_over']:.0f}% sopra)")

    with st.expander("📅 Piano prossimo mese", expanded=False):
        new_plan = replanner.generate_replan(current_month)

        st.markdown(f"""
        <div style="background: {COLORS['bg_secondary']}; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
            <div style="color: {COLORS['text_primary']}; font-weight: 600; margin-bottom: 0.75rem;">Proiezioni per {current_month}</div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span style="color: {COLORS['text_muted']};">Risparmio previsto</span>
                <span style="color: {COLORS['income']}; font-weight: 600;">€{new_plan.get('projected_savings', 0):,.0f}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: {COLORS['text_muted']};">Savings Rate</span>
                <span style="color: {COLORS['text_secondary']};">{new_plan.get('projected_savings_rate', 0):.1f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Recommendations
        recommendations = new_plan.get("recommendations", [])
        if recommendations:
            st.markdown(f"<div style='color: {COLORS['accent']}; font-weight: 600; margin-bottom: 0.5rem;'>💡 Raccomandazioni:</div>", unsafe_allow_html=True)
            for rec in recommendations:
                st.markdown(f"• {rec}")

    # v4.0: Import Section
    st.markdown(section_header("Importa Transazioni"), unsafe_allow_html=True)

    with st.expander("📥 Carica file bancario", expanded=False):
        # Bank selection
        bank = st.selectbox(
            "Seleziona la banca",
            ["Revolut", "Illimity"],
            key="import_bank_select"
        )

        # File uploader
        file_type = "csv" if bank == "Revolut" else "xlsx"
        uploaded_file = st.file_uploader(
            f"Carica file {file_type.upper()}",
            type=[file_type],
            key="import_file_uploader"
        )

        if uploaded_file is not None:
            try:
                # Parse the file based on bank type
                if bank == "Revolut":
                    parsed = parse_revolut(uploaded_file)
                else:
                    parsed = parse_illimity(uploaded_file)

                st.session_state.import_transactions = parsed
                st.session_state.import_categorized = False

                # Show preview
                st.markdown(f"""
                <div style="background: {COLORS['bg_secondary']}; border-radius: 8px; padding: 1rem; margin: 1rem 0;">
                    <div style="color: {COLORS['accent']}; font-weight: 600; margin-bottom: 0.5rem;">
                        ✅ {len(parsed)} transazioni trovate
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Preview table
                if parsed:
                    preview_data = []
                    for tx in parsed[:10]:
                        preview_data.append({
                            "Data": tx["date"],
                            "Descrizione": tx["description"][:40] + "..." if len(tx["description"]) > 40 else tx["description"],
                            "Importo": f"€{tx['amount']:,.2f}"
                        })
                    st.dataframe(pd.DataFrame(preview_data), use_container_width=True)

                    if len(parsed) > 10:
                        st.caption(f"... e altre {len(parsed) - 10} transazioni")

            except Exception as e:
                st.error(f"Errore nel parsing del file: {str(e)}")

        # Show pending transactions and actions
        if st.session_state.import_transactions:
            st.markdown("---")
            col1, col2 = st.columns(2)

            with col1:
                if st.button("🤖 Categorizza con AI", use_container_width=True):
                    with st.spinner("Categorizzazione in corso..."):
                        try:
                            # Get categories for mapping
                            categories = get_categories()
                            cat_map = {c["id"]: c["name"] for c in categories}

                            # Categorize transactions
                            categorized = categorize_transactions(
                                st.session_state.import_transactions,
                                categories
                            )
                            st.session_state.import_transactions = categorized
                            st.session_state.import_categorized = True
                            st.success("Categorizzazione completata!")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Errore categorizzazione: {str(e)}")

            with col2:
                btn_label = "📥 Importa" if st.session_state.import_categorized else "📥 Importa (senza categorie)"
                if st.button(btn_label, use_container_width=True):
                    with st.spinner("Importazione in corso..."):
                        try:
                            count = insert_transactions(st.session_state.import_transactions)
                            st.session_state.import_transactions = []
                            st.session_state.import_categorized = False
                            st.success(f"✅ {count} transazioni importate!")
                            # Clear cache to refresh data
                            st.cache_data.clear()
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Errore importazione: {str(e)}")

            # Show categorization status
            if st.session_state.import_categorized:
                categories = get_categories()
                cat_map = {c["id"]: c["name"] for c in categories}

                categorized_count = sum(1 for tx in st.session_state.import_transactions if tx.get("category_id"))
                st.markdown(f"""
                <div style="background: {COLORS['bg_tertiary']}; border-radius: 8px; padding: 0.75rem; margin-top: 0.5rem;">
                    <span style="color: {COLORS['income']};">✓</span>
                    <span style="color: {COLORS['text_secondary']};">
                        {categorized_count}/{len(st.session_state.import_transactions)} transazioni categorizzate
                    </span>
                </div>
                """, unsafe_allow_html=True)

    # Actions
    st.markdown(section_header("Azioni"), unsafe_allow_html=True)

    st.markdown(action_row("📥", "Importa Transazioni", "Carica file CSV o XLSX"), unsafe_allow_html=True)
    st.markdown(action_row("👤", "Modifica Profilo", "Aggiorna i tuoi dati"), unsafe_allow_html=True)
    st.markdown(action_row("🏦", "Gestisci Debiti", "Aggiungi o modifica debiti"), unsafe_allow_html=True)
    st.markdown(action_row("🎯", "Obiettivi", "Crea nuovi obiettivi"), unsafe_allow_html=True)
    st.markdown(action_row("📤", "Esporta Dati", "Scarica i tuoi dati"), unsafe_allow_html=True)


# =============================================================================
# BOTTOM NAVIGATION (Streamlit 1.12.0 compatible)
# =============================================================================
def render_bottom_nav():
    """Render minimal fixed bottom navigation."""

    tabs = [
        ("home", "🏠", "Home"),
        ("money", "💳", "Money"),
        ("coach", "💬", "Coach"),
        ("goals", "🎯", "Goals"),
        ("profile", "👤", "Profilo"),
    ]

    # Fixed bottom nav styling
    st.markdown(f"""
    <style>
    /* Fixed bottom navigation container */
    div[data-testid="stHorizontalBlock"]:last-of-type {{
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        background: {COLORS['bg_primary']} !important;
        border-top: 1px solid {COLORS['border']} !important;
        padding: 0.5rem 0 !important;
        z-index: 9999 !important;
        margin: 0 !important;
        display: flex !important;
        justify-content: center !important;
    }}
    div[data-testid="stHorizontalBlock"]:last-of-type > div {{
        flex: 1 !important;
        max-width: 80px !important;
    }}
    /* Minimal nav button styling */
    div[data-testid="stHorizontalBlock"]:last-of-type .stButton > button {{
        background: transparent !important;
        border: none !important;
        color: {COLORS['text_muted']} !important;
        padding: 0.375rem 0.5rem !important;
        font-size: 1.125rem !important;
        font-weight: 400 !important;
        min-height: 0 !important;
        height: auto !important;
        line-height: 1 !important;
        box-shadow: none !important;
        width: 100% !important;
    }}
    div[data-testid="stHorizontalBlock"]:last-of-type .stButton > button:hover {{
        background: transparent !important;
        color: {COLORS['accent']} !important;
        transform: none !important;
    }}
    div[data-testid="stHorizontalBlock"]:last-of-type .stButton > button:focus {{
        box-shadow: none !important;
        outline: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    cols = st.columns(5)
    for i, (tab_id, icon, label) in enumerate(tabs):
        with cols[i]:
            if st.button(icon, key=f"nav_{tab_id}"):
                st.session_state.active_tab = tab_id
                st.experimental_rerun()


# =============================================================================
# MAIN APP
# =============================================================================

# v4.0: Show wizard for new users, otherwise render active tab
if st.session_state.show_wizard:
    render_wizard()
else:
    # Render active tab content
    if st.session_state.active_tab == "home":
        render_home_tab()
    elif st.session_state.active_tab == "money":
        render_money_tab()
    elif st.session_state.active_tab == "coach":
        render_coach_tab()
    elif st.session_state.active_tab == "goals":
        render_goals_tab()
    elif st.session_state.active_tab == "profile":
        render_profile_tab()

# Bottom navigation (fixed at bottom)
render_bottom_nav()
