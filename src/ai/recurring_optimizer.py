"""
Recurring Expense Optimizer for MoneyMind v4.0

Analyzes recurring expenses and generates Smart Suggestions with:
- Concrete alternative providers/plans
- Estimated monthly savings
- Implementation difficulty rating
- Impact on debt payoff timeline

Optimization Strategies:
- downgrade: Switch to cheaper tier (e.g., Netflix Premium → Basic)
- switch: Change provider (e.g., Vodafone → Iliad)
- cancel: Remove unnecessary service
- renegotiate: Contact provider for better rate
- bundle: Combine services for discount
"""

from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, Dict, List, Any
from dateutil.relativedelta import relativedelta

from src.database import (
    get_recurring_expenses,
    get_recurring_expense_by_id,
    update_recurring_expense,
    get_db_context,
)


@dataclass
class OptimizationStrategy:
    """A single optimization strategy for a recurring expense."""
    strategy_type: str  # downgrade, switch, cancel, renegotiate, bundle
    title: str
    description: str
    alternative_provider: Optional[str]
    alternative_plan: Optional[str]
    current_cost: float
    new_cost: float
    estimated_savings_monthly: float
    estimated_savings_annual: float
    implementation_difficulty: str  # easy, medium, hard
    implementation_steps: List[str]
    payoff_impact_days: int  # Days earlier debt-free
    confidence: float  # 0-1 confidence in savings estimate
    requires_cancellation_fee: bool
    cancellation_fee_estimate: Optional[float]


@dataclass
class RecurringAnalysis:
    """Complete analysis of a recurring expense."""
    recurring_id: int
    provider: str
    category: str
    current_amount: float
    trend_6mo: float  # % change over 6 months
    frequency: str
    is_essential: bool
    optimization_potential: str  # none, low, medium, high
    strategies: List[OptimizationStrategy]
    recommended_strategy: Optional[OptimizationStrategy]
    total_potential_savings_monthly: float
    notes: List[str]


