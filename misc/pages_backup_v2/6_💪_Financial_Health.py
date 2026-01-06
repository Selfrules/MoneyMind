"""
Financial Health Dashboard v2.0 - Calm Finance Theme
Simple score + KPIs + actionable recommendations
"""

import streamlit as st
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database import get_debts, get_goals, get_user_profile, init_db
from analytics import (
    get_financial_snapshot, calculate_financial_health_score,
    get_top_spending_categories, generate_budget_recommendation
)
from styles import get_custom_css, COLORS, section_header, kpi_indicator, insight_card
from datetime import datetime

# Ensure database is initialized
init_db()

st.set_page_config(page_title="Salute Finanziaria - MoneyMind", page_icon="💪", layout="wide")

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# =============================================================================
# DATA
# =============================================================================
month = datetime.now().strftime("%Y-%m")
snapshot = get_financial_snapshot(month)
health_score = calculate_financial_health_score()
debts = get_debts(active_only=True)
goals = get_goals(status="active")
profile = get_user_profile()
budget_rec = generate_budget_recommendation()

score = health_score['total_score']
grade = health_score['grade']
description = health_score['description']

# Determine phase
has_debt = len(debts) > 0 if debts else False
phase = "Debt Payoff" if has_debt else "Wealth Building"
phase_icon = "🎯" if has_debt else "🚀"
phase_focus = "Focus: Debiti" if has_debt else "Focus: Investimenti"

# Grade styling
grade_configs = {
    'A': {'color': COLORS['income'], 'emoji': '💚', 'label': 'Eccellente'},
    'B': {'color': COLORS['accent'], 'emoji': '💙', 'label': 'Buono'},
    'C': {'color': COLORS['warning'], 'emoji': '💛', 'label': 'Discreto'},
    'D': {'color': '#F97316', 'emoji': '🧡', 'label': 'Attenzione'},
    'F': {'color': COLORS['expense'], 'emoji': '❤️', 'label': 'Critico'}
}
grade_config = grade_configs.get(grade, grade_configs['C'])

