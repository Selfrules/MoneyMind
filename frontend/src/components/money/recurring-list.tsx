"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { RecurringExpense, RecurringSummaryResponse } from "@/lib/api-types";
import {
  RefreshCw,
  TrendingUp,
  TrendingDown,
  Lightbulb,
  Calendar,
  PiggyBank,
} from "lucide-react";

interface RecurringListProps {
  expenses: RecurringExpense[];
  totalMonthly: number;
  essentialMonthly: number;
  nonEssentialMonthly: number;
  potentialSavings: number;
  optimizableCount: number;
}

function formatAmount(amount: number): string {
  return new Intl.NumberFormat("it-IT", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(amount);
}

function formatFrequency(freq: string): string {
  switch (freq) {
    case "monthly":
      return "Mensile";
    case "quarterly":
      return "Trimestrale";
    case "annual":
      return "Annuale";
    default:
      return freq;
  }
}

function TrendBadge({ percent }: { percent: number | null }) {
  if (percent === null) return null;

  const isUp = percent > 0;
  const isFlat = Math.abs(percent) < 5;

  if (isFlat) return null;

  return (
    <Badge
      variant="outline"
      className={`text-xs ${
        isUp ? "text-expense border-expense/30" : "text-income border-income/30"
      }`}
    >
      {isUp ? (
        <TrendingUp className="w-3 h-3 mr-1" />
      ) : (
        <TrendingDown className="w-3 h-3 mr-1" />
      )}
      {Math.abs(percent).toFixed(0)}%
    </Badge>
  );
}

function OptimizationBadge({ status }: { status: string }) {
  if (status === "ok" || status === "none") return null;

  return (
    <Badge
      variant="outline"
      className="text-xs text-warning border-warning/30"
    >
      <Lightbulb className="w-3 h-3 mr-1" />
      Ottimizzabile
    </Badge>
  );
}

function RecurringItem({ expense }: { expense: RecurringExpense }) {
  return (
    <div className="space-y-2 py-3 border-b border-border/50 last:border-0">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-lg">{expense.category_icon}</span>
          <div className="flex flex-col">
            <span className="text-sm font-medium line-clamp-1">
              {expense.pattern_name}
            </span>
            {expense.provider && (
              <span className="text-xs text-muted-foreground">
                {expense.provider}
              </span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-expense">
            {formatAmount(expense.avg_amount)}/mese
          </span>
        </div>
      </div>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="text-xs">
            <Calendar className="w-3 h-3 mr-1" />
            {formatFrequency(expense.frequency)}
          </Badge>
          {expense.is_essential && (
            <Badge variant="outline" className="text-xs">
              Essenziale
            </Badge>
          )}
          <TrendBadge percent={expense.trend_percent} />
        </div>
        <OptimizationBadge status={expense.optimization_status} />
      </div>
      {expense.optimization_suggestion && (
        <div className="bg-warning/10 border border-warning/20 rounded-lg p-2 mt-2">
          <p className="text-xs text-warning">
            <Lightbulb className="w-3 h-3 inline mr-1" />
            {expense.optimization_suggestion}
          </p>
          {expense.estimated_savings_monthly && expense.estimated_savings_monthly > 0 && (
            <p className="text-xs text-income mt-1">
              Risparmio potenziale: {formatAmount(expense.estimated_savings_monthly)}/mese
            </p>
          )}
        </div>
      )}
    </div>
  );
}

export function RecurringList({
  expenses,
  totalMonthly,
  essentialMonthly,
  nonEssentialMonthly,
  potentialSavings,
  optimizableCount,
}: RecurringListProps) {
  if (expenses.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <RefreshCw className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">
            Nessuna spesa ricorrente rilevata
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Summary Card */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Riepilogo Ricorrenti</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-2xl font-bold text-expense">
              {formatAmount(totalMonthly)}
            </span>
            <span className="text-sm text-muted-foreground">/mese</span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Essenziali</span>
              <span>{formatAmount(essentialMonthly)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Non essenziali</span>
              <span>{formatAmount(nonEssentialMonthly)}</span>
            </div>
          </div>
          {potentialSavings > 0 && (
            <div className="bg-income/10 border border-income/20 rounded-lg p-3">
              <div className="flex items-center gap-2">
                <PiggyBank className="w-4 h-4 text-income" />
                <span className="text-sm text-income">
                  Risparmio potenziale: {formatAmount(potentialSavings)}/mese
                </span>
              </div>
              {optimizableCount > 0 && (
                <p className="text-xs text-muted-foreground mt-1">
                  {optimizableCount} spese ottimizzabili
                </p>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Expenses List */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Spese Ricorrenti</CardTitle>
        </CardHeader>
        <CardContent>
          {expenses.map((expense) => (
            <RecurringItem key={expense.id} expense={expense} />
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
