"""
Impact Calculator API endpoints.

Provides What-If scenario simulation for financial decisions:
- Expense changes
- Income changes
- Extra debt payments
- Lump sum allocations
"""
import sys
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import sqlite3

# Add project root and src directory to path
BACKEND_DIR = Path(__file__).parent.parent.parent.parent
PROJECT_DIR = BACKEND_DIR.parent
SRC_DIR = PROJECT_DIR / "src"
sys.path.insert(0, str(PROJECT_DIR))
sys.path.insert(0, str(SRC_DIR))

from app.api.deps import get_db

# Import Scenario engine
from core_finance.scenario_engine import ScenarioEngine


router = APIRouter()


# Request/Response models
class ExpenseChangeRequest(BaseModel):
    category: str = Field(..., description="Category name (e.g., 'Ristoranti')")
    change_percent: Optional[float] = Field(None, description="Percentage change (-50 = 50% reduction)")
    change_amount: Optional[float] = Field(None, description="Absolute change in euros")


class IncomeChangeRequest(BaseModel):
    change_amount: float = Field(..., description="Monthly income change (positive or negative)")


class ExtraPaymentRequest(BaseModel):
    debt_id: int = Field(..., description="ID of the debt")
    extra_amount: float = Field(..., description="Extra monthly payment amount")


class LumpSumRequest(BaseModel):
    amount: float = Field(..., description="Total lump sum amount")
    allocation: Dict[str, float] = Field(
        ...,
        description="Allocation percentages (e.g., {'debt': 50, 'savings': 30, 'invest': 20})"
    )


class FinancialStateResponse(BaseModel):
    monthly_income: float
    monthly_expenses: float
    monthly_savings: float
    savings_rate: float
    total_debt: float
    monthly_debt_payment: float
    debt_payoff_date: Optional[str]
    debt_payoff_months: int
    emergency_fund_months: float
    fire_number: float
    fire_date: Optional[str]
    fire_years: float


class ImpactResponse(BaseModel):
    monthly_savings_delta: float
    annual_savings_delta: float
    debt_payoff_months_delta: int
    debt_payoff_days_delta: int
    fire_years_delta: float
    total_interest_saved: float
    savings_rate_delta: float
    summary: str
    highlights: List[str]


class ScenarioResponse(BaseModel):
    scenario_name: str
    scenario_type: str
    description: str
    current_state: FinancialStateResponse
    simulated_state: FinancialStateResponse
    impact: ImpactResponse
    confidence: float
    assumptions: List[str]
    warnings: List[str]


@router.post("/impact/expense", response_model=ScenarioResponse)
async def calculate_expense_impact(
    request: ExpenseChangeRequest,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Calculate impact of expense change.

    Simulates what happens if you reduce or increase spending in a category.

    Example: "What if I cut restaurant spending by 50%?"
    """
    try:
        engine = ScenarioEngine()
        result = engine.simulate_expense_change(
            category=request.category,
            change_percent=request.change_percent,
            change_amount=request.change_amount
        )

        return ScenarioResponse(**engine.to_dict(result))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating expense impact: {str(e)}"
        )


@router.post("/impact/income", response_model=ScenarioResponse)
async def calculate_income_impact(
    request: IncomeChangeRequest,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Calculate impact of income change.

    Simulates what happens with a salary raise, bonus, or job loss.

    Example: "What if I get a €500/month raise?"
    """
    try:
        engine = ScenarioEngine()
        result = engine.simulate_income_change(
            change_amount=request.change_amount
        )

        return ScenarioResponse(**engine.to_dict(result))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating income impact: {str(e)}"
        )


@router.post("/impact/extra-payment", response_model=ScenarioResponse)
async def calculate_extra_payment_impact(
    request: ExtraPaymentRequest,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Calculate impact of extra debt payment.

    Simulates what happens if you pay extra on a specific debt.

    Example: "What if I pay €100 extra on my credit card each month?"
    """
    try:
        engine = ScenarioEngine()
        result = engine.simulate_extra_payment(
            debt_id=request.debt_id,
            extra_amount=request.extra_amount
        )

        return ScenarioResponse(**engine.to_dict(result))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating extra payment impact: {str(e)}"
        )


@router.post("/impact/lump-sum", response_model=ScenarioResponse)
async def calculate_lump_sum_impact(
    request: LumpSumRequest,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Calculate impact of lump sum allocation.

    Simulates how to allocate a windfall (bonus, inheritance, tax refund).

    Example: "I have €5000 bonus. What's the best way to allocate it?"
    """
    try:
        engine = ScenarioEngine()
        result = engine.simulate_lump_sum(
            amount=request.amount,
            allocation=request.allocation
        )

        return ScenarioResponse(**engine.to_dict(result))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating lump sum impact: {str(e)}"
        )


class CompareRequest(BaseModel):
    scenarios: List[dict] = Field(
        ...,
        description="List of scenario configurations to compare"
    )