# =============================================================================
# PAGE HEADER
# =============================================================================
st.markdown(f"""
<div style="margin-bottom: 2rem;">
    <h1 style="font-size: 1.75rem; font-weight: 700; color: {COLORS['text_primary']}; margin-bottom: 0.25rem;">
        Salute Finanziaria
    </h1>
    <p style="color: {COLORS['text_muted']}; margin: 0;">
        Il tuo stato finanziario a colpo d'occhio
    </p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# SCORE + PHASE CARDS
# =============================================================================
col1, col2 = st.columns(2)

with col1:
    # Score Card
    st.markdown(f'''<div style="background: {COLORS['bg_secondary']}; border: 1px solid {COLORS['border']}; border-radius: 16px; padding: 1.5rem; text-align: center;">
<div style="font-size: 3rem; margin-bottom: 0.5rem;">{grade_config['emoji']}</div>
<div style="font-size: 0.875rem; color: {COLORS['text_muted']}; margin-bottom: 0.25rem;">Score</div>
<div style="font-size: 2.5rem; font-weight: 700; color: {grade_config['color']};">{score:.0f}<span style="font-size: 1.25rem; color: {COLORS['text_muted']};">/100</span></div>
<div style="font-size: 1rem; font-weight: 600; color: {grade_config['color']}; margin-top: 0.25rem;">"{grade_config['label']}"</div>
</div>''', unsafe_allow_html=True)

with col2:
    # Phase Card
    st.markdown(f'''<div style="background: {COLORS['bg_secondary']}; border: 1px solid {COLORS['border']}; border-radius: 16px; padding: 1.5rem;">
<div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
<span style="font-size: 1.5rem;">{phase_icon}</span>
<div>
<div style="font-size: 0.875rem; color: {COLORS['text_muted']};">Fase Attuale</div>
<div style="font-size: 1.25rem; font-weight: 700; color: {COLORS['text_primary']};">{phase}</div>
</div>
</div>
<div style="background: {COLORS['bg_tertiary']}; border-radius: 8px; padding: 0.75rem;">
<div style="color: {COLORS['text_secondary']}; font-size: 0.875rem;">{phase_focus}</div>
<div style="color: {COLORS['text_muted']}; font-size: 0.75rem; margin-top: 0.25rem;">
{'Paga prima il debito con tasso più alto' if has_debt else 'Costruisci il tuo patrimonio'}
</div>
</div>
</div>''', unsafe_allow_html=True)

# =============================================================================
# KPI INDICATORS
# =============================================================================
st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
st.markdown(section_header("I Tuoi Indicatori"), unsafe_allow_html=True)

# Get KPI values
savings_rate = snapshot.get('savings_rate') or 0
dti_ratio = snapshot.get('dti_ratio') or 0
ef_months = snapshot.get('emergency_fund_months') or 0
net_flow = snapshot.get('net_cash_flow') or 0

# Determine statuses
sr_status = "good" if savings_rate >= 20 else ("warning" if savings_rate >= 10 else "critical")
dti_status = "good" if dti_ratio < 20 else ("warning" if dti_ratio < 36 else "critical")
ef_status = "good" if ef_months >= 3 else ("warning" if ef_months >= 1 else "critical")
nf_status = "good" if net_flow >= 0 else "critical"

# Display KPIs
st.markdown(kpi_indicator(
    label="Tasso di Risparmio",
    value=f"{savings_rate:.1f}%",
    target="Obiettivo: 20%",
    status=sr_status
), unsafe_allow_html=True)

st.markdown(kpi_indicator(
    label="Rapporto Debito/Reddito (DTI)",
    value=f"{dti_ratio:.1f}%",
    target="Obiettivo: <36%",
    status=dti_status
), unsafe_allow_html=True)

st.markdown(kpi_indicator(
    label="Fondo Emergenza",
    value=f"{ef_months:.1f} mesi",
    target="Obiettivo: 3 mesi",
    status=ef_status
), unsafe_allow_html=True)

st.markdown(kpi_indicator(
    label="Flusso Netto Mensile",
    value=f"{'+'if net_flow >= 0 else ''}€{net_flow:,.0f}",
    target="Questo mese",
    status=nf_status
), unsafe_allow_html=True)

# =============================================================================
# RECOMMENDED ACTIONS
# =============================================================================
st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
st.markdown(section_header("Azioni Consigliate"), unsafe_allow_html=True)

# Generate personalized recommendations
recommendations = []

# Debt-focused recommendations
if debts:
    # Find highest rate debt
    sorted_debts = sorted(debts, key=lambda d: d.get("interest_rate", 0) or 0, reverse=True)
    top_debt = sorted_debts[0]
    top_rate = top_debt.get("interest_rate", 0) or 0

    recommendations.append({
        "icon": "💰",
        "title": f"Paga €50 extra su {top_debt['name']}",
        "message": f"Con il {top_rate:.1f}% APR, è il tuo debito più costoso. Ogni euro extra riduce gli interessi.",
        "severity": "warning"
    })

    if len(sorted_debts) > 1:
        next_debt = sorted_debts[1]
        recommendations.append({
            "icon": "📋",
            "title": f"Dopo {top_debt['name']}, concentrati su {next_debt['name']}",
            "message": "Segui la strategia Avalanche per risparmiare sugli interessi.",
            "severity": "info"
        })

# Emergency fund recommendation
if ef_months < 3:
    monthly_income = profile.get("monthly_net_income", 0) if profile else 0
    target_ef = monthly_income * 3 if monthly_income > 0 else 6000
    current_ef = ef_months * (monthly_income / 12) if monthly_income > 0 else 0
    needed = target_ef - current_ef

    if has_debt:
        recommendations.append({
            "icon": "🛡️",
            "title": "Dopo i debiti: Fondo Emergenza",
            "message": f"Obiettivo: €{target_ef:,.0f} (3 mesi di spese). Priorità dopo l'estinzione debiti.",
            "severity": "info"
        })
    else:
        recommendations.append({
            "icon": "🛡️",
            "title": "Costruisci il Fondo Emergenza",
            "message": f"Ti servono ancora €{needed:,.0f} per raggiungere 3 mesi di copertura.",
            "severity": "warning"
        })

# Savings rate recommendation
if savings_rate < 20:
    gap = 20 - savings_rate
    recommendations.append({
        "icon": "📈",
        "title": f"Aumenta il risparmio del {gap:.0f}%",
        "message": "Rivedi le spese non essenziali. Anche piccoli tagli mensili fanno la differenza.",
        "severity": "warning" if savings_rate < 10 else "info"
    })

# If no specific recommendations, add a positive one
if not recommendations:
    recommendations.append({
        "icon": "🎉",
        "title": "Ottimo lavoro!",
        "message": "I tuoi indicatori sono buoni. Continua così e considera di aumentare gli investimenti.",
        "severity": "success"
    })

# Display recommendations (max 3)
for i, rec in enumerate(recommendations[:3]):
    st.markdown(f'''<div style="background: {COLORS['bg_secondary']}; border-left: 4px solid {COLORS['accent'] if rec['severity'] == 'info' else (COLORS['warning'] if rec['severity'] == 'warning' else COLORS['income'])}; border-radius: 0 8px 8px 0; padding: 1rem; margin-bottom: 0.75rem;">
<div style="display: flex; gap: 0.75rem; align-items: flex-start;">
<span style="font-size: 1.25rem;">{rec['icon']}</span>
<div>
<div style="color: {COLORS['text_primary']}; font-weight: 600; margin-bottom: 0.25rem;">{i+1}. {rec['title']}</div>
<div style="color: {COLORS['text_secondary']}; font-size: 0.875rem;">{rec['message']}</div>
</div>
</div>
</div>''', unsafe_allow_html=True)

# =============================================================================
# MONTHLY BREAKDOWN (Simple)
# =============================================================================
st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
st.markdown(section_header("Questo Mese"), unsafe_allow_html=True)

top_spending = get_top_spending_categories(month)

if top_spending:
    st.markdown(f'<div style="background: {COLORS["bg_secondary"]}; border: 1px solid {COLORS["border"]}; border-radius: 12px; padding: 1rem;">', unsafe_allow_html=True)

    for cat in top_spending[:5]:
        bar_width = min(cat['percentage'], 100)
        st.markdown(f'''<div style="margin-bottom: 0.75rem;">
<div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem;">
<span style="color: {COLORS['text_primary']}; font-size: 0.875rem;">{cat['category_icon']} {cat['category_name']}</span>
<span style="color: {COLORS['text_secondary']}; font-size: 0.875rem;">€{cat['amount']:,.0f} ({cat['percentage']:.0f}%)</span>
</div>
<div style="background: {COLORS['bg_tertiary']}; border-radius: 4px; height: 6px;">
<div style="background: {COLORS['accent']}; height: 100%; border-radius: 4px; width: {bar_width}%;"></div>
</div>
</div>''', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown(f'''<div style="background: {COLORS['bg_secondary']}; border: 1px dashed {COLORS['border']}; border-radius: 12px; padding: 2rem; text-align: center;">
<div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
<div style="color: {COLORS['text_muted']};">Nessuna spesa registrata questo mese</div>
</div>''', unsafe_allow_html=True)

# =============================================================================
# FOOTER TIP
# =============================================================================
st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

if grade in ['D', 'F']:
    st.markdown(f'''<div style="background: {COLORS['bg_tertiary']}; border-radius: 12px; padding: 1rem; text-align: center;">
<span style="color: {COLORS['text_muted']}; font-size: 0.875rem;">
💡 <strong>Suggerimento:</strong> Non scoraggiarti! Piccoli passi costanti portano a grandi risultati.
Concentrati su una azione alla volta.
</span>
</div>''', unsafe_allow_html=True)
elif grade == 'A':
    st.markdown(f'''<div style="background: {COLORS['accent_muted']}; border-radius: 12px; padding: 1rem; text-align: center;">
<span style="color: {COLORS['text_secondary']}; font-size: 0.875rem;">
🌟 <strong>Eccellente!</strong> La tua salute finanziaria è ottima. Considera di investire di più per il futuro.
</span>
</div>''', unsafe_allow_html=True)
