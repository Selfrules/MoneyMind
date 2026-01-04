"""
MoneyMind Design System v3.0 - Warm Coral Theme
================================================
Smart Financial Coach - AI-First, Mobile-Native, Freedom-Focused
Redesigned for 2026 with Chat-First UX and Bottom Tab Navigation
"""

# =============================================================================
# COLOR PALETTE - WARM CORAL
# =============================================================================
COLORS = {
    # Backgrounds
    "bg_primary": "#0A0A0B",        # Near-black (warmer)
    "bg_secondary": "#151517",      # Card backgrounds
    "bg_tertiary": "#1E1E21",       # Elevated surfaces
    "bg_hover": "#262629",          # Hover states
    "bg_chat": "#1A1A1D",           # Chat bubbles background

    # Accent - Coral/Peach (Hero colors)
    "accent": "#FF6B6B",            # Primary coral - CTAs, highlights
    "accent_soft": "#FF8585",       # Hover state
    "accent_muted": "rgba(255, 107, 107, 0.15)",  # Background tints
    "accent_glow": "rgba(255, 107, 107, 0.3)",    # Glow effects

    # Secondary Accents
    "peach": "#FFAB91",             # Secondary warm tone
    "cream": "#FFF5EB",             # Light accent for contrast

    # Semantic
    "income": "#4ADE80",            # Green for money in
    "expense": "#FF6B6B",           # Coral for money out (matches accent)
    "success": "#4ADE80",           # Green success
    "warning": "#FBBF24",           # Amber warnings
    "danger": "#EF4444",            # Red danger
    "info": "#60A5FA",              # Blue info

    # Text
    "text_primary": "#FAFAFA",      # Headings, important
    "text_secondary": "#A3A3A3",    # Body text
    "text_muted": "#737373",        # Labels, hints
    "text_disabled": "#525252",     # Disabled states
    "text_inverse": "#0A0A0B",      # Text on light backgrounds

    # Borders
    "border": "#262629",            # Subtle borders
    "border_hover": "#3A3A3F",      # Hover state
    "divider": "#1F1F23",           # Section dividers

    # AI Chat specific
    "ai_bubble": "#FF6B6B",         # AI message background
    "user_bubble": "#262629",       # User message background

    # Progress & Tracking
    "track": "#262629",             # Progress bar background
    "progress_good": "#4ADE80",     # Good progress
    "progress_warning": "#FBBF24",  # Warning progress
    "progress_critical": "#FF6B6B", # Critical progress

    # Charts
    "chart_coral": "#FF6B6B",
    "chart_green": "#4ADE80",
    "chart_blue": "#60A5FA",
    "chart_purple": "#A78BFA",
    "chart_peach": "#FFAB91",
    "chart_amber": "#FBBF24",
    "chart_cyan": "#22D3EE",
    "chart_pink": "#F472B6",
}

# =============================================================================
# TYPOGRAPHY
# =============================================================================
TYPOGRAPHY = {
    "font_family": "'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Inter', sans-serif",
    "font_mono": "'SF Mono', 'JetBrains Mono', monospace",

    # Sizes
    "hero": "2.5rem",       # 40px - Big numbers, scores
    "h1": "1.5rem",         # 24px - Page titles
    "h2": "1.125rem",       # 18px - Section headers
    "body": "1rem",         # 16px - Body text
    "small": "0.875rem",    # 14px - Secondary text
    "caption": "0.75rem",   # 12px - Labels, hints
    "tiny": "0.625rem",     # 10px - Tab labels

    # Weights
    "light": "300",
    "regular": "400",
    "medium": "500",
    "semibold": "600",
    "bold": "700",
}

# =============================================================================
# SPACING
# =============================================================================
SPACING = {
    "xs": "0.25rem",    # 4px
    "sm": "0.5rem",     # 8px
    "md": "1rem",       # 16px
    "lg": "1.5rem",     # 24px
    "xl": "2rem",       # 32px
    "2xl": "3rem",      # 48px
    "3xl": "4rem",      # 64px
}

# =============================================================================
# BORDER RADIUS
# =============================================================================
RADIUS = {
    "sm": "8px",        # Buttons, inputs
    "md": "12px",       # Cards
    "lg": "16px",       # Modals, large containers
    "xl": "20px",       # Hero cards
    "full": "9999px",   # Pills, avatars
}

# =============================================================================
# COMPONENT FUNCTIONS
# =============================================================================

def freedom_score_card(score: int, message: str, grade: str = "C") -> str:
    """
    Main hero component showing financial freedom progress.

    Args:
        score: Score from 0-100
        message: Motivational message
        grade: Letter grade (A, B, C, D, F)
    """
    # Color based on score
    if score >= 80:
        color = COLORS["income"]
        emoji = "💚"
    elif score >= 60:
        color = COLORS["info"]
        emoji = "💙"
    elif score >= 40:
        color = COLORS["warning"]
        emoji = "💛"
    else:
        color = COLORS["accent"]
        emoji = "🧡"

    # Progress bar
    progress_width = min(100, max(0, score))

    return f'''
    <div style="
        background: linear-gradient(135deg, {COLORS['bg_secondary']} 0%, {COLORS['bg_tertiary']} 100%);
        border-radius: {RADIUS['xl']};
        padding: 1.5rem;
        text-align: center;
        margin-bottom: 1rem;
        border: 1px solid {COLORS['border']};
    ">
        <div style="font-size: 0.75rem; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.75rem;">
            🎯 Freedom Score
        </div>
        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{emoji}</div>
        <div style="
            font-size: 3rem;
            font-weight: 700;
            color: {color};
            margin-bottom: 0.25rem;
            line-height: 1;
        ">
            {score}<span style="font-size: 1.5rem; color: {COLORS['text_muted']};">/100</span>
        </div>
        <div style="
            background: {COLORS['track']};
            border-radius: {RADIUS['full']};
            height: 8px;
            margin: 1rem 0;
            overflow: hidden;
        ">
            <div style="
                background: linear-gradient(90deg, {color} 0%, {COLORS['peach']} 100%);
                height: 100%;
                width: {progress_width}%;
                border-radius: {RADIUS['full']};
                transition: width 0.5s ease;
            "></div>
        </div>
        <div style="color: {COLORS['text_secondary']}; font-size: 0.875rem; font-style: italic;">
            "{message}"
        </div>
    </div>
    '''


def chat_bubble(content: str, is_ai: bool = True, avatar: str = None) -> str:
    """
    Chat message bubble for AI Coach.

    Args:
        content: Message content (can include HTML)
        is_ai: True for AI messages, False for user messages
        avatar: Optional custom avatar emoji
    """
    if is_ai:
        avatar = avatar or "🧠"
        return f'''
        <div style="display: flex; gap: 0.75rem; margin-bottom: 1rem; align-items: flex-start;">
            <div style="
                width: 36px; height: 36px;
                background: {COLORS['accent']};
                border-radius: 50%;
                display: flex; align-items: center; justify-content: center;
                font-size: 1.125rem;
                flex-shrink: 0;
            ">{avatar}</div>
            <div style="
                background: {COLORS['bg_tertiary']};
                border-radius: 0 16px 16px 16px;
                padding: 1rem;
                max-width: 85%;
                color: {COLORS['text_primary']};
                font-size: 0.9375rem;
                line-height: 1.5;
            ">
                {content}
            </div>
        </div>
        '''
    else:
        avatar = avatar or "👤"
        return f'''
        <div style="display: flex; justify-content: flex-end; margin-bottom: 1rem;">
            <div style="
                background: {COLORS['accent']};
                border-radius: 16px 0 16px 16px;
                padding: 1rem;
                max-width: 85%;
                color: {COLORS['text_primary']};
                font-size: 0.9375rem;
                line-height: 1.5;
            ">
                {content}
            </div>
        </div>
        '''