@router.post("/impact/compare")
async def compare_scenarios(
    request: CompareRequest,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Compare multiple scenarios side by side.

    Useful for deciding between different financial strategies.

    Example: Compare cutting dining vs cutting subscriptions vs extra debt payment.
    """
    try:
        engine = ScenarioEngine()
        results = []

        for scenario_config in request.scenarios:
            scenario_type = scenario_config.get("type")

            if scenario_type == "expense":
                result = engine.simulate_expense_change(
                    category=scenario_config.get("category", ""),
                    change_percent=scenario_config.get("change_percent"),
                    change_amount=scenario_config.get("change_amount")
                )
            elif scenario_type == "income":
                result = engine.simulate_income_change(
                    change_amount=scenario_config.get("change_amount", 0)
                )
            elif scenario_type == "extra_payment":
                result = engine.simulate_extra_payment(
                    debt_id=scenario_config.get("debt_id", 0),
                    extra_amount=scenario_config.get("extra_amount", 0)
                )
            elif scenario_type == "lump_sum":
                result = engine.simulate_lump_sum(
                    amount=scenario_config.get("amount", 0),
                    allocation=scenario_config.get("allocation", {})
                )
            else:
                continue

            results.append(result)

        comparison = engine.compare_scenarios(results)
        comparison["detailed_scenarios"] = [engine.to_dict(r) for r in results]

        return comparison

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error comparing scenarios: {str(e)}"
        )


@router.get("/impact/current-state")
async def get_current_financial_state(
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Get current financial state.

    Returns the baseline financial state used for scenario simulations.
    """
    try:
        engine = ScenarioEngine()
        state = engine.current_state

        return {
            "monthly_income": state.monthly_income,
            "monthly_expenses": state.monthly_expenses,
            "monthly_savings": state.monthly_savings,
            "savings_rate": round(state.savings_rate * 100, 1),
            "total_debt": state.total_debt,
            "monthly_debt_payment": state.monthly_debt_payment,
            "debt_payoff_date": state.debt_payoff_date.isoformat() if state.debt_payoff_date else None,
            "debt_payoff_months": state.debt_payoff_months,
            "emergency_fund_months": round(state.emergency_fund_months, 1),
            "fire_number": round(state.fire_number, 0),
            "fire_date": state.fire_date.isoformat() if state.fire_date else None,
            "fire_years": round(state.fire_years, 1),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting current state: {str(e)}"
        )


@router.get("/impact/presets")
async def get_scenario_presets(
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Get pre-built scenario presets.

    Common scenarios users might want to explore.
    """
    try:
        engine = ScenarioEngine()

        presets = [
            {
                "id": "cut_dining_50",
                "name": "Taglia ristoranti 50%",
                "description": "Riduci le spese in ristoranti della metà",
                "type": "expense",
                "config": {"category": "Ristoranti", "change_percent": -50}
            },
            {
                "id": "cut_shopping_30",
                "name": "Taglia shopping 30%",
                "description": "Riduci le spese shopping del 30%",
                "type": "expense",
                "config": {"category": "Shopping", "change_percent": -30}
            },
            {
                "id": "salary_raise_200",
                "name": "Aumento €200/mese",
                "description": "Impatto di un aumento di stipendio",
                "type": "income",
                "config": {"change_amount": 200}
            },
            {
                "id": "salary_raise_500",
                "name": "Aumento €500/mese",
                "description": "Impatto di un significativo aumento di stipendio",
                "type": "income",
                "config": {"change_amount": 500}
            },
            {
                "id": "extra_50_debt",
                "name": "Extra €50/mese su debito",
                "description": "Paga €50 extra ogni mese verso il debito",
                "type": "extra_payment",
                "config": {"debt_id": 1, "extra_amount": 50}
            },
            {
                "id": "extra_100_debt",
                "name": "Extra €100/mese su debito",
                "description": "Paga €100 extra ogni mese verso il debito",
                "type": "extra_payment",
                "config": {"debt_id": 1, "extra_amount": 100}
            },
            {
                "id": "bonus_1000_debt",
                "name": "Bonus €1000 → Debito",
                "description": "Usa un bonus per ridurre il debito",
                "type": "lump_sum",
                "config": {"amount": 1000, "allocation": {"debt": 100}}
            },
            {
                "id": "bonus_1000_mixed",
                "name": "Bonus €1000 → 50/50",
                "description": "Dividi il bonus tra debito e risparmio",
                "type": "lump_sum",
                "config": {"amount": 1000, "allocation": {"debt": 50, "savings": 50}}
            },
            {
                "id": "job_loss",
                "name": "Perdita lavoro",
                "description": "Scenario pessimistico: perdita del reddito",
                "type": "income",
                "config": {"change_amount": -2000}
            }
        ]

        return {"presets": presets}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting presets: {str(e)}"
        )


@router.post("/impact/simulate-preset/{preset_id}")
async def simulate_preset(
    preset_id: str,
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Simulate a preset scenario.

    Quick way to run pre-built scenarios.
    """
    try:
        # Get preset configuration
        presets_response = await get_scenario_presets(db)
        presets = presets_response["presets"]

        preset = None
        for p in presets:
            if p["id"] == preset_id:
                preset = p
                break

        if not preset:
            raise HTTPException(
                status_code=404,
                detail=f"Preset not found: {preset_id}"
            )

        engine = ScenarioEngine()
        config = preset["config"]
        scenario_type = preset["type"]

        if scenario_type == "expense":
            result = engine.simulate_expense_change(
                category=config.get("category", ""),
                change_percent=config.get("change_percent")
            )
        elif scenario_type == "income":
            result = engine.simulate_income_change(
                change_amount=config.get("change_amount", 0)
            )
        elif scenario_type == "extra_payment":
            result = engine.simulate_extra_payment(
                debt_id=config.get("debt_id", 1),
                extra_amount=config.get("extra_amount", 0)
            )
        elif scenario_type == "lump_sum":
            result = engine.simulate_lump_sum(
                amount=config.get("amount", 0),
                allocation=config.get("allocation", {})
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown scenario type: {scenario_type}"
            )

        response = engine.to_dict(result)
        response["preset"] = preset

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error simulating preset: {str(e)}"
        )
