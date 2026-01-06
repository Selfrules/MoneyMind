"""
AI Financial Coach Chat Interface
Personalized financial advice using Claude Opus 4.5 with extended thinking
"""

import streamlit as st
from pathlib import Path
import sys
import uuid
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database import (
    init_db, get_user_profile, get_debts, get_goals, get_total_debt,
    add_chat_message, get_chat_history, get_chat_sessions, delete_chat_session
)
from analytics import get_financial_snapshot
from ai.advisor import get_financial_advice, explain_concept
from styles import get_custom_css, COLORS

# Ensure database is initialized
init_db()

st.set_page_config(page_title="AI Coach - MoneyMind", page_icon="🤖", layout="wide")

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Custom CSS for chat interface
st.markdown("""
<style>
.chat-message {
    padding: 1rem;
    border-radius: 12px;
    margin-bottom: 0.75rem;
}
.chat-user {
    background: linear-gradient(135deg, #10B981 0%, #059669 100%);
    color: white;
    margin-left: 20%;
    text-align: right;
}
.chat-assistant {
    background: #1F1F1F;
    border: 1px solid #2D2D2D;
    color: #FAFAFA;
    margin-right: 20%;
}
.thinking-block {
    background: #0D1117;
    border: 1px solid #30363D;
    border-radius: 8px;
    padding: 1rem;
    margin-top: 0.5rem;
    font-size: 0.85rem;
    color: #8B949E;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_thinking" not in st.session_state:
    st.session_state.show_thinking = False

# Header
st.markdown("""
<h1 style="font-size: 2rem; font-weight: 700; color: #FAFAFA; margin-bottom: 0.5rem;">
    AI Financial Coach
</h1>
<p style="color: #71717A; margin-bottom: 1.5rem;">
    Il tuo consulente finanziario personale powered by Claude Opus 4.5
</p>
""", unsafe_allow_html=True)

# Sidebar: Financial Context & Settings
with st.sidebar:
    st.markdown("### La Tua Situazione")

    # Get current financial data for context
    profile = get_user_profile()
    debts = get_debts()
    goals = get_goals()
    month = datetime.now().strftime("%Y-%m")
    snapshot = get_financial_snapshot(month)

    # Quick stats
    monthly_income = profile.get("monthly_net_income", 0) if profile else 0
    total_debt = get_total_debt()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Reddito Mensile", f"€{monthly_income:,.0f}")
    with col2:
        st.metric("Debiti Totali", f"€{total_debt:,.0f}")

    # DTI ratio
    if monthly_income > 0:
        monthly_payments = sum(d.get("monthly_payment", 0) or 0 for d in debts)
        dti = (monthly_payments / monthly_income) * 100
        status_color = "green" if dti < 20 else ("orange" if dti < 36 else "red")
        st.markdown(f"""
        <div style="background: {COLORS['bg_secondary']}; padding: 0.75rem; border-radius: 8px; margin: 0.5rem 0;">
            <span style="color: {COLORS['text_muted']};">DTI Ratio:</span>
            <span style="color: {status_color}; font-weight: 600;"> {dti:.1f}%</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Settings
    st.markdown("### Impostazioni")
    use_extended_thinking = st.checkbox(
        "Extended Thinking",
        value=True,
        help="Usa Claude Opus 4.5 con analisi approfondita"
    )
    st.session_state.show_thinking = st.checkbox(
        "Mostra Ragionamento",
        value=st.session_state.show_thinking,
        help="Visualizza il processo di ragionamento dell'AI"
    )

    st.markdown("---")

    # Session management
    st.markdown("### Sessioni")
    if st.button("Nuova Conversazione"):
        st.session_state.session_id = str(uuid.uuid4())[:8]
        st.session_state.messages = []
        st.experimental_rerun()

    st.markdown("---")

    # Suggested questions in sidebar
    st.markdown("### Domande Suggerite")

    suggested_questions = [
        "Come ripago i debiti velocemente?",
        "Avalanche o Snowball?",
        "Come costruisco un fondo emergenza?",
        "Qual è un buon budget?",
    ]

    for i, question in enumerate(suggested_questions):
        if st.button(question, key=f"suggest_{i}"):
            st.session_state.pending_question = question
            st.experimental_rerun()


def build_financial_context() -> dict:
    """Build comprehensive financial context for AI advisor."""
    profile = get_user_profile()
    debts = get_debts()
    goals = get_goals()
    month = datetime.now().strftime("%Y-%m")
    snapshot = get_financial_snapshot(month)

    monthly_income = profile.get("monthly_net_income", 0) if profile else 0
    total_debt = get_total_debt()
    monthly_payments = sum(d.get("monthly_payment", 0) or 0 for d in debts)

    total_income = snapshot.get("total_income", monthly_income)
    total_expenses = snapshot.get("total_expenses", 0)
    net_cash_flow = total_income - total_expenses if total_income else 0
    savings_rate = (net_cash_flow / total_income * 100) if total_income > 0 else 0

    return {
        "net_worth": -total_debt,
        "total_assets": 0,
        "total_debt": total_debt,
        "month": month,
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_cash_flow": net_cash_flow,
        "savings_rate": savings_rate,
        "dti_ratio": (monthly_payments / monthly_income * 100) if monthly_income > 0 else 0,
        "emergency_fund_months": 0,
        "debts": [
            {
                "name": d["name"],
                "current_balance": d["current_balance"],
                "interest_rate": d.get("interest_rate"),
                "monthly_payment": d.get("monthly_payment")
            }
            for d in debts
        ],
        "goals": [
            {
                "name": g["name"],
                "target_amount": g["target_amount"],
                "current_amount": g.get("current_amount", 0)
            }
            for g in goals if g["status"] == "active"
        ]
    }


# Check for pending question from sidebar
if "pending_question" in st.session_state:
    pending = st.session_state.pending_question
    del st.session_state.pending_question

    st.session_state.messages.append({"role": "user", "content": pending})
    add_chat_message(st.session_state.session_id, "user", pending)

    with st.spinner("Il coach sta pensando..."):
        context = build_financial_context()
        result = get_financial_advice(
            question=pending,
            context=context,
            use_extended_thinking=use_extended_thinking
        )

    assistant_msg = {
        "role": "assistant",
        "content": result.get("advice", "Errore"),
        "thinking": result.get("thinking")
    }
    st.session_state.messages.append(assistant_msg)

    tokens = result.get("tokens_input", 0) + result.get("tokens_output", 0)
    add_chat_message(st.session_state.session_id, "assistant", result.get("advice", ""), tokens)


# Welcome message if no messages
if not st.session_state.messages:
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {COLORS['bg_secondary']} 0%, #1A1A1A 100%);
                border: 1px solid {COLORS['border']}; border-radius: 12px; padding: 2rem;
                text-align: center; margin: 2rem 0;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">👋</div>
        <h2 style="color: {COLORS['text_primary']}; margin-bottom: 0.5rem;">
            Ciao! Sono il tuo Coach Finanziario
        </h2>
        <p style="color: {COLORS['text_muted']}; max-width: 500px; margin: 0 auto;">
            Sono qui per aiutarti a raggiungere i tuoi obiettivi finanziari.
            Chiedimi qualsiasi cosa sui tuoi debiti, budget, risparmi o investimenti.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Display message history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="chat-message chat-user">
            {msg["content"]}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message chat-assistant">
            {msg["content"]}
        </div>
        """, unsafe_allow_html=True)

        # Show thinking if available and enabled
        if st.session_state.show_thinking and msg.get("thinking"):
            with st.expander("Ragionamento AI"):
                st.markdown(f"""
                <div class="thinking-block">
                    {msg["thinking"][:2000]}...
                </div>
                """, unsafe_allow_html=True)

# Chat input form
st.markdown("---")
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Scrivi la tua domanda:", key="chat_input")
    submit_button = st.form_submit_button("Invia")

if submit_button and user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    add_chat_message(st.session_state.session_id, "user", user_input)

    # Get AI response
    with st.spinner("Il coach sta pensando..."):
        context = build_financial_context()
        result = get_financial_advice(
            question=user_input,
            context=context,
            use_extended_thinking=use_extended_thinking
        )

    # Add assistant message
    assistant_msg = {
        "role": "assistant",
        "content": result.get("advice", "Mi dispiace, si è verificato un errore."),
        "thinking": result.get("thinking")
    }
    st.session_state.messages.append(assistant_msg)

    # Save to database
    tokens = result.get("tokens_input", 0) + result.get("tokens_output", 0)
    add_chat_message(
        st.session_state.session_id,
        "assistant",
        result.get("advice", ""),
        tokens
    )

    st.experimental_rerun()

# Footer
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align: center; color: {COLORS['text_muted']}; font-size: 0.75rem;">
    Powered by Claude Opus 4.5 | Session: {st.session_state.session_id}
</div>
""", unsafe_allow_html=True)
