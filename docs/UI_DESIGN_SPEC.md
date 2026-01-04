# MoneyMind UI Design Specification

**Version:** 1.0
**Last Updated:** January 2026
**Design Direction:** Modern Minimalism (Hyper-Minimalism 2025)
**Framework:** Streamlit
**Default Mode:** Dark Mode

---

## Table of Contents

1. [Design Philosophy](#design-philosophy)
2. [Color System](#color-system)
3. [Typography](#typography)
4. [Spacing System](#spacing-system)
5. [Component Specifications](#component-specifications)
6. [Layout Grid](#layout-grid)
7. [Animations & Transitions](#animations--transitions)
8. [Streamlit Implementation](#streamlit-implementation)

---

## Design Philosophy

MoneyMind embraces **hyper-minimalism** - a design approach that prioritizes:

- **Extreme simplicity**: Only essential elements, zero visual clutter
- **Generous whitespace**: Breathing room for cognitive clarity
- **Subtle depth**: Minimal shadows, thin borders, micro-interactions
- **Functional beauty**: Every element serves a purpose
- **Data-first**: Numbers and insights take center stage

### Core Principles

1. **Reduce to the essential** - Remove anything that doesn't directly support the user's financial goals
2. **Clarity over decoration** - Data visualization should be immediately comprehensible
3. **Consistent rhythm** - Predictable spacing and alignment create trust
4. **Subtle feedback** - Micro-animations that feel responsive without being distracting

---

## Color System

### Background Colors

| Token | Hex | RGB | Usage |
|-------|-----|-----|-------|
| `--bg-primary` | `#0A0A0B` | `rgb(10, 10, 11)` | Main app background |
| `--bg-secondary` | `#111113` | `rgb(17, 17, 19)` | Sidebar, elevated sections |
| `--bg-card` | `#161618` | `rgb(22, 22, 24)` | Cards, containers |
| `--bg-card-hover` | `#1C1C1F` | `rgb(28, 28, 31)` | Card hover state |
| `--bg-elevated` | `#1F1F23` | `rgb(31, 31, 35)` | Modals, dropdowns |
| `--bg-input` | `#0D0D0E` | `rgb(13, 13, 14)` | Input fields |

### Text Colors

| Token | Hex | RGB | Usage |
|-------|-----|-----|-------|
| `--text-primary` | `#FAFAFA` | `rgb(250, 250, 250)` | Primary text, headings |
| `--text-secondary` | `#A1A1AA` | `rgb(161, 161, 170)` | Secondary text, descriptions |
| `--text-muted` | `#71717A` | `rgb(113, 113, 122)` | Placeholder, disabled text |
| `--text-disabled` | `#52525B` | `rgb(82, 82, 91)` | Disabled states |

### Accent Colors

| Token | Hex | RGB | Usage |
|-------|-----|-----|-------|
| `--accent-primary` | `#10B981` | `rgb(16, 185, 129)` | Primary actions, highlights |
| `--accent-primary-hover` | `#059669` | `rgb(5, 150, 105)` | Primary hover state |
| `--accent-primary-muted` | `#10B98120` | `rgba(16, 185, 129, 0.125)` | Subtle backgrounds |
| `--accent-success` | `#22C55E` | `rgb(34, 197, 94)` | Positive values, income |
| `--accent-success-muted` | `#22C55E15` | `rgba(34, 197, 94, 0.08)` | Success backgrounds |
| `--accent-warning` | `#F59E0B` | `rgb(245, 158, 11)` | Alerts, caution states |
| `--accent-warning-muted` | `#F59E0B15` | `rgba(245, 158, 11, 0.08)` | Warning backgrounds |
| `--accent-danger` | `#EF4444` | `rgb(239, 68, 68)` | Errors, expenses, negative |
| `--accent-danger-muted` | `#EF444415` | `rgba(239, 68, 68, 0.08)` | Danger backgrounds |

### Border Colors

| Token | Hex | RGB | Usage |
|-------|-----|-----|-------|
| `--border-default` | `#27272A` | `rgb(39, 39, 42)` | Default borders |
| `--border-subtle` | `#1F1F23` | `rgb(31, 31, 35)` | Subtle dividers |
| `--border-strong` | `#3F3F46` | `rgb(63, 63, 70)` | Emphasized borders |
| `--border-focus` | `#10B981` | `rgb(16, 185, 129)` | Focus rings |

### Chart Color Palette (Plotly)

```python
CHART_COLORS = {
    'primary': '#10B981',      # Emerald Green
    'secondary': '#3B82F6',    # Blue
    'tertiary': '#8B5CF6',     # Purple
    'quaternary': '#F59E0B',   # Amber
    'quinary': '#EC4899',      # Pink
    'senary': '#06B6D4',       # Cyan
    'septenary': '#F97316',    # Orange
    'octonary': '#84CC16',     # Lime
}

# Sequential scale for heatmaps/gradients
SEQUENTIAL_SCALE = [
    '#064E3B',  # Darkest
    '#065F46',
    '#047857',
    '#059669',
    '#10B981',
    '#34D399',
    '#6EE7B7',
    '#A7F3D0',  # Lightest
]
```

---

## Typography

### Font Family

**Primary Font:** Inter (Google Fonts)
**Fallback Stack:** `'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`

**Monospace Font:** JetBrains Mono
**Fallback Stack:** `'JetBrains Mono', 'Fira Code', 'SF Mono', Consolas, monospace`

### Font Import

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
```

### Type Scale

| Token | Size | Line Height | Weight | Usage |
|-------|------|-------------|--------|-------|
| `--text-display` | `48px` | `1.1` | `700` | Dashboard title, hero metrics |
| `--text-h1` | `32px` | `1.2` | `600` | Page titles |
| `--text-h2` | `24px` | `1.3` | `600` | Section headers |
| `--text-h3` | `20px` | `1.4` | `500` | Card titles |
| `--text-h4` | `16px` | `1.5` | `500` | Subsection headers |
| `--text-body` | `14px` | `1.6` | `400` | Body text |
| `--text-body-sm` | `13px` | `1.5` | `400` | Secondary body text |
| `--text-small` | `12px` | `1.4` | `400` | Captions, labels |
| `--text-tiny` | `11px` | `1.3` | `500` | Badges, chips |
| `--text-mono` | `13px` | `1.5` | `400` | Numbers, code |

### Weight Scale

| Token | Weight | Usage |
|-------|--------|-------|
| `--font-light` | `300` | Large display text |
| `--font-regular` | `400` | Body text |
| `--font-medium` | `500` | Emphasized text, buttons |
| `--font-semibold` | `600` | Headings |
| `--font-bold` | `700` | Display, hero elements |

### Letter Spacing

| Token | Value | Usage |
|-------|-------|-------|
| `--tracking-tight` | `-0.02em` | Headings, display |
| `--tracking-normal` | `0` | Body text |
| `--tracking-wide` | `0.02em` | Uppercase labels |
| `--tracking-wider` | `0.05em` | Small caps, badges |

---

## Spacing System

### Base Unit: 4px

| Token | Value | Pixels |
|-------|-------|--------|
| `--space-0` | `0` | `0px` |
| `--space-1` | `0.25rem` | `4px` |
| `--space-2` | `0.5rem` | `8px` |
| `--space-3` | `0.75rem` | `12px` |
| `--space-4` | `1rem` | `16px` |
| `--space-5` | `1.25rem` | `20px` |
| `--space-6` | `1.5rem` | `24px` |
| `--space-8` | `2rem` | `32px` |
| `--space-10` | `2.5rem` | `40px` |
| `--space-12` | `3rem` | `48px` |
| `--space-16` | `4rem` | `64px` |
| `--space-20` | `5rem` | `80px` |

### Component Spacing

| Component | Property | Value |
|-----------|----------|-------|
| Cards | Padding | `24px` (`--space-6`) |
| Cards | Gap between | `16px` (`--space-4`) |
| Sections | Margin bottom | `32px` (`--space-8`) |
| Page | Horizontal padding | `24px - 48px` |
| Sidebar | Padding | `16px` (`--space-4`) |
| Tables | Cell padding | `12px 16px` |
| Buttons | Padding | `8px 16px` / `12px 24px` |
| Inputs | Padding | `10px 14px` |
| Metrics | Gap | `8px` (`--space-2`) |

---

## Component Specifications

### Cards

```css
.card {
    background: #161618;
    border: 1px solid #27272A;
    border-radius: 12px;
    padding: 24px;
    transition: all 0.2s ease;
}

.card:hover {
    background: #1C1C1F;
    border-color: #3F3F46;
    transform: translateY(-2px);
}

/* Card with subtle glow (for featured/important) */
.card-glow {
    box-shadow: 0 0 0 1px #27272A,
                0 4px 24px rgba(0, 0, 0, 0.4);
}

/* Compact card variant */
.card-compact {
    padding: 16px;
    border-radius: 8px;
}
```

### Metric/KPI Cards

```css
.metric-card {
    background: #161618;
    border: 1px solid #27272A;
    border-radius: 12px;
    padding: 20px 24px;
}

.metric-value {
    font-size: 32px;
    font-weight: 600;
    letter-spacing: -0.02em;
    color: #FAFAFA;
    font-family: 'JetBrains Mono', monospace;
}

.metric-label {
    font-size: 12px;
    font-weight: 500;
    color: #71717A;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 8px;
}

.metric-delta-positive {
    color: #22C55E;
    font-size: 13px;
}

.metric-delta-negative {
    color: #EF4444;
    font-size: 13px;
}
```

### Buttons

```css
/* Primary Button */
.btn-primary {
    background: #10B981;
    color: #FAFAFA;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s ease;
}

.btn-primary:hover {
    background: #059669;
    transform: translateY(-1px);
}

.btn-primary:active {
    transform: translateY(0);
}

/* Secondary Button */
.btn-secondary {
    background: transparent;
    color: #FAFAFA;
    border: 1px solid #3F3F46;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s ease;
}

.btn-secondary:hover {
    background: #1F1F23;
    border-color: #52525B;
}

/* Ghost Button */
.btn-ghost {
    background: transparent;
    color: #A1A1AA;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s ease;
}

.btn-ghost:hover {
    color: #FAFAFA;
    background: #1F1F2310;
}

/* Icon Button */
.btn-icon {
    width: 36px;
    height: 36px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
}
```

### Tables / DataFrames

```css
/* Streamlit DataFrame styling */
.dataframe {
    background: #161618;
    border: 1px solid #27272A;
    border-radius: 8px;
    overflow: hidden;
}

.dataframe th {
    background: #111113;
    color: #A1A1AA;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 12px 16px;
    border-bottom: 1px solid #27272A;
    text-align: left;
}

.dataframe td {
    color: #FAFAFA;
    font-size: 13px;
    padding: 12px 16px;
    border-bottom: 1px solid #1F1F23;
    font-family: 'JetBrains Mono', monospace;
}

.dataframe tr:hover td {
    background: #1C1C1F;
}

.dataframe tr:last-child td {
    border-bottom: none;
}

/* Alternating rows (optional) */
.dataframe tr:nth-child(even) td {
    background: #131315;
}
```

### Charts (Plotly Configuration)

```python
# Plotly Layout Template
PLOTLY_TEMPLATE = {
    'layout': {
        'paper_bgcolor': '#161618',
        'plot_bgcolor': '#161618',
        'font': {
            'family': 'Inter, sans-serif',
            'color': '#A1A1AA',
            'size': 12
        },
        'title': {
            'font': {
                'size': 16,
                'color': '#FAFAFA'
            }
        },
        'xaxis': {
            'gridcolor': '#27272A',
            'linecolor': '#27272A',
            'tickfont': {'color': '#71717A', 'size': 11},
            'title': {'font': {'color': '#A1A1AA', 'size': 12}}
        },
        'yaxis': {
            'gridcolor': '#27272A',
            'linecolor': '#27272A',
            'tickfont': {'color': '#71717A', 'size': 11},
            'title': {'font': {'color': '#A1A1AA', 'size': 12}}
        },
        'legend': {
            'bgcolor': 'rgba(0,0,0,0)',
            'font': {'color': '#A1A1AA', 'size': 11}
        },
        'colorway': [
            '#10B981', '#3B82F6', '#8B5CF6', '#F59E0B',
            '#EC4899', '#06B6D4', '#F97316', '#84CC16'
        ],
        'margin': {'l': 48, 'r': 24, 't': 48, 'b': 48}
    }
}

# Chart-specific configurations
BAR_CHART_CONFIG = {
    'marker': {
        'color': '#10B981',
        'line': {'width': 0}
    }
}

LINE_CHART_CONFIG = {
    'line': {
        'width': 2,
        'color': '#10B981'
    },
    'marker': {
        'size': 0
    }
}

AREA_CHART_CONFIG = {
    'fill': 'tozeroy',
    'fillcolor': 'rgba(16, 185, 129, 0.1)',
    'line': {
        'width': 2,
        'color': '#10B981'
    }
}

PIE_CHART_CONFIG = {
    'hole': 0.6,  # Donut chart
    'marker': {
        'line': {'color': '#0A0A0B', 'width': 2}
    },
    'textfont': {'color': '#FAFAFA', 'size': 12}
}
```

### Progress Bars

```css
.progress-bar-container {
    background: #1F1F23;
    border-radius: 4px;
    height: 8px;
    overflow: hidden;
}

.progress-bar-fill {
    background: linear-gradient(90deg, #059669, #10B981);
    height: 100%;
    border-radius: 4px;
    transition: width 0.3s ease;
}

/* Thin variant */
.progress-bar-thin {
    height: 4px;
}

/* With label */
.progress-label {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
    font-size: 12px;
}

.progress-label-text {
    color: #A1A1AA;
}

.progress-label-value {
    color: #FAFAFA;
    font-family: 'JetBrains Mono', monospace;
}
```

### Input Fields

```css
.input-field {
    background: #0D0D0E;
    border: 1px solid #27272A;
    border-radius: 8px;
    padding: 10px 14px;
    color: #FAFAFA;
    font-size: 14px;
    font-family: 'Inter', sans-serif;
    transition: all 0.15s ease;
    width: 100%;
}

.input-field::placeholder {
    color: #52525B;
}

.input-field:hover {
    border-color: #3F3F46;
}

.input-field:focus {
    outline: none;
    border-color: #10B981;
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15);
}

/* Select/Dropdown */
.select-field {
    appearance: none;
    background-image: url("data:image/svg+xml,..."); /* chevron icon */
    background-repeat: no-repeat;
    background-position: right 12px center;
    padding-right: 40px;
}

/* Input with icon */
.input-with-icon {
    position: relative;
}

.input-icon {
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    color: #52525B;
}

.input-with-icon .input-field {
    padding-left: 42px;
}
```

### Badges / Chips

```css
.badge {
    display: inline-flex;
    align-items: center;
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.02em;
}

.badge-success {
    background: rgba(34, 197, 94, 0.15);
    color: #22C55E;
}

.badge-warning {
    background: rgba(245, 158, 11, 0.15);
    color: #F59E0B;
}

.badge-danger {
    background: rgba(239, 68, 68, 0.15);
    color: #EF4444;
}

.badge-neutral {
    background: rgba(161, 161, 170, 0.15);
    color: #A1A1AA;
}
```

---

## Layout Grid

### Responsive Breakpoints

| Breakpoint | Width | Usage |
|------------|-------|-------|
| `xs` | `< 576px` | Mobile portrait |
| `sm` | `576px - 767px` | Mobile landscape |
| `md` | `768px - 991px` | Tablet |
| `lg` | `992px - 1199px` | Small desktop |
| `xl` | `1200px - 1399px` | Desktop |
| `xxl` | `>= 1400px` | Large desktop |

### Streamlit Column Layouts

```python
# 2-column equal
col1, col2 = st.columns(2)

# 3-column equal
col1, col2, col3 = st.columns(3)

# 4-column equal (for metric cards)
col1, col2, col3, col4 = st.columns(4)

# Asymmetric (main + sidebar)
main, sidebar = st.columns([3, 1])

# Asymmetric (sidebar + main)
sidebar, main = st.columns([1, 4])

# With gaps (using container)
with st.container():
    cols = st.columns([1, 0.05, 1])  # 0.05 = gap column
```

### Sidebar Styling

```css
/* Streamlit sidebar */
[data-testid="stSidebar"] {
    background: #111113;
    border-right: 1px solid #27272A;
    padding: 24px 16px;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1 {
    font-size: 20px;
    font-weight: 600;
    color: #FAFAFA;
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid #27272A;
}

/* Sidebar navigation items */
.sidebar-nav-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 12px;
    border-radius: 8px;
    color: #A1A1AA;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s ease;
}

.sidebar-nav-item:hover {
    background: #1F1F23;
    color: #FAFAFA;
}

.sidebar-nav-item.active {
    background: rgba(16, 185, 129, 0.15);
    color: #10B981;
}
```

### Container Widths

```css
/* Max content width */
.content-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 24px;
}

/* Full-width sections */
.full-width {
    width: 100%;
    margin-left: -24px;
    margin-right: -24px;
    padding-left: 24px;
    padding-right: 24px;
}
```

---

## Animations & Transitions

### Timing Functions

| Token | Value | Usage |
|-------|-------|-------|
| `--ease-default` | `cubic-bezier(0.4, 0, 0.2, 1)` | General transitions |
| `--ease-in` | `cubic-bezier(0.4, 0, 1, 1)` | Exit animations |
| `--ease-out` | `cubic-bezier(0, 0, 0.2, 1)` | Enter animations |
| `--ease-bounce` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Playful feedback |

### Duration Scale

| Token | Value | Usage |
|-------|-------|-------|
| `--duration-fast` | `100ms` | Micro-interactions |
| `--duration-normal` | `150ms` | Buttons, inputs |
| `--duration-slow` | `200ms` | Cards, modals |
| `--duration-slower` | `300ms` | Page transitions |

### Hover States

```css
/* Card hover */
.card {
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.card:hover {
    transform: translateY(-2px);
    border-color: #3F3F46;
    background: #1C1C1F;
}

/* Button hover */
.btn {
    transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn:hover {
    transform: translateY(-1px);
}

.btn:active {
    transform: translateY(0);
}

/* Link hover */
.link {
    color: #A1A1AA;
    transition: color 0.15s ease;
}

.link:hover {
    color: #10B981;
}

/* Icon hover */
.icon-btn {
    transition: all 0.15s ease;
}

.icon-btn:hover {
    color: #FAFAFA;
    background: #1F1F23;
}
```

### Focus States

```css
/* Focus ring - accessibility */
.focusable:focus {
    outline: none;
    box-shadow: 0 0 0 2px #0A0A0B, 0 0 0 4px #10B981;
}

/* Focus within (for containers) */
.input-group:focus-within {
    border-color: #10B981;
}

/* Skip to main content (accessibility) */
.skip-link {
    position: absolute;
    top: -40px;
    left: 0;
    background: #10B981;
    color: #FAFAFA;
    padding: 8px 16px;
    z-index: 100;
    transition: top 0.15s ease;
}

.skip-link:focus {
    top: 0;
}
```

### Loading States

```css
/* Skeleton loading */
.skeleton {
    background: linear-gradient(
        90deg,
        #1F1F23 0%,
        #27272A 50%,
        #1F1F23 100%
    );
    background-size: 200% 100%;
    animation: skeleton-loading 1.5s ease-in-out infinite;
    border-radius: 4px;
}

@keyframes skeleton-loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}

/* Spinner */
.spinner {
    width: 20px;
    height: 20px;
    border: 2px solid #27272A;
    border-top-color: #10B981;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* Pulse (for live indicators) */
.pulse {
    animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
```

---

## Streamlit Implementation

### Custom CSS Injection

```python
import streamlit as st

def inject_custom_css():
    st.markdown("""
    <style>
        /* Import fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

        /* Root variables */
        :root {
            --bg-primary: #0A0A0B;
            --bg-secondary: #111113;
            --bg-card: #161618;
            --text-primary: #FAFAFA;
            --text-secondary: #A1A1AA;
            --text-muted: #71717A;
            --accent-primary: #10B981;
            --border-default: #27272A;
        }

        /* Global styles */
        .stApp {
            background-color: var(--bg-primary);
            font-family: 'Inter', sans-serif;
        }

        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: var(--bg-secondary);
            border-right: 1px solid var(--border-default);
        }

        /* Headings */
        h1, h2, h3, h4, h5, h6 {
            color: var(--text-primary) !important;
            font-weight: 600;
            letter-spacing: -0.02em;
        }

        /* Metrics */
        [data-testid="stMetricValue"] {
            font-family: 'JetBrains Mono', monospace;
            font-size: 32px;
            color: var(--text-primary);
        }

        [data-testid="stMetricLabel"] {
            font-size: 12px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        [data-testid="stMetricDelta"] > div {
            font-size: 13px;
        }

        /* DataFrames */
        .stDataFrame {
            border: 1px solid var(--border-default);
            border-radius: 8px;
        }

        /* Buttons */
        .stButton > button {
            background-color: var(--accent-primary);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: 500;
            transition: all 0.15s ease;
        }

        .stButton > button:hover {
            background-color: #059669;
            transform: translateY(-1px);
        }

        /* Inputs */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > div,
        .stMultiSelect > div > div > div {
            background-color: #0D0D0E;
            border: 1px solid var(--border-default);
            border-radius: 8px;
            color: var(--text-primary);
        }

        /* Cards using st.container */
        div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column"] > div[data-testid="stVerticalBlock"] {
            background-color: var(--bg-card);
            border: 1px solid var(--border-default);
            border-radius: 12px;
            padding: 24px;
        }

        /* Plotly chart backgrounds */
        .js-plotly-plot .plotly .main-svg {
            background-color: var(--bg-card) !important;
        }

        /* Progress bars */
        .stProgress > div > div > div {
            background-color: var(--accent-primary);
        }

        /* Expander */
        .streamlit-expanderHeader {
            background-color: var(--bg-card);
            border: 1px solid var(--border-default);
            border-radius: 8px;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: transparent;
        }

        .stTabs [data-baseweb="tab"] {
            background-color: transparent;
            border-radius: 8px;
            color: var(--text-secondary);
            padding: 10px 16px;
        }

        .stTabs [aria-selected="true"] {
            background-color: var(--accent-primary);
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)
```

### Plotly Theme Configuration

```python
import plotly.io as pio
import plotly.graph_objects as go

def setup_plotly_theme():
    """Configure Plotly with MoneyMind dark theme."""

    pio.templates["moneymind"] = go.layout.Template(
        layout=go.Layout(
            paper_bgcolor='#161618',
            plot_bgcolor='#161618',
            font=dict(
                family='Inter, sans-serif',
                color='#A1A1AA',
                size=12
            ),
            title=dict(
                font=dict(size=16, color='#FAFAFA'),
                x=0,
                xanchor='left'
            ),
            xaxis=dict(
                gridcolor='#27272A',
                linecolor='#27272A',
                tickfont=dict(color='#71717A', size=11),
                title=dict(font=dict(color='#A1A1AA', size=12))
            ),
            yaxis=dict(
                gridcolor='#27272A',
                linecolor='#27272A',
                tickfont=dict(color='#71717A', size=11),
                title=dict(font=dict(color='#A1A1AA', size=12))
            ),
            legend=dict(
                bgcolor='rgba(0,0,0,0)',
                font=dict(color='#A1A1AA', size=11)
            ),
            colorway=[
                '#10B981', '#3B82F6', '#8B5CF6', '#F59E0B',
                '#EC4899', '#06B6D4', '#F97316', '#84CC16'
            ],
            margin=dict(l=48, r=24, t=48, b=48)
        )
    )

    pio.templates.default = "moneymind"

# Usage
setup_plotly_theme()
```

### Component Helper Functions

```python
def metric_card(label: str, value: str, delta: str = None, delta_color: str = "normal"):
    """
    Create a styled metric card.

    Args:
        label: Metric label
        value: Metric value
        delta: Optional delta value
        delta_color: "normal", "inverse", or "off"
    """
    st.metric(
        label=label.upper(),
        value=value,
        delta=delta,
        delta_color=delta_color
    )

def styled_card(content_func, padding: str = "24px"):
    """
    Wrap content in a styled card container.

    Args:
        content_func: Function that renders content
        padding: CSS padding value
    """
    st.markdown(f"""
        <div style="
            background: #161618;
            border: 1px solid #27272A;
            border-radius: 12px;
            padding: {padding};
            margin-bottom: 16px;
        ">
    """, unsafe_allow_html=True)

    content_func()

    st.markdown("</div>", unsafe_allow_html=True)

def section_header(title: str, subtitle: str = None):
    """
    Create a styled section header.

    Args:
        title: Section title
        subtitle: Optional subtitle
    """
    st.markdown(f"""
        <div style="margin-bottom: 24px;">
            <h2 style="
                font-size: 24px;
                font-weight: 600;
                color: #FAFAFA;
                margin: 0 0 4px 0;
                letter-spacing: -0.02em;
            ">{title}</h2>
            {f'<p style="font-size: 14px; color: #71717A; margin: 0;">{subtitle}</p>' if subtitle else ''}
        </div>
    """, unsafe_allow_html=True)
```

### config.toml Theme Settings

```toml
# .streamlit/config.toml

[theme]
primaryColor = "#10B981"
backgroundColor = "#0A0A0B"
secondaryBackgroundColor = "#161618"
textColor = "#FAFAFA"
font = "sans serif"
```

---

## Quick Reference

### Color Palette Summary

```
Background:     #0A0A0B → #111113 → #161618 → #1C1C1F
Text:           #FAFAFA → #A1A1AA → #71717A → #52525B
Accent Green:   #10B981 (primary) | #059669 (hover)
Success:        #22C55E
Warning:        #F59E0B
Danger:         #EF4444
Border:         #27272A (default) | #3F3F46 (strong)
```

### Typography Summary

```
Font:           Inter (body) | JetBrains Mono (numbers)
Sizes:          48 → 32 → 24 → 20 → 16 → 14 → 13 → 12 → 11px
Weights:        300 → 400 → 500 → 600 → 700
```

### Spacing Summary

```
Base:           4px
Scale:          4 → 8 → 12 → 16 → 20 → 24 → 32 → 40 → 48 → 64 → 80px
Card padding:   24px
Card gap:       16px
Section gap:    32px
```

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Jan 2026 | Initial specification |

---

*This specification is a living document. Update as the design evolves.*
