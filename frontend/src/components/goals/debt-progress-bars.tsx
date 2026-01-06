"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  CreditCard,
  TrendingDown,
  Calendar,
  Target,
  Zap,
  CheckCircle,
  AlertCircle,
} from "lucide-react";

interface Debt {
  id: number;
  name: string;
  type: string;
  original_amount: number;
  current_balance: number;
  interest_rate: number;
  monthly_payment: number;
  expected_end_date?: string;
  is_active: boolean;
  priority_order?: number;
}

interface DebtProgressBarsProps {
  debts: Debt[];
  totalOriginal: number;
  totalCurrent: number;
  projectedPayoffDate?: string;
  monthlyPayment?: number;
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

function getDebtTypeIcon(type: string): string {
  switch (type.toLowerCase()) {
    case "credit_card":
      return "💳";
    case "personal_loan":
      return "🏦";
    case "mortgage":
      return "🏠";
    case "auto_loan":
      return "🚗";
    case "student_loan":
      return "🎓";
    default:
      return "💰";
  }
}

function getProgressColor(progress: number): string {
  if (progress >= 75) return "bg-emerald-500";
  if (progress >= 50) return "bg-green-500";
  if (progress >= 25) return "bg-yellow-500";
  return "bg-orange-500";
}

function DebtBar({ debt }: { debt: Debt }) {
  const paidOff = debt.original_amount - debt.current_balance;
  const progress = debt.original_amount > 0
    ? (paidOff / debt.original_amount) * 100
    : 0;
  const isComplete = debt.current_balance <= 0;

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-lg">{getDebtTypeIcon(debt.type)}</span>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-medium text-foreground text-sm">{debt.name}</span>
              {debt.priority_order === 1 && (
                <Badge variant="outline" className="bg-yellow-500/10 text-yellow-400 border-yellow-500/30 text-xs py-0">
                  <Zap className="h-3 w-3 mr-0.5" />
                  Priorità
                </Badge>
              )}
              {isComplete && (
                <Badge variant="outline" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/30 text-xs py-0">
                  <CheckCircle className="h-3 w-3 mr-0.5" />
                  Estinto
                </Badge>
              )}
            </div>
            <div className="flex items-center gap-3 text-xs text-muted-foreground">
              <span>{debt.interest_rate}% APR</span>
              {debt.monthly_payment > 0 && (
                <span>{formatCurrency(debt.monthly_payment)}/mese</span>
              )}
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className={`font-bold ${isComplete ? "text-emerald-400" : "text-foreground"}`}>
            {formatCurrency(debt.current_balance)}
          </div>
          <div className="text-xs text-muted-foreground">
            di {formatCurrency(debt.original_amount)}
          </div>
        </div>
      </div>

      {/* Progress bar */}
      <div className="relative">
        <Progress
          value={progress}
          className={`h-3 ${isComplete ? "[&>div]:bg-emerald-500" : ""}`}
        />
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-xs font-medium text-white drop-shadow">
            {progress.toFixed(0)}%
          </span>
        </div>
      </div>

      {/* Expected payoff */}
      {debt.expected_end_date && !isComplete && (
        <div className="flex items-center gap-1 text-xs text-muted-foreground">
          <Calendar className="h-3 w-3" />
          <span>Estinzione prevista: {formatDate(debt.expected_end_date)}</span>
        </div>
      )}
    </div>
  );
}

export function DebtProgressBars({
  debts,
  totalOriginal,
  totalCurrent,
  projectedPayoffDate,
  monthlyPayment,
  isLoading,
}: DebtProgressBarsProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            Debiti
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {[1, 2, 3].map((i) => (
              <div key={i} className="space-y-2">
                <div className="h-4 w-32 bg-muted animate-pulse rounded" />
                <div className="h-3 w-full bg-muted animate-pulse rounded" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const activeDebts = debts.filter((d) => d.is_active && d.current_balance > 0);
  const paidOffDebts = debts.filter((d) => d.current_balance <= 0);
  const totalPaid = totalOriginal - totalCurrent;
  const overallProgress = totalOriginal > 0 ? (totalPaid / totalOriginal) * 100 : 0;

  if (debts.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            Debiti
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <CheckCircle className="h-12 w-12 text-emerald-400 mx-auto mb-3" />
            <p className="text-foreground font-medium">Nessun debito attivo!</p>
            <p className="text-sm text-muted-foreground mt-1">
              Complimenti, sei libero dai debiti.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <TrendingDown className="h-5 w-5 text-primary" />
            Percorso Debt-Free
          </CardTitle>
          <Badge variant="outline" className="bg-primary/10 text-primary">
            {activeDebts.length} attivi
          </Badge>
        </div>

        {/* Overall summary */}
        <div className="grid grid-cols-2 gap-4 mt-4">
          <div className="rounded-lg bg-card border border-border p-3">
            <div className="text-xs text-muted-foreground mb-1">Debito totale</div>
            <div className="text-xl font-bold text-foreground">
              {formatCurrency(totalCurrent)}
            </div>
            <div className="text-xs text-emerald-400">
              -{formatCurrency(totalPaid)} pagato
            </div>
          </div>
          <div className="rounded-lg bg-card border border-border p-3">
            <div className="text-xs text-muted-foreground mb-1">Debt-free</div>
            <div className="text-xl font-bold text-foreground">
              {projectedPayoffDate ? formatDate(projectedPayoffDate) : "N/A"}
            </div>
            {monthlyPayment && (
              <div className="text-xs text-muted-foreground">
                {formatCurrency(monthlyPayment)}/mese
              </div>
            )}
          </div>
        </div>

        {/* Overall progress */}
        <div className="mt-4">
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-muted-foreground">Progresso totale</span>
            <span className="font-medium text-foreground">{overallProgress.toFixed(1)}%</span>
          </div>
          <Progress value={overallProgress} className="h-3" />
        </div>
      </CardHeader>

      <CardContent>
        {/* Active debts */}
        {activeDebts.length > 0 && (
          <div className="space-y-6">
            {activeDebts
              .sort((a, b) => (a.priority_order || 99) - (b.priority_order || 99))
              .map((debt) => (
                <DebtBar key={debt.id} debt={debt} />
              ))}
          </div>
        )}

        {/* Paid off debts */}
        {paidOffDebts.length > 0 && (
          <div className="mt-6 pt-4 border-t border-border">
            <div className="text-sm font-medium text-muted-foreground mb-3 flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-emerald-400" />
              Debiti estinti ({paidOffDebts.length})
            </div>
            <div className="space-y-4">
              {paidOffDebts.map((debt) => (
                <DebtBar key={debt.id} debt={debt} />
              ))}
            </div>
          </div>
        )}

        {/* Freedom celebration */}
        {activeDebts.length === 0 && debts.length > 0 && (
          <div className="mt-4 p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-center">
            <CheckCircle className="h-10 w-10 text-emerald-400 mx-auto mb-2" />
            <p className="font-bold text-emerald-400 text-lg">Debt-Free!</p>
            <p className="text-sm text-muted-foreground mt-1">
              Hai estinto tutti i tuoi debiti. Ora puoi concentrarti sulla crescita!
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
