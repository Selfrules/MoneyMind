"""
MoneyMind FastAPI Backend - Entry Point

AI-First Personal Finance Coach API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.api.routes import dashboard, actions, insights, transactions, budgets, recurring, trends, debts, goals, profile, chat, import_transactions, xray, quickwins, impact, fire, report

settings = get_settings()

app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(actions.router, prefix="/api", tags=["Actions"])
app.include_router(insights.router, prefix="/api", tags=["Insights"])
app.include_router(transactions.router, prefix="/api", tags=["Transactions"])
app.include_router(budgets.router, prefix="/api", tags=["Budgets"])
app.include_router(recurring.router, prefix="/api", tags=["Recurring"])
app.include_router(trends.router, prefix="/api", tags=["Trends"])
app.include_router(debts.router, prefix="/api", tags=["Debts"])
app.include_router(goals.router, prefix="/api", tags=["Goals"])
app.include_router(profile.router, prefix="/api", tags=["Profile"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(import_transactions.router, prefix="/api", tags=["Import"])
app.include_router(xray.router, prefix="/api", tags=["X-Ray"])
app.include_router(quickwins.router, prefix="/api", tags=["Quick Wins"])
app.include_router(impact.router, prefix="/api", tags=["Impact Calculator"])
app.include_router(fire.router, prefix="/api", tags=["FIRE Calculator"])
app.include_router(report.router, prefix="/api", tags=["Report"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.api_version}


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "docs": "/docs",
    }