def suggested_question(text: str, key: str = "") -> str:
    """
    Suggested question pill for Coach tab.

    Args:
        text: Question text
        key: Optional key for Streamlit button
    """
    return f'''
    <div style="
        background: {COLORS['bg_tertiary']};
        border: 1px solid {COLORS['border']};
        border-radius: {RADIUS['full']};
        padding: 0.5rem 1rem;
        color: {COLORS['text_secondary']};
        font-size: 0.875rem;
        cursor: pointer;
        display: inline-block;
        margin: 0.25rem;
        transition: all 0.2s ease;
    " onmouseover="this.style.borderColor='{COLORS['accent']}'; this.style.color='{COLORS['accent']}';"
       onmouseout="this.style.borderColor='{COLORS['border']}'; this.style.color='{COLORS['text_secondary']}';">
        {text}
    </div>
    '''


def bottom_tab_bar(active_tab: str) -> str:
    """
    Fixed bottom navigation bar.

    Args:
        active_tab: Currently active tab ID (home, money, coach, goals, profile)
    """
    tabs = [
        ("home", "🏠", "Home"),
        ("money", "💳", "Money"),
        ("coach", "💬", "Coach"),
        ("goals", "🎯", "Goals"),
        ("profile", "👤", "Profilo"),
    ]

    tabs_html = ""
    for tab_id, icon, label in tabs:
        is_active = tab_id == active_tab
        color = COLORS["accent"] if is_active else COLORS["text_muted"]
        font_weight = "600" if is_active else "400"

        tabs_html += f'''
        <div style="
            flex: 1;
            text-align: center;
            padding: 0.75rem 0;
            color: {color};
            cursor: pointer;
            transition: color 0.2s ease;
        ">
            <div style="font-size: 1.25rem; margin-bottom: 0.125rem;">{icon}</div>
            <div style="font-size: 0.625rem; font-weight: {font_weight}; letter-spacing: 0.02em;">{label}</div>
        </div>
        '''

    return f'''
    <div style="
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: {COLORS['bg_primary']};
        border-top: 1px solid {COLORS['border']};
        display: flex;
        padding-bottom: env(safe-area-inset-bottom, 0);
        z-index: 1000;
    ">
        {tabs_html}
    </div>
    '''


def transaction_row(icon: str, description: str, date: str, category: str, amount: float) -> str:
    """
    Transaction row with modern styling.

    Args:
        icon: Emoji icon for category
        description: Transaction description
        date: Date string
        category: Category name
        amount: Amount (positive = income, negative = expense)
    """
    amount_color = COLORS["income"] if amount > 0 else COLORS["expense"]
    amount_str = f"+€{amount:,.2f}" if amount > 0 else f"€{amount:,.2f}"

    return f'''
    <div style="
        display: flex;
        align-items: center;
        padding: 0.875rem 1rem;
        background: {COLORS['bg_secondary']};
        border-radius: {RADIUS['md']};
        margin-bottom: 0.5rem;
        gap: 0.875rem;
    ">
        <div style="
            width: 40px; height: 40px;
            background: {COLORS['bg_tertiary']};
            border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.25rem;
            flex-shrink: 0;
        ">{icon}</div>
        <div style="flex: 1; min-width: 0;">
            <div style="color: {COLORS['text_primary']}; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{description}</div>
            <div style="color: {COLORS['text_muted']}; font-size: 0.75rem;">{date} • {category}</div>
        </div>
        <div style="color: {amount_color}; font-weight: 600; white-space: nowrap; font-size: 0.9375rem;">{amount_str}</div>
    </div>
    '''


def metric_card(label: str, value: str, trend: str = None, trend_positive: bool = True, icon: str = None) -> str:
    """
    Compact metric card for key numbers.

    Args:
        label: Metric label
        value: Metric value
        trend: Optional trend text
        trend_positive: Whether trend is positive
        icon: Optional emoji icon
    """
    trend_html = ""
    if trend:
        trend_color = COLORS["income"] if trend_positive else COLORS["expense"]
        arrow = "↑" if trend_positive else "↓"
        trend_html = f'<div style="color: {trend_color}; font-size: 0.75rem; margin-top: 0.25rem;">{arrow} {trend}</div>'

    icon_html = f'<span style="font-size: 1.25rem; margin-right: 0.5rem;">{icon}</span>' if icon else ""

    return f'''<div style="background: {COLORS['bg_secondary']}; border: 1px solid {COLORS['border']}; border-radius: {RADIUS['md']}; padding: 1rem;">
<div style="display: flex; align-items: center;">{icon_html}<div style="color: {COLORS['text_muted']}; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em;">{label}</div></div>
<div style="color: {COLORS['text_primary']}; font-size: 1.5rem; font-weight: 700; margin-top: 0.25rem;">{value}</div>
{trend_html}</div>'''


def insight_card(icon: str, title: str, message: str, severity: str = "info", action_text: str = None) -> str:
    """
    AI insight card with optional action button.

    Args:
        icon: Emoji icon
        title: Insight title
        message: Insight message
        severity: "info", "warning", "success", or "critical"
        action_text: Optional action button text
    """
    severity_colors = {
        "info": COLORS["info"],
        "warning": COLORS["warning"],
        "success": COLORS["income"],
        "critical": COLORS["expense"]
    }
    accent = severity_colors.get(severity, COLORS["info"])

    action_html = ""
    if action_text:
        action_html = f'<div style="margin-top: 0.75rem;"><span style="background: {accent}; color: {COLORS["text_primary"]}; padding: 0.5rem 1rem; border-radius: {RADIUS["full"]}; font-size: 0.8125rem; font-weight: 500; cursor: pointer;">{action_text}</span></div>'

    return f'''<div style="background: {COLORS['bg_secondary']}; border-left: 4px solid {accent}; border-radius: 0 {RADIUS['md']} {RADIUS['md']} 0; padding: 1rem; margin-bottom: 0.75rem;">
<div style="display: flex; gap: 0.75rem; align-items: flex-start;">
<span style="font-size: 1.25rem;">{icon}</span>
<div style="flex: 1;">
<div style="color: {COLORS['text_primary']}; font-weight: 600; margin-bottom: 0.25rem;">{title}</div>
<div style="color: {COLORS['text_secondary']}; font-size: 0.875rem; line-height: 1.5;">{message}</div>
{action_html}</div></div></div>'''


