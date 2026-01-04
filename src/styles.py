"""
MoneyMind Design System - Modern Minimal Dark Theme
====================================================
Emerald Green accent on dark background
2025 Finance Dashboard UI
"""

# Color Palette
COLORS = {
    # Backgrounds
    "bg_primary": "#0A0A0A",      # Near black - main background
    "bg_secondary": "#141414",     # Slightly lighter - cards
    "bg_tertiary": "#1F1F1F",      # Hover states, inputs
    "bg_elevated": "#262626",      # Modals, dropdowns

    # Text
    "text_primary": "#FAFAFA",     # White - headings
    "text_secondary": "#A1A1AA",   # Gray - body text
    "text_muted": "#71717A",       # Muted - labels, captions
    "text_inverse": "#0A0A0A",     # Dark text on light bg

    # Accent - Emerald Green
    "accent": "#10B981",           # Primary emerald
    "accent_hover": "#059669",     # Darker emerald
    "accent_light": "#34D399",     # Lighter emerald
    "accent_muted": "rgba(16, 185, 129, 0.15)",  # Background tint

    # Semantic
    "success": "#22C55E",          # Green
    "warning": "#F59E0B",          # Amber
    "danger": "#EF4444",           # Red
    "info": "#3B82F6",             # Blue

    # Borders
    "border": "#27272A",           # Subtle borders
    "border_hover": "#3F3F46",     # Hover state

    # Charts
    "chart_green": "#10B981",
    "chart_red": "#EF4444",
    "chart_blue": "#3B82F6",
    "chart_purple": "#8B5CF6",
    "chart_orange": "#F97316",
    "chart_pink": "#EC4899",
    "chart_cyan": "#06B6D4",
    "chart_yellow": "#EAB308",
}

# Typography
FONTS = {
    "heading": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
    "body": "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
    "mono": "'JetBrains Mono', 'Fira Code', monospace",
}

# Spacing (4px base)
SPACING = {
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px",
    "2xl": "48px",
    "3xl": "64px",
}

# Border Radius
RADIUS = {
    "sm": "6px",
    "md": "8px",
    "lg": "12px",
    "xl": "16px",
    "full": "9999px",
}