# Knowledge base of Italian providers and alternatives
PROVIDER_ALTERNATIVES = {
    # Streaming Services
    "netflix": {
        "category": "Abbonamenti",
        "tiers": {
            "premium": {"cost": 17.99, "features": "4K, 4 schermi"},
            "standard": {"cost": 12.99, "features": "HD, 2 schermi"},
            "standard_ads": {"cost": 6.99, "features": "HD con pubblicità"},
        },
        "alternatives": [
            {"provider": "Disney+", "cost": 8.99, "features": "Catalogo Disney/Marvel/Star Wars"},
            {"provider": "Amazon Prime Video", "cost": 4.99, "features": "Incluso in Prime"},
            {"provider": "RaiPlay", "cost": 0, "features": "Gratuito con canone RAI"},
        ],
        "bundle_options": ["Sky + Netflix", "TIM Vision + Netflix"],
    },
    "spotify": {
        "category": "Abbonamenti",
        "tiers": {
            "premium_family": {"cost": 17.99, "features": "6 account"},
            "premium_duo": {"cost": 14.99, "features": "2 account"},
            "premium": {"cost": 10.99, "features": "1 account"},
            "free": {"cost": 0, "features": "Con pubblicità"},
        },
        "alternatives": [
            {"provider": "YouTube Music", "cost": 9.99, "features": "Include YouTube Premium"},
            {"provider": "Amazon Music", "cost": 0, "features": "Incluso in Prime (limitato)"},
            {"provider": "Apple Music", "cost": 10.99, "features": "Integrazione Apple"},
        ],
    },
    "amazon prime": {
        "category": "Abbonamenti",
        "tiers": {
            "annual": {"cost": 4.08, "features": "€49/anno = €4.08/mese"},
            "monthly": {"cost": 4.99, "features": "Mensile"},
        },
        "alternatives": [],
        "essential_check": "Verifica frequenza ordini Amazon",
    },
    "disney+": {
        "category": "Abbonamenti",
        "tiers": {
            "premium": {"cost": 11.99, "features": "4K, 4 dispositivi"},
            "standard": {"cost": 8.99, "features": "HD, 2 dispositivi"},
            "standard_ads": {"cost": 5.99, "features": "Con pubblicità"},
        },
    },

    # Mobile Carriers
    "vodafone": {
        "category": "Telefonia",
        "alternatives": [
            {"provider": "Iliad", "cost_range": "7.99-9.99", "features": "150GB-300GB"},
            {"provider": "ho.Mobile", "cost_range": "6.99-9.99", "features": "100GB-200GB"},
            {"provider": "Kena Mobile", "cost_range": "5.99-7.99", "features": "100GB-150GB"},
            {"provider": "PosteMobile", "cost_range": "6.99-9.99", "features": "100GB-150GB"},
        ],
        "typical_savings": 15,
    },
    "tim": {
        "category": "Telefonia",
        "alternatives": [
            {"provider": "Iliad", "cost_range": "7.99-9.99", "features": "150GB-300GB"},
            {"provider": "ho.Mobile", "cost_range": "6.99-9.99", "features": "100GB-200GB"},
            {"provider": "Very Mobile", "cost_range": "5.99-7.99", "features": "100GB-200GB"},
        ],
        "typical_savings": 12,
    },
    "wind tre": {
        "category": "Telefonia",
        "alternatives": [
            {"provider": "Iliad", "cost_range": "7.99-9.99", "features": "150GB-300GB"},
            {"provider": "Spusu", "cost_range": "5.98-9.99", "features": "100GB-150GB"},
        ],
        "typical_savings": 10,
    },

    # Energy Providers
    "enel": {
        "category": "Utenze",
        "alternatives": [
            {"provider": "Octopus Energy", "savings": "10-15%", "features": "100% rinnovabile"},
            {"provider": "Sorgenia", "savings": "5-10%", "features": "App moderna"},
            {"provider": "Plenitude", "savings": "5-10%", "features": "Ex Eni gas e luce"},
        ],
        "renegotiate_potential": True,
    },
    "eni": {
        "category": "Utenze",
        "alternatives": [
            {"provider": "Octopus Energy", "savings": "10-15%", "features": "Tariffe trasparenti"},
            {"provider": "Wekiwi", "savings": "5-10%", "features": "Cashback"},
        ],
    },

    # Software/Cloud
    "adobe": {
        "category": "Abbonamenti",
        "alternatives": [
            {"provider": "Canva Pro", "cost": 11.99, "features": "Design grafico"},
            {"provider": "Affinity Suite", "cost": 2.50, "features": "Acquisto una tantum/mese"},
            {"provider": "GIMP + Inkscape", "cost": 0, "features": "Open source"},
        ],
        "typical_savings": 20,
    },
    "microsoft 365": {
        "category": "Abbonamenti",
        "alternatives": [
            {"provider": "Google Workspace", "cost": 0, "features": "Versione gratuita"},
            {"provider": "LibreOffice", "cost": 0, "features": "Open source"},
        ],
    },

    # Gym/Fitness
    "palestra": {
        "category": "Sport",
        "alternatives": [
            {"provider": "App fitness (Nike, Adidas)", "cost": 0, "features": "Allenamento casa"},
            {"provider": "YouTube Fitness", "cost": 0, "features": "Video gratuiti"},
            {"provider": "Palestre low-cost", "cost_range": "19-29", "features": "McFit, FitActive"},
        ],
        "seasonal_tip": "Negozia a settembre o gennaio",
    },
}