def section_header(title: str, action_text: str = None) -> str:
    """
    Section header with optional action link.

    Args:
        title: Section title
        action_text: Optional action link text
    """
    action_html = f'<span style="color: {COLORS["accent"]}; font-size: 0.8125rem; cursor: pointer;">{action_text}</span>' if action_text else ""

    return f'''
    <div style="
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 1.5rem 0 0.75rem 0;
    ">
        <span style="color: {COLORS['text_muted']}; font-size: 0.6875rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em;">{title}</span>
        {action_html}
    </div>
    '''


def goal_progress_card(name: str, current: float, target: float, icon: str = "🎯",
                       subtitle: str = None, is_locked: bool = False) -> str:
    """
    Goal progress card with visual progress bar.

    Args:
        name: Goal name
        current: Current amount
        target: Target amount
        icon: Emoji icon
        subtitle: Optional subtitle (e.g., "12 mesi rimanenti")
        is_locked: Whether goal is locked (future goal)
    """
    percent = min(100, (current / target) * 100) if target > 0 else 0

    if is_locked:
        opacity = "0.5"
        border_color = COLORS["border"]
        progress_color = COLORS["text_muted"]
        status = "🔒"
    elif percent >= 100:
        opacity = "1"
        border_color = COLORS["income"]
        progress_color = COLORS["income"]
        status = "✓"
    else:
        opacity = "1"
        border_color = COLORS["accent"]
        progress_color = COLORS["accent"]
        status = f"{percent:.0f}%"

    subtitle_html = f'<div style="color: {COLORS["text_muted"]}; font-size: 0.75rem; margin-top: 0.25rem;">{subtitle}</div>' if subtitle else ""

    return f'''<div style="background: {COLORS['bg_secondary']}; border: 1px solid {border_color}; border-radius: {RADIUS['lg']}; padding: 1rem; margin-bottom: 0.75rem; opacity: {opacity};">
<div style="display: flex; align-items: flex-start; gap: 0.75rem; margin-bottom: 0.75rem;">
<span style="font-size: 1.5rem;">{icon}</span>
<div style="flex: 1;">
<div style="color: {COLORS['text_primary']}; font-weight: 600;">{name}</div>
<div style="color: {COLORS['text_secondary']}; font-size: 0.875rem;">€{current:,.0f} / €{target:,.0f}</div>
{subtitle_html}</div>
<span style="color: {border_color}; font-weight: 600; font-size: 0.875rem;">{status}</span></div>
<div style="background: {COLORS['track']}; border-radius: {RADIUS['full']}; height: 8px; overflow: hidden;">
<div style="background: linear-gradient(90deg, {progress_color} 0%, {COLORS['peach']} 100%); height: 100%; width: {percent}%; border-radius: {RADIUS['full']};"></div></div></div>'''


def kpi_indicator(label: str, value: str, target: str, status: str = "warning") -> str:
    """
    KPI indicator row with status.

    Args:
        label: KPI name
        value: Current value
        target: Target description
        status: "good", "warning", or "critical"
    """
    status_colors = {
        "good": COLORS["income"],
        "warning": COLORS["warning"],
        "critical": COLORS["expense"]
    }
    status_icons = {"good": "🟢", "warning": "🟡", "critical": "🔴"}

    color = status_colors.get(status, COLORS["warning"])
    icon = status_icons.get(status, "🟡")

    return f'''<div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 0; border-bottom: 1px solid {COLORS['divider']};">
<div><div style="color: {COLORS['text_secondary']}; font-size: 0.875rem;">{label}</div>
<div style="color: {COLORS['text_muted']}; font-size: 0.75rem;">{target}</div></div>
<div style="display: flex; align-items: center; gap: 0.75rem;">
<span style="color: {color}; font-weight: 600;">{value}</span><span>{icon}</span></div></div>'''


def phase_card(phase_name: str, phase_icon: str, focus_text: str, tip_text: str) -> str:
    """
    Current financial phase card.

    Args:
        phase_name: Phase name (e.g., "Debt Payoff")
        phase_icon: Phase emoji
        focus_text: Focus description
        tip_text: Actionable tip
    """
    return f'''<div style="background: {COLORS['bg_secondary']}; border: 1px solid {COLORS['border']}; border-radius: {RADIUS['lg']}; padding: 1rem;">
<div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.75rem;">
<span style="font-size: 1.5rem;">{phase_icon}</span>
<div><div style="font-size: 0.75rem; color: {COLORS['text_muted']}; text-transform: uppercase; letter-spacing: 0.05em;">Fase Attuale</div>
<div style="font-size: 1.125rem; font-weight: 700; color: {COLORS['text_primary']};">{phase_name}</div></div></div>
<div style="background: {COLORS['bg_tertiary']}; border-radius: {RADIUS['sm']}; padding: 0.75rem;">
<div style="color: {COLORS['text_secondary']}; font-size: 0.875rem;">{focus_text}</div>
<div style="color: {COLORS['text_muted']}; font-size: 0.75rem; margin-top: 0.25rem;">{tip_text}</div></div></div>'''


def quick_action_button(icon: str, label: str) -> str:
    """
    Quick action button for Home tab.

    Args:
        icon: Button icon
        label: Button label
    """
    return f'''
    <div style="
        background: {COLORS['bg_tertiary']};
        border: 1px solid {COLORS['border']};
        border-radius: {RADIUS['md']};
        padding: 0.875rem 1rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        cursor: pointer;
        transition: all 0.2s ease;
    " onmouseover="this.style.borderColor='{COLORS['accent']}';"
       onmouseout="this.style.borderColor='{COLORS['border']}';">
        <span style="font-size: 1.25rem;">{icon}</span>
        <span style="color: {COLORS['text_secondary']}; font-size: 0.875rem; font-weight: 500;">{label}</span>
    </div>
    '''


def debt_card(name: str, balance: float, original: float, rate: float = None,
              monthly: float = None, is_priority: bool = False) -> str:
    """
    Debt progress card.

    Args:
        name: Debt name
        balance: Current balance
        original: Original amount
        rate: Interest rate APR
        monthly: Monthly payment
        is_priority: Whether this is the priority debt
    """
    percent = max(0, min(100, ((original - balance) / original) * 100)) if original > 0 else 0

    priority_html = f'<span style="color: {COLORS["warning"]}; font-size: 0.6875rem; font-weight: 600; text-transform: uppercase;">→ PROSSIMO</span>' if is_priority else ""
    rate_html = f'<span style="color: {COLORS["text_muted"]}; font-size: 0.8125rem;">{rate}% APR</span>' if rate else ""
    monthly_html = f'<span style="color: {COLORS["text_muted"]}; font-size: 0.75rem;">€{monthly:,.0f}/mese</span>' if monthly else ""

    return f'''<div style="background: {COLORS['bg_secondary']}; border: 1px solid {COLORS['accent'] if is_priority else COLORS['border']}; border-radius: {RADIUS['md']}; padding: 1rem; margin-bottom: 0.75rem;">
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
<div><div style="color: {COLORS['text_primary']}; font-weight: 600;">{name}</div>{priority_html}</div>{rate_html}</div>
<div style="margin-bottom: 0.5rem;"><span style="color: {COLORS['text_primary']}; font-size: 1.375rem; font-weight: 700;">€{balance:,.0f}</span><span style="color: {COLORS['text_muted']};"> / €{original:,.0f}</span></div>
<div style="background: {COLORS['track']}; border-radius: {RADIUS['full']}; height: 6px; margin-bottom: 0.5rem; overflow: hidden;">
<div style="background: linear-gradient(90deg, {COLORS['accent']} 0%, {COLORS['income']} 100%); height: 100%; width: {percent}%; border-radius: {RADIUS['full']};"></div></div>
<div style="display: flex; justify-content: space-between; align-items: center;">{monthly_html}<span style="color: {COLORS['income']}; font-size: 0.75rem; font-weight: 500;">{percent:.0f}% pagato</span></div></div>'''