def get_custom_css() -> str:
    """Return the complete custom CSS for the app."""
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
        --accent-hover: {COLORS['accent_hover']};
        --border: {COLORS['border']};
        --success: {COLORS['success']};
        --warning: {COLORS['warning']};
        --danger: {COLORS['danger']};
        --radius: {RADIUS['md']};
    }}

    /* ===== GLOBAL STYLES ===== */
    .stApp {{
        background-color: var(--bg-primary);
        color: var(--text-primary);
        font-family: {FONTS['body']};
    }}

    /* Hide Streamlit branding */
    #MainMenu, footer, header {{
        visibility: hidden;
    }}

    /* ===== TYPOGRAPHY ===== */
    h1, h2, h3, h4, h5, h6 {{
        font-family: {FONTS['heading']};
        font-weight: 600;
        color: var(--text-primary);
        letter-spacing: -0.02em;
    }}

    h1 {{
        font-size: 2rem;
        font-weight: 700;
    }}

    h2 {{
        font-size: 1.5rem;
    }}

    h3 {{
        font-size: 1.25rem;
    }}

    p, span, div {{
        font-family: {FONTS['body']};
        color: var(--text-secondary);
    }}

    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {{
        background-color: var(--bg-secondary);
        border-right: 1px solid var(--border);
    }}

    [data-testid="stSidebar"] [data-testid="stMarkdown"] {{
        color: var(--text-primary);
    }}

    /* ===== CARDS ===== */
    .metric-card {{
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: {RADIUS['lg']};
        padding: {SPACING['lg']};
        transition: all 0.2s ease;
    }}

    .metric-card:hover {{
        border-color: var(--accent);
        transform: translateY(-2px);
    }}

    .metric-card .label {{
        font-size: 0.875rem;
        color: var(--text-muted);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: {SPACING['sm']};
    }}

    .metric-card .value {{
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        font-family: {FONTS['heading']};
    }}

    .metric-card .value.positive {{
        color: var(--success);
    }}

    .metric-card .value.negative {{
        color: var(--danger);
    }}

    .metric-card .delta {{
        font-size: 0.875rem;
        margin-top: {SPACING['xs']};
    }}

    .metric-card .delta.up {{
        color: var(--success);
    }}

    .metric-card .delta.down {{
        color: var(--danger);
    }}

    /* ===== BUTTONS ===== */
    .stButton > button {{
        background: var(--accent);
        color: var(--text-inverse);
        border: none;
        border-radius: {RADIUS['md']};
        padding: {SPACING['sm']} {SPACING['lg']};
        font-weight: 600;
        font-family: {FONTS['body']};
        transition: all 0.2s ease;
        cursor: pointer;
    }}

    .stButton > button:hover {{
        background: var(--accent-hover);
        transform: translateY(-1px);
    }}

    .stButton > button:active {{
        transform: translateY(0);
    }}

    /* Secondary button */
    .stButton > button[kind="secondary"] {{
        background: transparent;
        color: var(--text-primary);
        border: 1px solid var(--border);
    }}

    .stButton > button[kind="secondary"]:hover {{
        background: var(--bg-tertiary);
        border-color: var(--accent);
    }}

    /* ===== INPUTS ===== */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {{
        background-color: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: {RADIUS['md']};
        color: var(--text-primary);
        font-family: {FONTS['body']};
    }}

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {{
        border-color: var(--accent);
        box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.2);
    }}

    /* ===== DATA TABLES ===== */
    .stDataFrame {{
        border: 1px solid var(--border);
        border-radius: {RADIUS['lg']};
        overflow: hidden;
    }}

    .stDataFrame [data-testid="stDataFrameResizable"] {{
        background-color: var(--bg-secondary);
    }}

    /* ===== METRICS ===== */
    [data-testid="stMetric"] {{
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: {RADIUS['lg']};
        padding: {SPACING['md']};
    }}

    [data-testid="stMetricLabel"] {{
        color: var(--text-muted) !important;
    }}

    [data-testid="stMetricValue"] {{
        color: var(--text-primary) !important;
        font-weight: 700;
    }}

    /* ===== PROGRESS BARS ===== */
    .stProgress > div > div {{
        background-color: var(--bg-tertiary);
        border-radius: {RADIUS['full']};
    }}

    .stProgress > div > div > div {{
        background: linear-gradient(90deg, var(--accent) 0%, {COLORS['accent_light']} 100%);
        border-radius: {RADIUS['full']};
    }}

    /* ===== FILE UPLOADER ===== */
    [data-testid="stFileUploader"] {{
        background: var(--bg-secondary);
        border: 2px dashed var(--border);
        border-radius: {RADIUS['lg']};
        padding: {SPACING['xl']};
        transition: all 0.2s ease;
    }}

    [data-testid="stFileUploader"]:hover {{
        border-color: var(--accent);
        background: var(--bg-tertiary);
    }}

    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: transparent;
        gap: {SPACING['xs']};
    }}

    .stTabs [data-baseweb="tab"] {{
        background-color: transparent;
        color: var(--text-muted);
        border-radius: {RADIUS['md']};
        padding: {SPACING['sm']} {SPACING['md']};
        font-weight: 500;
    }}

    .stTabs [data-baseweb="tab"]:hover {{
        background-color: var(--bg-tertiary);
        color: var(--text-primary);
    }}

    .stTabs [aria-selected="true"] {{
        background-color: var(--accent) !important;
        color: var(--text-inverse) !important;
    }}

    /* ===== EXPANDER ===== */
    .streamlit-expanderHeader {{
        background-color: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: {RADIUS['md']};
        color: var(--text-primary);
    }}

    .streamlit-expanderContent {{
        background-color: var(--bg-secondary);
        border: 1px solid var(--border);
        border-top: none;
        border-radius: 0 0 {RADIUS['md']} {RADIUS['md']};
    }}

    /* ===== ALERTS ===== */
    .stAlert {{
        border-radius: {RADIUS['md']};
        border: none;
    }}

    .stSuccess {{
        background-color: rgba(34, 197, 94, 0.1);
        color: var(--success);
    }}

    .stWarning {{
        background-color: rgba(245, 158, 11, 0.1);
        color: var(--warning);
    }}

    .stError {{
        background-color: rgba(239, 68, 68, 0.1);
        color: var(--danger);
    }}

    .stInfo {{
        background-color: rgba(59, 130, 246, 0.1);
        color: var(--info);
    }}

    /* ===== DIVIDERS ===== */
    hr {{
        border: none;
        border-top: 1px solid var(--border);
        margin: {SPACING['lg']} 0;
    }}

    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}

    ::-webkit-scrollbar-track {{
        background: var(--bg-primary);
    }}

    ::-webkit-scrollbar-thumb {{
        background: var(--border);
        border-radius: {RADIUS['full']};
    }}

    ::-webkit-scrollbar-thumb:hover {{
        background: var(--text-muted);
    }}

    /* ===== CUSTOM COMPONENTS ===== */

    /* Transaction Row */
    .tx-row {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: {SPACING['md']};
        background: var(--bg-secondary);
        border-radius: {RADIUS['md']};
        margin-bottom: {SPACING['sm']};
        transition: all 0.2s ease;
    }}

    .tx-row:hover {{
        background: var(--bg-tertiary);
    }}

    /* Category Badge */
    .category-badge {{
        display: inline-flex;
        align-items: center;
        gap: {SPACING['xs']};
        padding: {SPACING['xs']} {SPACING['sm']};
        background: var(--bg-tertiary);
        border-radius: {RADIUS['full']};
        font-size: 0.75rem;
        font-weight: 500;
        color: var(--text-secondary);
    }}

    /* Budget Progress */
    .budget-item {{
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: {RADIUS['lg']};
        padding: {SPACING['md']};
        margin-bottom: {SPACING['sm']};
    }}

    .budget-item .header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: {SPACING['sm']};
    }}

    .budget-item .progress-bar {{
        height: 8px;
        background: var(--bg-tertiary);
        border-radius: {RADIUS['full']};
        overflow: hidden;
    }}

    .budget-item .progress-fill {{
        height: 100%;
        border-radius: {RADIUS['full']};
        transition: width 0.3s ease;
    }}

    .budget-item .progress-fill.ok {{
        background: var(--success);
    }}

    .budget-item .progress-fill.warning {{
        background: var(--warning);
    }}

    .budget-item .progress-fill.danger {{
        background: var(--danger);
    }}

    /* AI Insight Card */
    .ai-card {{
        background: linear-gradient(135deg, {COLORS['accent']}15 0%, {COLORS['chart_purple']}15 100%);
        border: 1px solid {COLORS['accent']}40;
        border-radius: {RADIUS['lg']};
        padding: {SPACING['lg']};
    }}

    .ai-card .icon {{
        font-size: 1.5rem;
        margin-bottom: {SPACING['sm']};
    }}

    .ai-card .title {{
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: {SPACING['sm']};
    }}

    .ai-card .content {{
        color: var(--text-secondary);
        line-height: 1.6;
    }}
