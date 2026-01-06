"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { CreditCard, TrendingUp, Calendar, AlertTriangle } from "lucide-react";

interface DebtPriorityItem {
  id: number;
  name: string;
  balance: number;
  apr: number;
  monthly_payment: number;
  interest_monthly: number;
  principal_monthly: number;
  priority_score: number;
  months_remaining: number;
  payoff_date: string | null;
  total_remaining_cost: number;
}

interface DebtPriorityMatrixProps {
  data?: DebtPriorityItem[];
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

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "N/A";
  const date = new Date(dateStr);
  return date.toLocaleDateString("it-IT", { month: "short", year: "numeric" });
}

function getAPRColor(apr: number): string {
  if (apr >= 15) return "text-red-500";
  if (apr >= 10) return "text-orange-400";
  if (apr >= 5) return "text-yellow-400";
  return "text-emerald-400";
}

function getAPRBadgeVariant(apr: number): "destructive" | "default" | "secondary" | "outline" {
  if (apr >= 15) return "destructive";
  if (apr >= 10) return "default";
  return "secondary";
}

export function DebtPriorityMatrix({ data, isLoading }: DebtPriorityMatrixProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Matrice Priorita Debiti</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-28 bg-muted animate-pulse rounded-lg" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const debts = data || [];
  const totalBalance = debts.reduce((sum, d) => sum + d.balance, 0);
  const totalMonthly = debts.reduce((sum, d) => sum + d.monthly_payment, 0);
  const totalInterest = debts.reduce((sum, d) => sum + d.interest_monthly, 0);
  const highAPRDebts = debts.filter(d => d.apr >= 10).length;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            Matrice Priorita Debiti
          </CardTitle>
          <div className="text-right">
            <div className="text-xs text-muted-foreground">Debito Totale</div>
            <div className="text-lg font-bold text-foreground">{formatCurrency(totalBalance)}</div>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-3 gap-3 mt-3">
          <div className="bg-muted/30 rounded-lg p-2 text-center">
            <div className="text-xs text-muted-foreground">Rata Mensile</div>
            <div className="text-sm font-bold">{formatCurrency(totalMonthly)}</div>
          </div>
          <div className="bg-muted/30 rounded-lg p-2 text-center">
            <div className="text-xs text-muted-foreground">Interessi/Mese</div>
            <div className="text-sm font-bold text-red-400">{formatCurrency(totalInterest)}</div>
          </div>
          <div className="bg-muted/30 rounded-lg p-2 text-center">
            <div className="text-xs text-muted-foreground">Alta Priorita</div>
            <div className="text-sm font-bold text-orange-400">{highAPRDebts} debiti</div>
          </div>
        </div>

        {highAPRDebts > 0 && (
          <div className="mt-3 p-2 bg-red-500/10 border border-red-500/20 rounded-lg flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-red-400" />
            <span className="text-sm text-red-400">
              {highAPRDebts} debito/i con APR {">"}10% - priorita massima!
            </span>
          </div>
        )}
      </CardHeader>

      <CardContent className="space-y-4">
        {debts.map((debt, index) => {
          const interestRatio = debt.monthly_payment > 0
            ? (debt.interest_monthly / debt.monthly_payment) * 100
            : 0;

          return (
            <div
              key={debt.id}
              className={`p-4 rounded-lg border ${
                debt.apr >= 15 ? "border-red-500/30 bg-red-500/5" :
                debt.apr >= 10 ? "border-orange-500/30 bg-orange-500/5" :
                "border-border bg-muted/20"
              }`}
            >
              <div className="flex items-start justify-between gap-4 mb-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-foreground">{debt.name}</span>
                    <Badge variant={getAPRBadgeVariant(debt.apr)} className="text-xs">
                      {debt.apr.toFixed(1)}% APR
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      #{index + 1} priorita
                    </Badge>
                  </div>
                  <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      Fine: {formatDate(debt.payoff_date)}
                    </span>
                    <span>{debt.months_remaining} mesi rimanenti</span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold">{formatCurrency(debt.balance)}</div>
                  <div className="text-xs text-muted-foreground">saldo</div>
                </div>
              </div>

              {/* Payment Breakdown Bar */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">
                    Rata: {formatCurrency(debt.monthly_payment)}/m
                  </span>
                  <span className="flex items-center gap-2">
                    <span className="text-red-400">{formatCurrency(debt.interest_monthly)} interessi</span>
                    <span className="text-muted-foreground">+</span>
                    <span className="text-emerald-400">{formatCurrency(debt.principal_monthly)} capitale</span>
                  </span>
                </div>

                {/* Visual bar showing interest vs principal ratio */}
                <div className="h-2 rounded-full overflow-hidden bg-muted flex">
                  <div
                    className="bg-red-500 transition-all"
                    style={{ width: `${interestRatio}%` }}
                    title={`${interestRatio.toFixed(1)}% interessi`}
                  />
                  <div
                    className="bg-emerald-500 transition-all"
                    style={{ width: `${100 - interestRatio}%` }}
                    title={`${(100 - interestRatio).toFixed(1)}% capitale`}
                  />
                </div>

                <div className="flex justify-between text-xs text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <div className="h-2 w-2 rounded-full bg-red-500" />
                    Interessi ({interestRatio.toFixed(0)}%)
                  </span>
                  <span className="flex items-center gap-1">
                    <div className="h-2 w-2 rounded-full bg-emerald-500" />
                    Capitale ({(100 - interestRatio).toFixed(0)}%)
                  </span>
                </div>
              </div>

              {/* Cost Info */}
              <div className="mt-3 pt-3 border-t border-border/50 text-xs text-muted-foreground">
                Costo totale rimanente: <span className="text-foreground font-medium">{formatCurrency(debt.total_remaining_cost)}</span>
                {debt.total_remaining_cost > debt.balance && (
                  <span className="text-red-400 ml-2">
                    ({formatCurrency(debt.total_remaining_cost - debt.balance)} in interessi)
                  </span>
                )}
              </div>
            </div>
          );
        })}

        {debts.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            Nessun debito attivo - ottimo lavoro!
          </div>
        )}
      </CardContent>
    </Card>
  );
}