def timeline_item(date: str, label: str, is_completed: bool = False, is_current: bool = False) -> str:
    """
    Timeline item for debt journey.

    Args:
        date: Date string
        label: Event label
        is_completed: Whether event is completed
        is_current: Whether this is the current event
    """
    if is_completed:
        dot_color = COLORS["income"]
        icon = "✓"
        text_color = COLORS["text_secondary"]
    elif is_current:
        dot_color = COLORS["accent"]
        icon = "→"
        text_color = COLORS["text_primary"]
    else:
        dot_color = COLORS["text_muted"]
        icon = "○"
        text_color = COLORS["text_muted"]

    return f'''
    <div style="display: flex; align-items: center; gap: 0.75rem; padding: 0.5rem 0;">
        <span style="color: {dot_color}; font-weight: 600;">{icon}</span>
        <span style="color: {COLORS['text_muted']}; font-size: 0.8125rem; width: 80px;">{date}</span>
        <span style="color: {text_color}; font-size: 0.875rem;">{label}</span>
    </div>
    '''


def profile_header(name: str, income: float, phase: str) -> str:
    """
    Profile header card.

    Args:
        name: User name
        income: Monthly income
        phase: Current financial phase
    """
    return f'''
    <div style="
        background: linear-gradient(135deg, {COLORS['bg_secondary']} 0%, {COLORS['bg_tertiary']} 100%);
        border-radius: {RADIUS['lg']};
        padding: 1.25rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
    ">
        <div style="
            width: 56px; height: 56px;
            background: {COLORS['accent']};
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.5rem;
        ">👤</div>
        <div>
            <div style="color: {COLORS['text_primary']}; font-size: 1.25rem; font-weight: 700;">{name}</div>
            <div style="color: {COLORS['text_muted']}; font-size: 0.875rem;">€{income:,.0f}/mese • {phase}</div>
        </div>
    </div>
    '''


def action_row(icon: str, label: str, description: str = None) -> str:
    """
    Clickable action row for settings/profile.

    Args:
        icon: Action icon
        label: Action label
        description: Optional description
    """
    desc_html = f'<div style="color: {COLORS["text_muted"]}; font-size: 0.75rem;">{description}</div>' if description else ""

    return f'''
    <div style="
        display: flex;
        align-items: center;
        padding: 1rem;
        background: {COLORS['bg_secondary']};
        border-radius: {RADIUS['md']};
        margin-bottom: 0.5rem;
        cursor: pointer;
        transition: all 0.2s ease;
        gap: 1rem;
    " onmouseover="this.style.background='{COLORS['bg_tertiary']}';"
       onmouseout="this.style.background='{COLORS['bg_secondary']}';">
        <span style="font-size: 1.25rem;">{icon}</span>
        <div style="flex: 1;">
            <div style="color: {COLORS['text_primary']}; font-weight: 500;">{label}</div>
            {desc_html}
        </div>
        <span style="color: {COLORS['text_muted']};">→</span>
    </div>
    '''


def sub_tab(label: str, is_active: bool = False) -> str:
    """
    Sub-tab button for Money tab.

    Args:
        label: Tab label
        is_active: Whether tab is active
    """
    if is_active:
        bg = COLORS["accent"]
        color = COLORS["text_primary"]
    else:
        bg = COLORS["bg_tertiary"]
        color = COLORS["text_muted"]

    return f'''
    <div style="
        background: {bg};
        color: {color};
        padding: 0.5rem 1rem;
        border-radius: {RADIUS['full']};
        font-size: 0.8125rem;
        font-weight: 500;
        cursor: pointer;
        display: inline-block;
        margin-right: 0.5rem;
    ">{label}</div>
    '''


# =============================================================================
# MAIN CSS FUNCTION
# =============================================================================

