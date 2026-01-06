"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import {
  Calculator,
  TrendingUp,
  TrendingDown,
  ArrowRight,
  Wallet,
  CreditCard,
  Flame,
  ChevronDown,
  ChevronUp,
  Sparkles,
  Target,
} from "lucide-react";

interface FinancialState {
  monthly_income: number;
  monthly_expenses: number;
  monthly_savings: number;
  savings_rate: number;
  total_debt: number;
  debt_payoff_months: number;
  debt_payoff_date: string | null;
  fire_years: number;
  fire_date: string | null;
}

interface ScenarioImpact {
  monthly_savings_delta: number;
  annual_savings_delta: number;
  debt_payoff_months_delta: number;
  debt_payoff_days_delta: number;
  fire_years_delta: number;
  total_interest_saved: number;
  savings_rate_delta: number;
  summary: string;
  highlights: string[];
}

interface ScenarioResult {
  scenario_name: string;
  scenario_type: string;
  description: string;
  current_state: FinancialState;
  simulated_state: FinancialState;
  impact: ScenarioImpact;
  confidence: number;
  assumptions: string[];
  warnings: string[];
}

interface ScenarioPreset {
  id: string;
  name: string;
  description: string;
  type: string;
  config: Record<string, unknown>;
}

interface ImpactCalculatorProps {
  presets?: ScenarioPreset[];
  isLoading?: boolean;
  onSimulate?: (presetId: string) => void;
  simulationResult?: ScenarioResult | null;
  isSimulating?: boolean;
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("it-IT", {
    style: "currency",
    currency: "EUR",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "N/A";
  const date = new Date(dateStr);
  return date.toLocaleDateString("it-IT", { month: "short", year: "numeric" });
}

interface PresetCardProps {
  preset: ScenarioPreset;
  onSimulate: () => void;
  isActive: boolean;
}

function PresetCard({ preset, onSimulate, isActive }: PresetCardProps) {
  const getTypeIcon = (type: string) => {
    switch (type) {
      case "expense":
        return <TrendingDown className="h-4 w-4" />;
      case "income":
        return <TrendingUp className="h-4 w-4" />;
      case "extra_payment":
        return <CreditCard className="h-4 w-4" />;
      case "lump_sum":
        return <Wallet className="h-4 w-4" />;
      default:
        return <Calculator className="h-4 w-4" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case "expense":
        return "bg-blue-500/20 text-blue-400 border-blue-500/30";
      case "income":
        return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
      case "extra_payment":
        return "bg-purple-500/20 text-purple-400 border-purple-500/30";
      case "lump_sum":
        return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
      default:
        return "bg-muted text-muted-foreground border-border";
    }
  };

  return (
    <button
      onClick={onSimulate}
      className={`w-full text-left p-3 rounded-lg border transition-colors ${
        isActive
          ? "border-primary bg-primary/10"
          : "border-border bg-card hover:border-primary/30"
      }`}
    >
      <div className="flex items-center gap-3">
        <div className={`flex h-8 w-8 items-center justify-center rounded-lg ${getTypeColor(preset.type)}`}>
          {getTypeIcon(preset.type)}
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium text-foreground">{preset.name}</div>
          <div className="text-xs text-muted-foreground truncate">{preset.description}</div>
        </div>
        <ArrowRight className="h-4 w-4 text-muted-foreground" />
      </div>
    </button>
  );
}

interface ResultDisplayProps {
  result: ScenarioResult;
}

function ResultDisplay({ result }: ResultDisplayProps) {
  const [showDetails, setShowDetails] = useState(false);

  return (
    <div className="space-y-4">
      {/* Impact Summary */}
      <div className="rounded-lg bg-primary/5 border border-primary/20 p-4">
        <div className="flex items-center gap-2 mb-3">
          <Target className="h-5 w-5 text-primary" />
          <span className="font-medium text-foreground">{result.scenario_name}</span>
        </div>
        <p className="text-sm text-muted-foreground">{result.description}</p>

        {/* Highlights */}
        <div className="flex flex-wrap gap-2 mt-3">
          {result.impact.highlights.map((highlight, idx) => (
            <Badge key={idx} variant="outline" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/30">
              {highlight}
            </Badge>
          ))}
        </div>
      </div>

      {/* Key Metrics Comparison */}
      <div className="grid grid-cols-2 gap-4">
        {/* Monthly Savings */}
        <div className="rounded-lg border border-border bg-card p-3">
          <div className="text-xs text-muted-foreground mb-1">Risparmio mensile</div>
          <div className="flex items-baseline gap-2">
            <span className="text-lg font-bold text-foreground">
              {formatCurrency(result.simulated_state.monthly_savings)}
            </span>
            {result.impact.monthly_savings_delta !== 0 && (
              <span className={`text-xs font-medium ${
                result.impact.monthly_savings_delta > 0 ? "text-emerald-400" : "text-red-400"
              }`}>
                {result.impact.monthly_savings_delta > 0 ? "+" : ""}
                {formatCurrency(result.impact.monthly_savings_delta)}
              </span>
            )}
          </div>
        </div>

        {/* Debt Payoff */}
        <div className="rounded-lg border border-border bg-card p-3">
          <div className="text-xs text-muted-foreground mb-1">Debt-free</div>
          <div className="flex items-baseline gap-2">
            <span className="text-lg font-bold text-foreground">
              {formatDate(result.simulated_state.debt_payoff_date)}
            </span>
            {result.impact.debt_payoff_months_delta !== 0 && (
              <span className={`text-xs font-medium ${
                result.impact.debt_payoff_months_delta < 0 ? "text-emerald-400" : "text-red-400"
              }`}>
                {result.impact.debt_payoff_months_delta < 0
                  ? `${Math.abs(result.impact.debt_payoff_months_delta)} mesi prima`
                  : `${result.impact.debt_payoff_months_delta} mesi dopo`
                }
              </span>
            )}
          </div>
        </div>

        {/* Interest Saved */}
        {result.impact.total_interest_saved > 0 && (
          <div className="rounded-lg border border-border bg-card p-3">
            <div className="text-xs text-muted-foreground mb-1">Interessi risparmiati</div>
            <div className="text-lg font-bold text-emerald-400">
              {formatCurrency(result.impact.total_interest_saved)}
            </div>
          </div>
        )}

        {/* FIRE Years */}
        {result.impact.fire_years_delta !== 0 && (
          <div className="rounded-lg border border-border bg-card p-3">
            <div className="text-xs text-muted-foreground mb-1 flex items-center gap-1">
              <Flame className="h-3.5 w-3.5 text-orange-400" />
              FIRE
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-lg font-bold text-foreground">
                {result.simulated_state.fire_years.toFixed(1)} anni
              </span>
              <span className="text-xs font-medium text-emerald-400">
                -{result.impact.fire_years_delta.toFixed(1)} anni
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Expand for more details */}
      <Button
        variant="ghost"
        size="sm"
        className="w-full text-xs"
        onClick={() => setShowDetails(!showDetails)}
      >
        {showDetails ? "Nascondi dettagli" : "Mostra confronto completo"}
        {showDetails ? <ChevronUp className="h-4 w-4 ml-1" /> : <ChevronDown className="h-4 w-4 ml-1" />}
      </Button>

      {showDetails && (
        <div className="rounded-lg border border-border bg-card p-4 text-xs">
          <div className="grid grid-cols-3 gap-2 text-muted-foreground mb-2">
            <div></div>
            <div className="text-center font-medium">Attuale</div>
            <div className="text-center font-medium">Scenario</div>
          </div>

          <div className="space-y-2">
            <div className="grid grid-cols-3 gap-2">
              <div className="text-muted-foreground">Reddito</div>
              <div className="text-center">{formatCurrency(result.current_state.monthly_income)}</div>
              <div className="text-center">{formatCurrency(result.simulated_state.monthly_income)}</div>
            </div>
            <div className="grid grid-cols-3 gap-2">
              <div className="text-muted-foreground">Spese</div>
              <div className="text-center">{formatCurrency(result.current_state.monthly_expenses)}</div>
              <div className="text-center">{formatCurrency(result.simulated_state.monthly_expenses)}</div>
            </div>
            <div className="grid grid-cols-3 gap-2">
              <div className="text-muted-foreground">Risparmio</div>
              <div className="text-center">{formatCurrency(result.current_state.monthly_savings)}</div>
              <div className="text-center text-emerald-400">{formatCurrency(result.simulated_state.monthly_savings)}</div>
            </div>
            <div className="grid grid-cols-3 gap-2">
              <div className="text-muted-foreground">Savings Rate</div>
              <div className="text-center">{result.current_state.savings_rate.toFixed(1)}%</div>
              <div className="text-center">{result.simulated_state.savings_rate.toFixed(1)}%</div>
            </div>
          </div>

          {/* Assumptions */}
          {result.assumptions.length > 0 && (
            <div className="mt-4 pt-3 border-t border-border">
              <div className="text-muted-foreground mb-1">Assunzioni:</div>
              <ul className="list-disc list-inside text-muted-foreground">
                {result.assumptions.map((a, i) => (
                  <li key={i}>{a}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Warnings */}
          {result.warnings.length > 0 && (
            <div className="mt-2">
              {result.warnings.map((w, i) => (
                <div key={i} className="text-yellow-400 flex items-center gap-1">
                  <span>!</span> {w}
                </div>
              ))}
            </div>
          )}

          {/* Confidence */}
          <div className="mt-3 flex items-center gap-2">
            <span className="text-muted-foreground">Confidenza:</span>
            <Progress value={result.confidence * 100} className="flex-1 h-1.5" />
            <span className="text-foreground">{(result.confidence * 100).toFixed(0)}%</span>
          </div>
        </div>
      )}
    </div>
  );
}

export function ImpactCalculator({
  presets = [],
  isLoading,
  onSimulate,
  simulationResult,
  isSimulating = false,
}: ImpactCalculatorProps) {
  const [selectedPreset, setSelectedPreset] = useState<string | null>(null);

  const handleSimulate = (presetId: string) => {
    if (!onSimulate) return;
    setSelectedPreset(presetId);
    onSimulate(presetId);
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Calculator className="h-5 w-5" />
            What-If Calculator
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-16 bg-muted animate-pulse rounded-lg" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg flex items-center gap-2">
          <Calculator className="h-5 w-5 text-primary" />
          What-If Calculator
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Esplora come le decisioni impattano il tuo futuro finanziario
        </p>
      </CardHeader>
      <CardContent>
        {/* Preset buttons */}
        <div className="space-y-2 mb-4">
          {presets.map((preset) => (
            <PresetCard
              key={preset.id}
              preset={preset}
              onSimulate={() => handleSimulate(preset.id)}
              isActive={selectedPreset === preset.id}
            />
          ))}
        </div>

        {/* Loading state */}
        {isSimulating && (
          <div className="text-center py-6">
            <Sparkles className="h-8 w-8 animate-pulse text-primary mx-auto mb-2" />
            <p className="text-sm text-muted-foreground">Calcolando impatto...</p>
          </div>
        )}

        {/* Results */}
        {simulationResult && !isSimulating && <ResultDisplay result={simulationResult} />}

        {/* Empty state */}
        {!simulationResult && !isSimulating && (
          <div className="text-center py-6 text-muted-foreground">
            <Calculator className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">Seleziona uno scenario per vedere l&apos;impatto</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
