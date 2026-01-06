"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  TrendingUp,
  TrendingDown,
  Minus,
  ArrowRight,
  Calendar,
  AlertCircle,
  CheckCircle,
  Target,
} from "lucide-react";
import type { FIREScenario } from "@/lib/api";

interface ScenarioComparisonProps {
  scenarios?: {
    conservative: FIREScenario;
    expected: FIREScenario;
    optimistic: FIREScenario;
  };
  isLoading?: boolean;
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("it-IT", {
    style: "currency",
    currency: "EUR",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString("it-IT", { month: "short", year: "numeric" });
}

function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

interface ScenarioCardProps {
  name: string;
  scenario: FIREScenario;
  variant: "conservative" | "expected" | "optimistic";
  baseYears: number;
}

function ScenarioCard({ name, scenario, variant, baseYears }: ScenarioCardProps) {
  const yearsDiff = scenario.years_to_fire - baseYears;

  const getVariantStyles = () => {
    switch (variant) {
      case "conservative":
        return {
          bg: "bg-amber-500/10 border-amber-500/20",
          icon: <AlertCircle className="h-5 w-5 text-amber-400" />,
          badge: "bg-amber-500/20 text-amber-400",
          iconColor: "text-amber-400",
        };
      case "expected":
        return {
          bg: "bg-blue-500/10 border-blue-500/20",
          icon: <Target className="h-5 w-5 text-blue-400" />,
          badge: "bg-blue-500/20 text-blue-400",
          iconColor: "text-blue-400",
        };
      case "optimistic":
        return {
          bg: "bg-emerald-500/10 border-emerald-500/20",
          icon: <CheckCircle className="h-5 w-5 text-emerald-400" />,
          badge: "bg-emerald-500/20 text-emerald-400",
          iconColor: "text-emerald-400",
        };
    }
  };

  const styles = getVariantStyles();

  return (
    <div className={`rounded-lg border p-4 ${styles.bg}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          {styles.icon}
          <span className="font-medium text-foreground">{name}</span>
        </div>
        <Badge variant="outline" className={styles.badge}>
          {formatPercent(scenario.return_rate)}
        </Badge>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">FIRE Number</span>
          <span className="font-medium text-foreground">
            {formatCurrency(scenario.fire_number)}
          </span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Tempo a FI</span>
          <div className="flex items-center gap-2">
            <span className="font-medium text-foreground">
              {scenario.years_to_fire.toFixed(1)} anni
            </span>
            {yearsDiff !== 0 && variant !== "expected" && (
              <span
                className={`text-xs flex items-center gap-0.5 ${
                  yearsDiff > 0 ? "text-red-400" : "text-emerald-400"
                }`}
              >
                {yearsDiff > 0 ? (
                  <TrendingUp className="h-3 w-3" />
                ) : (
                  <TrendingDown className="h-3 w-3" />
                )}
                {yearsDiff > 0 ? "+" : ""}
                {yearsDiff.toFixed(1)}
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Data FI</span>
          <span className="text-sm flex items-center gap-1 text-muted-foreground">
            <Calendar className="h-3 w-3" />
            {formatDate(scenario.fire_date)}
          </span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Spese annuali</span>
          <span className="text-sm text-muted-foreground">
            {formatCurrency(scenario.expenses)}
          </span>
        </div>
      </div>
    </div>
  );
}

export function ScenarioComparison({
  scenarios,
  isLoading,
}: ScenarioComparisonProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <TrendingUp className="h-5 w-5" />
            Scenari FI
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-32 bg-muted animate-pulse rounded-lg" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!scenarios) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <TrendingUp className="h-5 w-5" />
            Scenari FI
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-center py-4">
            Nessuno scenario disponibile
          </p>
        </CardContent>
      </Card>
    );
  }

  const baseYears = scenarios.expected.years_to_fire;

  return (
    <Card>
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-lg">
          <TrendingUp className="h-5 w-5 text-primary" />
          Scenari FI
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Come variano le proiezioni in base a rendimenti e spese
        </p>
      </CardHeader>

      <CardContent>
        <div className="space-y-3">
          <ScenarioCard
            name="Conservativo"
            scenario={scenarios.conservative}
            variant="conservative"
            baseYears={baseYears}
          />
          <ScenarioCard
            name="Atteso"
            scenario={scenarios.expected}
            variant="expected"
            baseYears={baseYears}
          />
          <ScenarioCard
            name="Ottimistico"
            scenario={scenarios.optimistic}
            variant="optimistic"
            baseYears={baseYears}
          />
        </div>

        {/* Summary */}
        <div className="mt-4 pt-4 border-t border-border">
          <div className="flex items-center justify-center gap-3 text-sm">
            <span className="text-muted-foreground">Range:</span>
            <span className="font-medium">
              {scenarios.optimistic.years_to_fire.toFixed(1)} anni
            </span>
            <ArrowRight className="h-4 w-4 text-muted-foreground" />
            <span className="font-medium">
              {scenarios.conservative.years_to_fire.toFixed(1)} anni
            </span>
          </div>
          <p className="text-xs text-muted-foreground text-center mt-2">
            Differenza di{" "}
            {Math.abs(
              scenarios.conservative.years_to_fire -
                scenarios.optimistic.years_to_fire
            ).toFixed(1)}{" "}
            anni tra gli scenari
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