def get_custom_css() -> str:
    """Return the complete custom CSS for the MoneyMind v3.0 app."""
    return f"""
<style>
    /* ===== IMPORTS ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ===== ROOT VARIABLES ===== */
    :root {{
        --bg-primary: {COLORS['bg_primary']};
        --bg-secondary: {COLORS['bg_secondary']};
        --bg-tertiary: {COLORS['bg_tertiary']};
        --text-primary: {COLORS['text_primary']};
        --text-secondary: {COLORS['text_secondary']};
        --text-muted: {COLORS['text_muted']};
        --accent: {COLORS['accent']};
        --accent-soft: {COLORS['accent_soft']};
        --border: {COLORS['border']};
        --income: {COLORS['income']};
        --expense: {COLORS['expense']};
    }}

    /* ===== GLOBAL STYLES ===== */
    .stApp {{
        background-color: var(--bg-primary) !important;
        color: var(--text-primary);
        font-family: {TYPOGRAPHY['font_family']};
    }}

    /* Hide Streamlit elements */
    #MainMenu, footer, header {{
        visibility: hidden !important;
    }}

    /* Hide sidebar completely */
    [data-testid="stSidebar"] {{
        display: none !important;
    }}

    /* Hide sidebar button */
    [data-testid="collapsedControl"] {{
        display: none !important;
    }}

    /* Main content padding for bottom nav */
    .main > div {{
        padding-bottom: 100px !important;
    }}

    /* Block container max-width for mobile feel */
    .block-container {{
        max-width: 480px !important;
        padding: 1rem 1rem 7rem 1rem !important;
    }}

    /* Add spacing between elements */
    .element-container {{
        margin-bottom: 0.75rem !important;
    }}

    /* Add spacing between stacked markdown elements */
    .stMarkdown {{
        margin-bottom: 0.5rem !important;
    }}

    /* ===== TYPOGRAPHY ===== */
    h1, h2, h3, h4, h5, h6 {{
        font-family: {TYPOGRAPHY['font_family']};
        font-weight: 600;
        color: var(--text-primary);
        letter-spacing: -0.02em;
    }}

    h1 {{ font-size: 1.5rem; font-weight: 700; }}
    h2 {{ font-size: 1.125rem; }}
    h3 {{ font-size: 1rem; }}

    /* ===== BUTTONS ===== */
    .stButton > button {{
        background: var(--accent) !important;
        color: {COLORS['text_primary']} !important;
        border: none !important;
        border-radius: {RADIUS['full']} !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        font-size: 0.8125rem !important;
        font-family: {TYPOGRAPHY['font_family']} !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
    }}

    .stButton > button:hover {{
        background: var(--accent-soft) !important;
        transform: translateY(-1px);
    }}

    /* Secondary buttons */
    .stButton > button[kind="secondary"] {{
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border) !important;
    }}

    /* ===== BOTTOM NAVIGATION BUTTONS ===== */
    /* Target the last horizontal block (nav bar) */
    .main .block-container > div:last-child .stButton > button,
    .element-container:has(+ .element-container:last-child) .stButton > button {{
        background: transparent !important;
        color: var(--text-muted) !important;
        padding: 0.25rem 0.5rem !important;
        font-size: 0.6875rem !important;
        font-weight: 400 !important;
        min-height: auto !important;
        height: auto !important;
        line-height: 1.2 !important;
        border-radius: {RADIUS['sm']} !important;
    }}

    /* Make nav columns tighter */
    [data-testid="column"] .stButton > button {{
        width: 100% !important;
        white-space: nowrap !important;
    }}

    /* ===== INPUTS ===== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {{
        background-color: var(--bg-tertiary) !important;
        border: 1px solid var(--border) !important;
        border-radius: {RADIUS['md']} !important;
        color: var(--text-primary) !important;
        font-family: {TYPOGRAPHY['font_family']} !important;
    }}

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px {COLORS['accent_muted']} !important;
    }}

    /* ===== SELECT ===== */
    .stSelectbox > div > div {{
        background-color: var(--bg-tertiary) !important;
        border: 1px solid var(--border) !important;
        border-radius: {RADIUS['md']} !important;
    }}

    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: transparent !important;
        gap: 0.25rem !important;
    }}

    .stTabs [data-baseweb="tab"] {{
        background-color: var(--bg-tertiary) !important;
        color: var(--text-muted) !important;
        border-radius: {RADIUS['full']} !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: var(--accent) !important;
        color: var(--text-primary) !important;
    }}

    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] {{
        display: none !important;
    }}

    /* ===== FILE UPLOADER ===== */
    [data-testid="stFileUploader"] {{
        background: var(--bg-secondary) !important;
        border: 2px dashed var(--border) !important;
        border-radius: {RADIUS['lg']} !important;
        padding: 1.5rem !important;
    }}

    [data-testid="stFileUploader"]:hover {{
        border-color: var(--accent) !important;
    }}

    /* ===== CHAT INPUT ===== */
    [data-testid="stChatInput"] {{
        background-color: var(--bg-tertiary) !important;
        border-radius: {RADIUS['full']} !important;
    }}

    [data-testid="stChatInput"] input {{
        background-color: transparent !important;
    }}

    /* ===== DIVIDERS ===== */
    hr {{
        border: none !important;
        border-top: 1px solid var(--border) !important;
        margin: 1rem 0 !important;
    }}

    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: var(--bg-primary); }}
    ::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 3px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: var(--text-muted); }}

    /* ===== METRICS (native Streamlit) ===== */
    [data-testid="stMetric"] {{
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border) !important;
        border-radius: {RADIUS['md']} !important;
        padding: 1rem !important;
    }}

    [data-testid="stMetricLabel"] {{
        color: var(--text-muted) !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
    }}

    [data-testid="stMetricValue"] {{
        color: var(--text-primary) !important;
        font-weight: 700 !important;
    }}

    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {{
        background-color: var(--bg-secondary) !important;
        border: 1px solid var(--border) !important;
        border-radius: {RADIUS['md']} !important;
        color: var(--text-primary) !important;
    }}

    /* ===== ANIMATIONS ===== */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    .animate-fade-in {{
        animation: fadeIn 0.3s ease forwards;
    }}

    /* ===== RADIO BUTTONS (for tabs) ===== */
    .stRadio > div {{
        flex-direction: row !important;
        gap: 0.5rem !important;
    }}

    .stRadio > div > label {{
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border) !important;
        border-radius: {RADIUS['full']} !important;
        padding: 0.5rem 1rem !important;
        margin: 0 !important;
        color: var(--text-muted) !important;
        font-size: 0.875rem !important;
        cursor: pointer !important;
    }}

    .stRadio > div > label[data-checked="true"] {{
        background: var(--accent) !important;
        border-color: var(--accent) !important;
        color: var(--text-primary) !important;
    }}

    .stRadio > div > label > div:first-child {{
        display: none !important;
    }}

    /* ===== PROGRESS BARS ===== */
    .stProgress > div > div {{
        background-color: var(--bg-tertiary) !important;
        border-radius: {RADIUS['full']} !important;
    }}

    .stProgress > div > div > div {{
        background: linear-gradient(90deg, var(--accent) 0%, {COLORS['peach']} 100%) !important;
        border-radius: {RADIUS['full']} !important;
    }}

    /* ===== CHAT MESSAGE ===== */
    [data-testid="stChatMessage"] {{
        background: var(--bg-secondary) !important;
        border-radius: {RADIUS['lg']} !important;
        padding: 1rem !important;
    }}
</style>
"""


def get_plotly_theme() -> dict:
    """Return Plotly theme configuration for MoneyMind v3.0."""
    return {
        "template": "plotly_dark",
        "layout": {
            "paper_bgcolor": COLORS["bg_secondary"],
            "plot_bgcolor": COLORS["bg_secondary"],
            "font": {
                "family": TYPOGRAPHY["font_family"],
                "color": COLORS["text_secondary"],
            },
            "title": {
                "font": {
                    "color": COLORS["text_primary"],
                    "size": 16,
                }
            },
            "xaxis": {
                "gridcolor": COLORS["border"],
                "linecolor": COLORS["border"],
                "tickfont": {"color": COLORS["text_muted"]},
            },
            "yaxis": {
                "gridcolor": COLORS["border"],
                "linecolor": COLORS["border"],
                "tickfont": {"color": COLORS["text_muted"]},
            },
            "legend": {
                "font": {"color": COLORS["text_secondary"]},
                "bgcolor": "rgba(0,0,0,0)",
            },
            "margin": {"l": 40, "r": 20, "t": 40, "b": 40},
        },
        "colors": [
            COLORS["chart_coral"],
            COLORS["chart_green"],
            COLORS["chart_blue"],
            COLORS["chart_purple"],
            COLORS["chart_peach"],
            COLORS["chart_amber"],
            COLORS["chart_cyan"],
            COLORS["chart_pink"],
        ],
    }


# =============================================================================
# LEGACY COMPATIBILITY (keeping old function signatures for imports)
# =============================================================================

# Legacy aliases
FONTS = {
    "heading": TYPOGRAPHY["font_family"],
    "body": TYPOGRAPHY["font_family"],
    "mono": TYPOGRAPHY["font_mono"],
}

