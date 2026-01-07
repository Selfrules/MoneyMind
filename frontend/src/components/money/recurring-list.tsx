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
  Clock,
  AlertTriangle,
  CheckCircle,
  XCircle,
  MessageSquare,
} from "lucide-react";

interface RecurringListProps {
  expenses: RecurringExpense[];
  totalMonthly: number;
  essentialMonthly: number;
  nonEssentialMonthly: number;
  potentialSavings: number;
  optimizableCount: number;
  dueThisMonthCount?: number;
  dueThisMonthTotal?: number;
  highPriorityActions?: number;
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

function AIActionBadge({ action, priority }: { action: string | null; priority: string | null }) {
  if (!action) return null;

  const config: Record<string, { icon: React.ReactNode; label: string; className: string }> = {
    keep: {
      icon: <CheckCircle className="w-3 h-3 mr-1" />,
      label: "OK",
      className: "text-income border-income/30 bg-income/5",
    },
    cancel: {
      icon: <XCircle className="w-3 h-3 mr-1" />,
      label: "Disdici",
      className: "text-expense border-expense/30 bg-expense/5",
    },
    renegotiate: {
      icon: <MessageSquare className="w-3 h-3 mr-1" />,
      label: "Rinegozia",
      className: "text-warning border-warning/30 bg-warning/5",
    },
    review: {
      icon: <AlertTriangle className="w-3 h-3 mr-1" />,
      label: "Verifica",
      className: "text-primary border-primary/30 bg-primary/5",
    },
  };

  const cfg = config[action] || config.keep;
  const priorityIndicator = priority === "high" ? "!" : "";

  return (
    <Badge variant="outline" className={`text-xs ${cfg.className}`}>
      {cfg.icon}
      {cfg.label}{priorityIndicator}
    </Badge>
  );
}

function DueDateBadge({ daysUntil }: { daysUntil: number | null }) {
  if (daysUntil === null) return null;

  let className = "text-muted-foreground border-muted/30";
  let label = `${daysUntil}g`;

  if (daysUntil <= 3) {
    className = "text-expense border-expense/30";
    label = daysUntil === 0 ? "Oggi" : daysUntil === 1 ? "Domani" : `${daysUntil}g`;
  } else if (daysUntil <= 7) {
    className = "text-warning border-warning/30";
  }

  return (
    <Badge variant="outline" className={`text-xs ${className}`}>
      <Clock className="w-3 h-3 mr-1" />
      {label}
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
        <div className="flex flex-col items-end gap-1">
          <span className="text-sm font-semibold text-expense">
            {formatAmount(expense.avg_amount)}
          </span>
          <span className="text-xs text-muted-foreground">
            {formatFrequency(expense.frequency)}
          </span>
        </div>
      </div>
      <div className="flex items-center justify-between flex-wrap gap-1">
        <div className="flex items-center gap-1 flex-wrap">
          <DueDateBadge daysUntil={expense.days_until_due} />
          {expense.is_essential && (
            <Badge variant="outline" className="text-xs">
              Essenziale
            </Badge>
          )}
          <TrendBadge percent={expense.trend_percent} />
          {expense.budget_impact_percent && expense.budget_impact_percent > 3 && (
            <Badge variant="outline" className="text-xs text-muted-foreground">
              {expense.budget_impact_percent.toFixed(1)}% budget
            </Badge>
          )}
        </div>
        <AIActionBadge action={expense.ai_action} priority={expense.ai_priority} />
      </div>
      {expense.ai_reason && expense.ai_action !== "keep" && (
        <div className="bg-muted/50 border border-border/50 rounded-lg p-2 mt-1">
          <p className="text-xs text-muted-foreground">
            <Lightbulb className="w-3 h-3 inline mr-1 text-primary" />
            {expense.ai_reason}
          </p>
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
  dueThisMonthCount = 0,
  dueThisMonthTotal = 0,
  highPriorityActions = 0,
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
      {/* Due This Month Card */}
      {dueThisMonthCount > 0 && (
        <Card className="border-primary/30 bg-primary/5">
          <CardContent className="py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-primary/20 rounded-full">
                  <Calendar className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <p className="text-sm font-medium">Scadenze questo mese</p>
                  <p className="text-xs text-muted-foreground">
                    {dueThisMonthCount} pagamenti in arrivo
                  </p>
                </div>
              </div>
              <div className="text-right">
                <span className="text-xl font-bold text-primary">
                  {formatAmount(dueThisMonthTotal)}
                </span>
              </div>
            </div>
            {highPriorityActions > 0 && (
              <div className="mt-3 flex items-center gap-2 text-warning">
                <AlertTriangle className="w-4 h-4" />
                <span className="text-xs">
                  {highPriorityActions} azioni ad alta priorità da verificare
                </span>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Summary Card */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Riepilogo Mensile</CardTitle>
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
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">Prossime Scadenze</CardTitle>
            <Badge variant="secondary" className="text-xs">
              {expenses.length} abbonamenti
            </Badge>
          </div>
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