class RecurringOptimizer:
    """
    Generates Smart Suggestions for optimizing recurring expenses.

    Usage:
        optimizer = RecurringOptimizer()
        analysis = optimizer.analyze_recurring_expense(recurring_id)

        # Or analyze all recurring expenses
        all_analyses = optimizer.analyze_all_recurring()

        # Get top optimization opportunities
        opportunities = optimizer.get_top_opportunities(limit=5)
    """

    def __init__(self, debt_total: float = 0):
        """
        Initialize optimizer.

        Args:
            debt_total: Total debt amount (for payoff impact calculation)
        """
        self.debt_total = debt_total

    def analyze_recurring_expense(self, recurring_id: int) -> Optional[RecurringAnalysis]:
        """
        Analyze a single recurring expense and generate optimization strategies.

        Args:
            recurring_id: ID of the recurring expense

        Returns:
            RecurringAnalysis with strategies and recommendations
        """
        expense = get_recurring_expense_by_id(recurring_id)
        if not expense:
            return None

        provider = expense.get("provider", expense.get("pattern_name", "")).lower()
        amount = expense.get("avg_amount", 0)
        category = expense.get("category_name", "")
        trend = expense.get("trend_percent", 0)
        frequency = expense.get("frequency", "monthly")
        is_essential = expense.get("is_essential", False)

        strategies = []
        notes = []

        # Try to match with known providers
        provider_key = self._match_provider(provider)

        if provider_key and provider_key in PROVIDER_ALTERNATIVES:
            provider_data = PROVIDER_ALTERNATIVES[provider_key]
            strategies.extend(self._generate_provider_strategies(
                provider_key, provider_data, amount, category
            ))

        # Generic strategies based on category
        generic_strategies = self._generate_generic_strategies(
            provider, amount, category, is_essential, trend
        )
        strategies.extend(generic_strategies)

        # Calculate optimization potential
        total_potential = sum(s.estimated_savings_monthly for s in strategies)

        if total_potential >= amount * 0.5:
            potential = "high"
        elif total_potential >= amount * 0.2:
            potential = "medium"
        elif total_potential > 0:
            potential = "low"
        else:
            potential = "none"

        # Select best strategy
        recommended = None
        if strategies:
            # Prefer easy strategies with good savings
            strategies.sort(
                key=lambda s: (
                    s.estimated_savings_monthly * (1.5 if s.implementation_difficulty == "easy" else 1),
                ),
                reverse=True
            )
            recommended = strategies[0]

        # Add trend note
        if trend > 10:
            notes.append(f"Costo aumentato del {trend:.0f}% negli ultimi 6 mesi")
        elif trend < -10:
            notes.append(f"Costo diminuito del {abs(trend):.0f}% negli ultimi 6 mesi")

        return RecurringAnalysis(
            recurring_id=recurring_id,
            provider=provider,
            category=category,
            current_amount=amount,
            trend_6mo=trend,
            frequency=frequency,
            is_essential=is_essential,
            optimization_potential=potential,
            strategies=strategies,
            recommended_strategy=recommended,
            total_potential_savings_monthly=total_potential,
            notes=notes,
        )

    def _match_provider(self, provider_name: str) -> Optional[str]:
        """Match provider name to knowledge base key."""
        provider_lower = provider_name.lower()

        for key in PROVIDER_ALTERNATIVES.keys():
            if key in provider_lower or provider_lower in key:
                return key

        # Partial matches
        if "netflix" in provider_lower:
            return "netflix"
        if "spotify" in provider_lower:
            return "spotify"
        if "amazon" in provider_lower and "prime" in provider_lower:
            return "amazon prime"
        if "vodafone" in provider_lower:
            return "vodafone"
        if "tim" in provider_lower or "telecom" in provider_lower:
            return "tim"
        if "wind" in provider_lower or "tre" in provider_lower:
            return "wind tre"
        if "enel" in provider_lower:
            return "enel"
        if "eni" in provider_lower:
            return "eni"
        if "adobe" in provider_lower:
            return "adobe"
        if "microsoft" in provider_lower or "office" in provider_lower:
            return "microsoft 365"
        if "palestra" in provider_lower or "gym" in provider_lower or "fitness" in provider_lower:
            return "palestra"
        if "disney" in provider_lower:
            return "disney+"

        return None

    def _generate_provider_strategies(self, provider_key: str, provider_data: dict,
                                       current_amount: float, category: str) -> List[OptimizationStrategy]:
        """Generate strategies based on known provider data."""
        strategies = []

        # Downgrade strategies (tiers)
        if "tiers" in provider_data:
            tiers = provider_data["tiers"]
            current_tier = None

            # Find current tier based on amount
            for tier_name, tier_info in tiers.items():
                if abs(tier_info["cost"] - current_amount) < 2:
                    current_tier = tier_name
                    break

            # Suggest cheaper tiers
            for tier_name, tier_info in tiers.items():
                tier_cost = tier_info["cost"]
                if tier_cost < current_amount - 1:  # At least €1 savings
                    savings = current_amount - tier_cost
                    strategies.append(OptimizationStrategy(
                        strategy_type="downgrade",
                        title=f"Passa a {provider_key.title()} {tier_name.replace('_', ' ').title()}",
                        description=f"Downgrade a piano più economico: {tier_info['features']}",
                        alternative_provider=provider_key.title(),
                        alternative_plan=tier_name,
                        current_cost=current_amount,
                        new_cost=tier_cost,
                        estimated_savings_monthly=savings,
                        estimated_savings_annual=savings * 12,
                        implementation_difficulty="easy",
                        implementation_steps=[
                            "Accedi al tuo account",
                            "Vai a Impostazioni > Abbonamento",
                            "Seleziona il nuovo piano",
                            "Conferma il cambio"
                        ],
                        payoff_impact_days=self._calculate_payoff_impact(savings),
                        confidence=0.95,
                        requires_cancellation_fee=False,
                        cancellation_fee_estimate=None,
                    ))

        # Alternative provider strategies
        if "alternatives" in provider_data:
            for alt in provider_data["alternatives"]:
                alt_cost = alt.get("cost", 0)
                if isinstance(alt_cost, str):
                    # Handle cost ranges like "7.99-9.99"
                    try:
                        alt_cost = float(alt_cost.split("-")[0])
                    except ValueError:
                        continue

                if alt_cost < current_amount:
                    savings = current_amount - alt_cost
                    strategies.append(OptimizationStrategy(
                        strategy_type="switch",
                        title=f"Passa a {alt['provider']}",
                        description=f"Alternativa: {alt.get('features', 'Servizio equivalente')}",
                        alternative_provider=alt["provider"],
                        alternative_plan=None,
                        current_cost=current_amount,
                        new_cost=alt_cost,
                        estimated_savings_monthly=savings,
                        estimated_savings_annual=savings * 12,
                        implementation_difficulty="medium",
                        implementation_steps=[
                            f"Registrati su {alt['provider']}",
                            "Verifica la copertura/disponibilità",
                            "Richiedi la portabilità se applicabile",
                            f"Disdici {provider_key.title()}"
                        ],
                        payoff_impact_days=self._calculate_payoff_impact(savings),
                        confidence=0.85,
                        requires_cancellation_fee=category in ["Telefonia", "Utenze"],
                        cancellation_fee_estimate=50 if category in ["Telefonia", "Utenze"] else None,
                    ))

        return strategies

    def _generate_generic_strategies(self, provider: str, amount: float,
                                      category: str, is_essential: bool,
                                      trend: float) -> List[OptimizationStrategy]:
        """Generate generic optimization strategies."""
        strategies = []

        # Cancel strategy for non-essential
        if not is_essential and amount > 5:
            strategies.append(OptimizationStrategy(
                strategy_type="cancel",
                title=f"Cancella {provider}",
                description="Elimina completamente questa spesa se non necessaria",
                alternative_provider=None,
                alternative_plan=None,
                current_cost=amount,
                new_cost=0,
                estimated_savings_monthly=amount,
                estimated_savings_annual=amount * 12,
                implementation_difficulty="easy",
                implementation_steps=[
                    "Valuta quanto usi effettivamente questo servizio",
                    "Considera alternative gratuite",
                    "Procedi con la disdetta",
                    "Imposta un promemoria per rivalutare tra 3 mesi"
                ],
                payoff_impact_days=self._calculate_payoff_impact(amount),
                confidence=1.0,
                requires_cancellation_fee=category in ["Telefonia", "Utenze", "Palestra"],
                cancellation_fee_estimate=None,
            ))

        # Renegotiate strategy for utilities and services
        if category in ["Utenze", "Telefonia", "Assicurazioni"] and amount > 30:
            potential_savings = amount * 0.15  # Conservative 15% estimate
            strategies.append(OptimizationStrategy(
                strategy_type="renegotiate",
                title=f"Rinegozia con {provider}",
                description="Chiedi uno sconto o una tariffa migliore",
                alternative_provider=provider,
                alternative_plan="Tariffa rinegoziata",
                current_cost=amount,
                new_cost=amount - potential_savings,
                estimated_savings_monthly=potential_savings,
                estimated_savings_annual=potential_savings * 12,
                implementation_difficulty="medium",
                implementation_steps=[
                    "Cerca offerte della concorrenza",
                    f"Chiama il servizio clienti {provider}",
                    "Menziona che stai valutando alternative",
                    "Chiedi esplicitamente uno sconto fedeltà"
                ],
                payoff_impact_days=self._calculate_payoff_impact(potential_savings),
                confidence=0.6,  # Lower confidence for negotiation
                requires_cancellation_fee=False,
                cancellation_fee_estimate=None,
            ))

        # Annual payment strategy
        if amount > 10 and category in ["Abbonamenti", "Assicurazioni"]:
            annual_savings = amount * 0.15  # ~15% discount typical for annual
            strategies.append(OptimizationStrategy(
                strategy_type="bundle",
                title="Passa al pagamento annuale",
                description="Molti servizi offrono sconti per il pagamento annuale",
                alternative_provider=provider,
                alternative_plan="Piano annuale",
                current_cost=amount,
                new_cost=amount * 0.85,
                estimated_savings_monthly=annual_savings,
                estimated_savings_annual=annual_savings * 12,
                implementation_difficulty="easy",
                implementation_steps=[
                    "Verifica se è disponibile il piano annuale",
                    "Calcola il risparmio effettivo",
                    "Assicurati di voler mantenere il servizio per 12 mesi",
                    "Effettua il cambio al rinnovo"
                ],
                payoff_impact_days=self._calculate_payoff_impact(annual_savings),
                confidence=0.7,
                requires_cancellation_fee=False,
                cancellation_fee_estimate=None,
            ))

        return strategies

    def _calculate_payoff_impact(self, monthly_savings: float) -> int:
        """Calculate days earlier debt-free with these savings."""
        if self.debt_total <= 0 or monthly_savings <= 0:
            return 0

        # Rough estimate: each €50/month = 1 month earlier
        months_impact = monthly_savings / 50
        return int(months_impact * 30)  # Convert to days

    def analyze_all_recurring(self) -> List[RecurringAnalysis]:
        """Analyze all active recurring expenses."""
        recurring = get_recurring_expenses(active_only=True)
        analyses = []

        for exp in recurring:
            analysis = self.analyze_recurring_expense(exp["id"])
            if analysis:
                analyses.append(analysis)

        return analyses

    def get_top_opportunities(self, limit: int = 5) -> List[RecurringAnalysis]:
        """
        Get top optimization opportunities sorted by potential savings.

        Args:
            limit: Maximum number of opportunities to return

        Returns:
            List of RecurringAnalysis sorted by savings potential
        """
        all_analyses = self.analyze_all_recurring()

        # Filter to those with optimization potential
        with_potential = [a for a in all_analyses if a.optimization_potential != "none"]

        # Sort by total potential savings
        with_potential.sort(
            key=lambda a: a.total_potential_savings_monthly,
            reverse=True
        )

        return with_potential[:limit]

    def get_total_optimization_potential(self) -> Dict[str, Any]:
        """
        Calculate total potential savings across all recurring expenses.

        Returns:
            Dict with total monthly/annual savings and payoff impact
        """
        analyses = self.analyze_all_recurring()

        total_monthly = sum(a.total_potential_savings_monthly for a in analyses)
        total_annual = total_monthly * 12
        payoff_days = self._calculate_payoff_impact(total_monthly)

        by_category = {}
        for a in analyses:
            cat = a.category
            if cat not in by_category:
                by_category[cat] = 0
            by_category[cat] += a.total_potential_savings_monthly

        return {
            "total_monthly_potential": round(total_monthly, 2),
            "total_annual_potential": round(total_annual, 2),
            "payoff_days_potential": payoff_days,
            "recurring_count": len(analyses),
            "with_opportunities": len([a for a in analyses if a.optimization_potential != "none"]),
            "by_category": by_category,
        }

    def apply_optimization(self, recurring_id: int, strategy: OptimizationStrategy) -> bool:
        """
        Mark a recurring expense as optimized with the chosen strategy.

        Args:
            recurring_id: ID of the recurring expense
            strategy: The chosen optimization strategy

        Returns:
            True if update successful
        """
        return update_recurring_expense(recurring_id, {
            "optimization_status": "optimized",
            "optimization_suggestion": strategy.title,
            "estimated_savings_monthly": strategy.estimated_savings_monthly,
        })

    def dismiss_optimization(self, recurring_id: int, reason: str = None) -> bool:
        """
        Mark an optimization as dismissed by user.

        Args:
            recurring_id: ID of the recurring expense
            reason: Optional reason for dismissal

        Returns:
            True if update successful
        """
        return update_recurring_expense(recurring_id, {
            "optimization_status": "dismissed",
            "optimization_suggestion": reason or "Utente ha scelto di non ottimizzare",
        })

    def format_strategy_card(self, strategy: OptimizationStrategy) -> Dict[str, str]:
        """
        Format strategy for UI display.

        Returns:
            Dict with formatted strings for card display
        """
        difficulty_emoji = {
            "easy": "🟢",
            "medium": "🟡",
            "hard": "🔴",
        }

        impact_text = f"€{strategy.estimated_savings_monthly:.0f}/mese"
        if strategy.payoff_impact_days > 0:
            impact_text += f" | {strategy.payoff_impact_days} giorni prima"

        steps_text = "\n".join(f"{i+1}. {step}" for i, step in enumerate(strategy.implementation_steps))

        warning = ""
        if strategy.requires_cancellation_fee:
            if strategy.cancellation_fee_estimate:
                warning = f"⚠️ Possibile penale: ~€{strategy.cancellation_fee_estimate}"
            else:
                warning = "⚠️ Verifica eventuali penali di recesso"

        return {
            "title": strategy.title,
            "description": strategy.description,
            "savings": f"Risparmia €{strategy.estimated_savings_monthly:.0f}/mese",
            "annual": f"€{strategy.estimated_savings_annual:.0f}/anno",
            "difficulty": f"{difficulty_emoji.get(strategy.implementation_difficulty, '⚪')} {strategy.implementation_difficulty.title()}",
            "impact": impact_text,
            "steps": steps_text,
            "warning": warning,
            "confidence": f"{strategy.confidence * 100:.0f}% di confidenza",
        }

    def generate_optimization_report(self) -> str:
        """
        Generate a text report of all optimization opportunities.

        Returns:
            Formatted report string
        """
        potential = self.get_total_optimization_potential()
        top_opportunities = self.get_top_opportunities(5)

        report = f"""
REPORT OTTIMIZZAZIONE SPESE RICORRENTI
======================================

POTENZIALE TOTALE
-----------------
Risparmio mensile potenziale: €{potential['total_monthly_potential']:.0f}
Risparmio annuale potenziale: €{potential['total_annual_potential']:.0f}
Impatto su estinzione debiti: {potential['payoff_days_potential']} giorni prima

Spese analizzate: {potential['recurring_count']}
Con opportunità: {potential['with_opportunities']}

TOP 5 OPPORTUNITA'
------------------
"""
        for i, analysis in enumerate(top_opportunities, 1):
            report += f"""
{i}. {analysis.provider.upper()} (€{analysis.current_amount:.0f}/mese)
   Potenziale: {analysis.optimization_potential}
   Risparmio possibile: €{analysis.total_potential_savings_monthly:.0f}/mese
"""
            if analysis.recommended_strategy:
                strat = analysis.recommended_strategy
                report += f"   Strategia consigliata: {strat.title}\n"
                report += f"   Difficoltà: {strat.implementation_difficulty}\n"

        return report