def budget_row(category: str, icon: str, spent: float, budget: float) -> str:
    """Legacy function - redirects to goal_progress_card."""
    percent = min(100, (spent / budget) * 100) if budget > 0 else 0

    if percent >= 100:
        status_color = COLORS["expense"]
        status_icon = "🔴"
    elif percent >= 75:
        status_color = COLORS["warning"]
        status_icon = "🟡"
    else:
        status_color = COLORS["income"]
        status_icon = "🟢"

    return f'''
    <div style="
        background: {COLORS['bg_secondary']};
        border: 1px solid {COLORS['border']};
        border-radius: {RADIUS['md']};
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span>{icon}</span>
                <span style="color: {COLORS['text_primary']}; font-weight: 500;">{category}</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="color: {COLORS['text_secondary']}; font-size: 0.875rem;">€{spent:,.0f} / €{budget:,.0f}</span>
                <span style="font-size: 0.75rem;">{status_icon}</span>
            </div>
        </div>
        <div style="
            background: {COLORS['track']};
            border-radius: {RADIUS['full']};
            height: 6px;
            overflow: hidden;
        ">
            <div style="
                background: {status_color};
                height: 100%;
                width: {min(100, percent)}%;
                border-radius: {RADIUS['full']};
            "></div>
        </div>
    </div>
    '''


def goal_card(name: str, current: float, target: float, icon: str = "🎯", status: str = "active") -> str:
    """Legacy function - redirects to goal_progress_card."""
    is_locked = status == "locked"
    return goal_progress_card(name, current, target, icon, is_locked=is_locked)


def chat_message(content: str, role: str = "assistant", avatar: str = None) -> str:
    """Legacy function - redirects to chat_bubble."""
    is_ai = role == "assistant"
    return chat_bubble(content, is_ai=is_ai, avatar=avatar)


# =============================================================================
# MONEYMIND v4.0 DIRECTIVE UI COMPONENTS
# =============================================================================

def plan_vs_actual_card(current_savings: float, baseline_savings: float,
                        on_track_status: str, status_message: str) -> str:
    """
    Card showing comparison vs baseline and debt plan status.

    Args:
        current_savings: Current month savings
        baseline_savings: 3-month average savings
        on_track_status: "on_track", "behind", "ahead", "no_plan"
        status_message: Status message to display
    """
    delta = current_savings - baseline_savings
    is_better = delta >= 0

    # Delta styling
    if is_better:
        delta_color = COLORS["income"]
        delta_icon = "+"
        delta_emoji = "📈"
    else:
        delta_color = COLORS["expense"]
        delta_icon = ""
        delta_emoji = "📉"

    # Status styling
    status_config = {
        "on_track": {"color": COLORS["income"], "icon": "✅", "label": "On Track"},
        "ahead": {"color": COLORS["income"], "icon": "🚀", "label": "Avanti"},
        "behind": {"color": COLORS["warning"], "icon": "⚠️", "label": "In Ritardo"},
        "no_plan": {"color": COLORS["text_muted"], "icon": "📋", "label": "Nessun Piano"},
        "planned": {"color": COLORS["info"], "icon": "📅", "label": "Pianificato"},
    }
    status = status_config.get(on_track_status, status_config["no_plan"])

    return f'''
    <div style="
        display: flex;
        gap: 0.75rem;
        margin-bottom: 1rem;
    ">
        <!-- Savings vs Baseline -->
        <div style="
            flex: 1;
            background: {COLORS['bg_secondary']};
            border: 1px solid {COLORS['border']};
            border-radius: {RADIUS['lg']};
            padding: 1rem;
            text-align: center;
        ">
            <div style="font-size: 1.25rem; margin-bottom: 0.25rem;">{delta_emoji}</div>
            <div style="
                font-size: 1.5rem;
                font-weight: 700;
                color: {delta_color};
            ">{delta_icon}€{abs(delta):,.0f}</div>
            <div style="
                font-size: 0.6875rem;
                color: {COLORS['text_muted']};
                text-transform: uppercase;
                letter-spacing: 0.05em;
            ">vs media 3 mesi</div>
        </div>

        <!-- Debt Plan Status -->
        <div style="
            flex: 1;
            background: {COLORS['bg_secondary']};
            border: 1px solid {COLORS['border']};
            border-radius: {RADIUS['lg']};
            padding: 1rem;
            text-align: center;
        ">
            <div style="font-size: 1.25rem; margin-bottom: 0.25rem;">{status['icon']}</div>
            <div style="
                font-size: 1rem;
                font-weight: 600;
                color: {status['color']};
            ">{status['label']}</div>
            <div style="
                font-size: 0.6875rem;
                color: {COLORS['text_muted']};
                margin-top: 0.25rem;
            ">{status_message}</div>
        </div>
    </div>
    '''


def daily_action_task(title: str, description: str, impact_text: str,
                      is_completed: bool = False, priority: int = 1,
                      action_type: str = "generic") -> str:
    """
    Daily action task component with checkbox styling.

    Args:
        title: Action title
        description: Action description
        impact_text: Impact badge text (e.g., "Risparmia €15/mese")
        is_completed: Whether task is completed
        priority: Priority level (1=highest)
        action_type: Type of action for icon selection
    """
    # Icon based on action type
    action_icons = {
        "review_subscription": "📱",
        "increase_payment": "💳",
        "cut_category": "✂️",
        "confirm_budget": "📊",
        "check_progress": "📈",
        "generic": "📌",
    }
    icon = action_icons.get(action_type, "📌")

    # Priority indicator
    priority_colors = {
        1: COLORS["expense"],
        2: COLORS["warning"],
        3: COLORS["info"],
    }
    priority_color = priority_colors.get(priority, COLORS["text_muted"])

    # Completed state
    if is_completed:
        opacity = "0.6"
        checkbox = "☑"
        checkbox_color = COLORS["income"]
        title_style = "text-decoration: line-through;"
    else:
        opacity = "1"
        checkbox = "☐"
        checkbox_color = COLORS["text_muted"]
        title_style = ""

    # Build complete single-line HTML to avoid Streamlit code block rendering
    return f'<div style="background:{COLORS["bg_secondary"]};border:1px solid {COLORS["border"]};border-left:3px solid {priority_color};border-radius:0 {RADIUS["md"]} {RADIUS["md"]} 0;padding:0.875rem 1rem;margin-bottom:0.5rem;opacity:{opacity};display:flex;align-items:flex-start;gap:0.75rem"><span style="font-size:1.25rem;color:{checkbox_color};cursor:pointer">{checkbox}</span><div style="flex:1"><div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.25rem"><span>{icon}</span><span style="color:{COLORS["text_primary"]};font-weight:500;{title_style}">{title}</span></div><div style="color:{COLORS["text_muted"]};font-size:0.8125rem;margin-bottom:0.5rem">{description}</div><div style="display:inline-block;background:{COLORS["accent_muted"]};color:{COLORS["accent"]};padding:0.25rem 0.5rem;border-radius:{RADIUS["full"]};font-size:0.6875rem;font-weight:600">{impact_text}</div></div></div>'