</style>
"""


def get_plotly_theme() -> dict:
    """Return Plotly theme configuration for dark mode."""
    return {
        "template": "plotly_dark",
        "layout": {
            "paper_bgcolor": COLORS["bg_secondary"],
            "plot_bgcolor": COLORS["bg_secondary"],
            "font": {
                "family": FONTS["body"],
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
            COLORS["chart_green"],
            COLORS["chart_red"],
            COLORS["chart_blue"],
            COLORS["chart_purple"],
            COLORS["chart_orange"],
            COLORS["chart_pink"],
            COLORS["chart_cyan"],
            COLORS["chart_yellow"],
        ],
    }


# Metric card HTML template
def metric_card(label: str, value: str, delta: str = None, delta_type: str = "neutral") -> str:
    """Generate HTML for a metric card."""
    delta_html = ""
    if delta:
        delta_class = "up" if delta_type == "positive" else "down" if delta_type == "negative" else ""
        arrow = "↑" if delta_type == "positive" else "↓" if delta_type == "negative" else ""
        delta_html = f'<div class="delta {delta_class}">{arrow} {delta}</div>'

    value_class = "positive" if delta_type == "positive" else "negative" if delta_type == "negative" else ""

    return f"""
    <div class="metric-card">
        <div class="label">{label}</div>
        <div class="value {value_class}">{value}</div>
        {delta_html}
    </div>
    """