def scenario_comparison_mini(current_payoff_date: str, moneymind_payoff_date: str,
                             months_saved: int) -> str:
    """
    Mini comparison showing current vs MoneyMind scenario.

    Args:
        current_payoff_date: Current projected payoff date (e.g., "Apr 2027")
        moneymind_payoff_date: MoneyMind optimized date (e.g., "Nov 2026")
        months_saved: Number of months saved
    """
    # Complete single-line HTML to avoid Streamlit code block rendering
    return f'<div style="background:linear-gradient(135deg,{COLORS["bg_secondary"]} 0%,{COLORS["bg_tertiary"]} 100%);border:1px solid {COLORS["border"]};border-radius:{RADIUS["lg"]};padding:1rem;margin-bottom:1rem"><div style="font-size:0.6875rem;color:{COLORS["text_muted"]};text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.75rem">📈 Confronto Scenario</div><div style="display:flex;gap:1rem;align-items:center"><div style="flex:1"><div style="color:{COLORS["text_muted"]};font-size:0.75rem;margin-bottom:0.25rem">Oggi</div><div style="color:{COLORS["text_secondary"]};font-size:0.875rem">Debt-free</div><div style="color:{COLORS["text_primary"]};font-weight:600">{current_payoff_date}</div></div><div style="color:{COLORS["accent"]};font-size:1.25rem">→</div><div style="flex:1"><div style="color:{COLORS["accent"]};font-size:0.75rem;margin-bottom:0.25rem">Con MoneyMind</div><div style="color:{COLORS["text_secondary"]};font-size:0.875rem">Debt-free</div><div style="color:{COLORS["income"]};font-weight:700">{moneymind_payoff_date}</div></div><div style="background:{COLORS["accent_muted"]};color:{COLORS["accent"]};padding:0.5rem 0.75rem;border-radius:{RADIUS["md"]};text-align:center"><div style="font-size:1.125rem;font-weight:700">-{months_saved}</div><div style="font-size:0.6875rem">mesi</div></div></div></div>'


def action_impact_badge(impact_monthly: float = None, impact_days: int = None) -> str:
    """
    Badge showing action impact.

    Args:
        impact_monthly: Monthly savings in euros
        impact_days: Days earlier debt-free
    """
    parts = []
    if impact_monthly and impact_monthly > 0:
        parts.append(f"€{impact_monthly:.0f}/mese")
    if impact_days and impact_days > 0:
        parts.append(f"{impact_days} giorni prima")

    text = " | ".join(parts) if parts else "Migliora le finanze"

    return f'''
    <span style="
        display: inline-block;
        background: {COLORS['accent_muted']};
        color: {COLORS['accent']};
        padding: 0.25rem 0.75rem;
        border-radius: {RADIUS['full']};
        font-size: 0.75rem;
        font-weight: 600;
    ">{text}</span>
    '''


def decision_confirmation_card(title: str, description: str,
                               impact_monthly: float, impact_days: int) -> str:
    """
    Card for confirming a decision/action.

    Args:
        title: Decision title
        description: Decision description
        impact_monthly: Monthly impact in euros
        impact_days: Days impact on payoff
    """
    return f'''
    <div style="
        background: {COLORS['bg_secondary']};
        border: 2px solid {COLORS['accent']};
        border-radius: {RADIUS['lg']};
        padding: 1.25rem;
        margin-bottom: 1rem;
    ">
        <div style="
            font-size: 0.75rem;
            color: {COLORS['accent']};
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        ">🎯 Conferma Azione</div>

        <div style="
            color: {COLORS['text_primary']};
            font-size: 1.125rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        ">{title}</div>

        <div style="
            color: {COLORS['text_secondary']};
            font-size: 0.875rem;
            margin-bottom: 1rem;
            line-height: 1.5;
        ">{description}</div>

        <!-- Impact Summary -->
        <div style="
            background: {COLORS['bg_tertiary']};
            border-radius: {RADIUS['md']};
            padding: 0.75rem;
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
        ">
            <div style="flex: 1; text-align: center;">
                <div style="color: {COLORS['income']}; font-weight: 700; font-size: 1.125rem;">
                    €{impact_monthly:.0f}
                </div>
                <div style="color: {COLORS['text_muted']}; font-size: 0.6875rem;">
                    al mese
                </div>
            </div>
            <div style="
                width: 1px;
                background: {COLORS['border']};
            "></div>
            <div style="flex: 1; text-align: center;">
                <div style="color: {COLORS['income']}; font-weight: 700; font-size: 1.125rem;">
                    {impact_days}
                </div>
                <div style="color: {COLORS['text_muted']}; font-size: 0.6875rem;">
                    giorni prima
                </div>
            </div>
        </div>

        <!-- Action Buttons Info -->
        <div style="
            color: {COLORS['text_muted']};
            font-size: 0.75rem;
            text-align: center;
        ">Usa i pulsanti sotto per confermare o rimandare</div>
    </div>
    '''


def recurring_expense_card(provider: str, amount: float, category: str,
                           trend_percent: float, optimization_potential: str,
                           suggestion: str = None) -> str:
    """
    Card showing a recurring expense with optimization suggestion.

    Args:
        provider: Provider name
        amount: Monthly amount
        category: Category name
        trend_percent: 6-month trend (positive = increasing)
        optimization_potential: "none", "low", "medium", "high"
        suggestion: Optimization suggestion text
    """
    # Trend display
    if trend_percent > 5:
        trend_color = COLORS["expense"]
        trend_icon = "📈"
        trend_text = f"+{trend_percent:.0f}%"
    elif trend_percent < -5:
        trend_color = COLORS["income"]
        trend_icon = "📉"
        trend_text = f"{trend_percent:.0f}%"
    else:
        trend_color = COLORS["text_muted"]
        trend_icon = "→"
        trend_text = "Stabile"

    # Potential badge
    potential_config = {
        "high": {"color": COLORS["income"], "text": "Alto"},
        "medium": {"color": COLORS["warning"], "text": "Medio"},
        "low": {"color": COLORS["info"], "text": "Basso"},
        "none": {"color": COLORS["text_muted"], "text": "—"},
    }
    potential = potential_config.get(optimization_potential, potential_config["none"])

    # Suggestion section
    suggestion_html = ""
    if suggestion and optimization_potential != "none":
        suggestion_html = f'''
        <div style="
            background: {COLORS['accent_muted']};
            border-radius: {RADIUS['sm']};
            padding: 0.5rem 0.75rem;
            margin-top: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        ">
            <span>💡</span>
            <span style="color: {COLORS['accent']}; font-size: 0.8125rem;">{suggestion}</span>
        </div>
        '''

    return f'''
    <div style="
        background: {COLORS['bg_secondary']};
        border: 1px solid {COLORS['border']};
        border-radius: {RADIUS['md']};
        padding: 1rem;
        margin-bottom: 0.75rem;
    ">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <div style="
                    color: {COLORS['text_primary']};
                    font-weight: 600;
                    margin-bottom: 0.125rem;
                ">{provider}</div>
                <div style="
                    color: {COLORS['text_muted']};
                    font-size: 0.75rem;
                ">{category}</div>
            </div>
            <div style="text-align: right;">
                <div style="
                    color: {COLORS['text_primary']};
                    font-weight: 700;
                    font-size: 1.125rem;
                ">€{amount:.0f}</div>
                <div style="
                    color: {COLORS['text_muted']};
                    font-size: 0.6875rem;
                ">/mese</div>
            </div>
        </div>

        <div style="
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 0.75rem;
            padding-top: 0.75rem;
            border-top: 1px solid {COLORS['divider']};
        ">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span>{trend_icon}</span>
                <span style="color: {trend_color}; font-size: 0.8125rem;">{trend_text} vs 6 mesi fa</span>
            </div>
            <div style="
                background: {potential['color']}20;
                color: {potential['color']};
                padding: 0.25rem 0.5rem;
                border-radius: {RADIUS['full']};
                font-size: 0.6875rem;
                font-weight: 600;
            ">Potenziale: {potential['text']}</div>
        </div>

        {suggestion_html}
    </div>
    '''


def home_greeting(name: str, pending_actions: int = 0) -> str:
    """
    Home tab greeting with action badge.

    Args:
        name: User name
        pending_actions: Number of pending actions
    """
    # Time-based greeting
    from datetime import datetime
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Buongiorno"
        emoji = "☀️"
    elif hour < 18:
        greeting = "Buon pomeriggio"
        emoji = "🌤️"
    else:
        greeting = "Buonasera"
        emoji = "🌙"

    # Build badge directly in string - no variable interpolation
    if pending_actions > 0:
        badge = f'<div style="background:{COLORS["accent"]};color:{COLORS["text_primary"]};min-width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:700;padding:0 6px">{pending_actions}</div>'
    else:
        badge = ''

    # Complete single-line HTML - no nested variable interpolation
    return f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem"><div><div style="color:{COLORS["text_primary"]};font-size:1.25rem;font-weight:700">{emoji} {greeting}, {name}!</div><div style="color:{COLORS["text_muted"]};font-size:0.875rem">Il tuo percorso verso la libertà finanziaria</div></div>{badge}</div>'


def impact_story_card(title: str, months_ago: int, expected_savings: float,
                      actual_savings: float, is_verified: bool = False) -> str:
    """
    Card showing impact of a past decision.

    Args:
        title: Decision title
        months_ago: How many months ago
        expected_savings: Expected monthly savings
        actual_savings: Actual realized savings (total)
        is_verified: Whether impact has been verified
    """
    if is_verified:
        status_icon = "✅"
        status_text = "Verificato"
        status_color = COLORS["income"]
    else:
        status_icon = "⏳"
        status_text = "In verifica"
        status_color = COLORS["warning"]

    accuracy = (actual_savings / (expected_savings * months_ago)) * 100 if expected_savings > 0 and months_ago > 0 else 0

    return f'''
    <div style="
        background: {COLORS['bg_secondary']};
        border: 1px solid {COLORS['border']};
        border-radius: {RADIUS['md']};
        padding: 1rem;
        margin-bottom: 0.75rem;
    ">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem;">
            <div>
                <div style="
                    color: {COLORS['text_primary']};
                    font-weight: 600;
                ">{status_icon} {title}</div>
                <div style="
                    color: {COLORS['text_muted']};
                    font-size: 0.75rem;
                ">{months_ago} mesi fa</div>
            </div>
            <div style="
                color: {status_color};
                font-size: 0.6875rem;
                font-weight: 600;
            ">{status_text}</div>
        </div>

        <div style="
            background: {COLORS['bg_tertiary']};
            border-radius: {RADIUS['sm']};
            padding: 0.75rem;
            display: flex;
            justify-content: space-between;
        ">
            <div>
                <div style="color: {COLORS['text_muted']}; font-size: 0.6875rem;">Risparmiato</div>
                <div style="color: {COLORS['income']}; font-weight: 700;">€{actual_savings:.0f}</div>
            </div>
            <div style="text-align: right;">
                <div style="color: {COLORS['text_muted']}; font-size: 0.6875rem;">Accuratezza</div>
                <div style="color: {COLORS['text_secondary']}; font-weight: 600;">{accuracy:.0f}%</div>
            </div>
        </div>
    </div>
    '''


def daily_actions_header(date_str: str, pending_count: int, completed_count: int) -> str:
    """
    Header for daily actions section.

    Args:
        date_str: Date string (e.g., "Oggi, 4 Gen")
        pending_count: Number of pending actions
        completed_count: Number of completed actions
    """
    total = pending_count + completed_count
    progress = (completed_count / total * 100) if total > 0 else 0

    # Complete single-line HTML - no variable interpolation or newlines
    return f'<div style="background:{COLORS["bg_secondary"]};border:1px solid {COLORS["border"]};border-radius:{RADIUS["lg"]};padding:1rem;margin-bottom:0.75rem"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.75rem"><div style="color:{COLORS["text_primary"]};font-weight:600">📅 {date_str}</div><div style="color:{COLORS["text_muted"]};font-size:0.8125rem">{completed_count}/{total} completate</div></div><div style="background:{COLORS["track"]};border-radius:{RADIUS["full"]};height:6px;overflow:hidden"><div style="background:{COLORS["income"]};height:100%;width:{progress}%;border-radius:{RADIUS["full"]};transition:width 0.3s ease"></div></div></div>'


def wizard_step_indicator(current_step: int, total_steps: int, step_name: str) -> str:
    """
    Step indicator for setup wizard.

    Args:
        current_step: Current step number (1-based)
        total_steps: Total number of steps
        step_name: Name of current step
    """
    dots_html = ""
    for i in range(1, total_steps + 1):
        if i < current_step:
            color = COLORS["income"]
        elif i == current_step:
            color = COLORS["accent"]
        else:
            color = COLORS["text_muted"]

        dots_html += f'''
        <div style="
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: {color};
        "></div>
        '''

    return f'''
    <div style="
        text-align: center;
        margin-bottom: 1.5rem;
    ">
        <div style="
            color: {COLORS['text_muted']};
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 0.5rem;
        ">Step {current_step} di {total_steps}</div>

        <div style="
            color: {COLORS['text_primary']};
            font-size: 1.125rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
        ">{step_name}</div>

        <div style="
            display: flex;
            justify-content: center;
            gap: 0.5rem;
        ">
            {dots_html}
        </div>
    </div>
    '''


def empty_state(icon: str, title: str, message: str, action_text: str = None) -> str:
    """
    Empty state placeholder.

    Args:
        icon: Emoji icon
        title: Title text
        message: Message text
        action_text: Optional action button text
    """
    action_html = ""
    if action_text:
        action_html = f'''
        <div style="margin-top: 1rem;">
            <span style="
                background: {COLORS['accent']};
                color: {COLORS['text_primary']};
                padding: 0.5rem 1rem;
                border-radius: {RADIUS['full']};
                font-size: 0.8125rem;
                font-weight: 500;
                cursor: pointer;
            ">{action_text}</span>
        </div>
        '''

    return f'''
    <div style="
        text-align: center;
        padding: 2rem 1rem;
        color: {COLORS['text_muted']};
    ">
        <div style="font-size: 3rem; margin-bottom: 1rem;">{icon}</div>
        <div style="
            color: {COLORS['text_secondary']};
            font-weight: 600;
            margin-bottom: 0.5rem;
        ">{title}</div>
        <div style="
            font-size: 0.875rem;
            max-width: 280px;
            margin: 0 auto;
        ">{message}</div>
        {action_html}
    </div>
    '''
