"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, Calendar, TrendingDown, Percent } from "lucide-react";

interface DebtDetail {
  id: number;
  name: string;
  balance: number;
  rate: number;
  payment: number;
  burden_percent: number;
}

interface HighestRateDebt {
  name: string;
  rate: number;
  balance: number;
}

interface DebtAnalysisData {
  total_debt: number;
  total_monthly_payments: number;
  total_interest_paid_ytd: number;
  total_interest_remaining: number;
  debt_burden_percent: number;
  months_to_freedom: number | null;
  freedom_date: string | null;
  highest_rate_debt: HighestRateDebt | null;
  debts: DebtDetail[];
}

interface DebtCostAnalysisProps {
  data?: DebtAnalysisData;
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
  if (!dateStr) return "--";
  const date = new Date(dateStr);
  return date.toLocaleDateString("it-IT", { month: "short", year: "numeric" });
}

export function DebtCostAnalysis({ data, isLoading }: DebtCostAnalysisProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Debt Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-20 bg-muted animate-pulse rounded-lg" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const defaultData: DebtAnalysisData = data || {
    total_debt: 0,
    total_monthly_payments: 0,
    total_interest_paid_ytd: 0,
    total_interest_remaining: 0,
    debt_burden_percent: 0,
    months_to_freedom: null,
    freedom_date: null,
    highest_rate_debt: null,
    debts: [],
  };

  const hasDebts = defaultData.debts.length > 0;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Debt Analysis</CardTitle>
          {defaultData.months_to_freedom && (
            <Badge variant="outline" className="text-xs">
              <Calendar className="h-3 w-3 mr-1" />
              {defaultData.months_to_freedom} mesi alla libertà
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {/* Summary Stats */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="rounded-lg bg-card border border-border p-4">
            <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Total Debt</div>
            <div className="text-2xl font-bold text-red-400">{formatCurrency(defaultData.total_debt)}</div>
          </div>
          <div className="rounded-lg bg-card border border-border p-4">
            <div className="text-xs text-muted-foreground uppercase tracking-wider mb-1">Monthly Payments</div>
            <div className="text-2xl font-bold text-foreground">{formatCurrency(defaultData.total_monthly_payments)}</div>
          </div>
        </div>

        {/* Interest Cost Card */}
        <div className="rounded-lg bg-red-500/10 border border-red-500/20 p-4 mb-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="h-4 w-4 text-red-400" />
            <span className="text-sm font-medium text-red-400">Interest Cost</span>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-xs text-muted-foreground">Paid YTD</div>
              <div className="text-lg font-semibold text-red-400">
                {formatCurrency(defaultData.total_interest_paid_ytd)}
              </div>
            </div>
            <div>
              <div className="text-xs text-muted-foreground">Remaining</div>
              <div className="text-lg font-semibold text-red-300">
                {formatCurrency(defaultData.total_interest_remaining)}
              </div>
            </div>
          </div>
        </div>

        {/* Highest Rate Alert */}
        {defaultData.highest_rate_debt && (
          <div className="rounded-lg bg-yellow-500/10 border border-yellow-500/20 p-4 mb-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Percent className="h-4 w-4 text-yellow-400" />
                <span className="text-sm text-muted-foreground">Highest Interest Rate</span>
              </div>
              <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30">
                {defaultData.highest_rate_debt.rate.toFixed(1)}%
              </Badge>
            </div>
            <div className="mt-2">
              <div className="text-sm font-medium text-foreground">{defaultData.highest_rate_debt.name}</div>
              <div className="text-xs text-muted-foreground">Balance: {formatCurrency(defaultData.highest_rate_debt.balance)}</div>
            </div>
          </div>
        )}

        {/* Debt Burden Indicator */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-muted-foreground">Debt Burden (DTI)</span>
            <span className={`text-sm font-semibold ${
              defaultData.debt_burden_percent <= 20 ? "text-emerald-400" :
              defaultData.debt_burden_percent <= 36 ? "text-yellow-400" : "text-red-400"
            }`}>
              {defaultData.debt_burden_percent.toFixed(1)}%
            </span>
          </div>
          <Progress
            value={Math.min(defaultData.debt_burden_percent, 100)}
            className="h-2"
          />
          <div className="flex justify-between mt-1 text-xs text-muted-foreground">
            <span>Healthy &lt;20%</span>
            <span>Stretched &lt;36%</span>
            <span>At Risk &gt;36%</span>
          </div>
        </div>

        {/* Debts List */}
        {hasDebts && (
          <div className="space-y-2">
            <div className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">
              Active Debts
            </div>
            {defaultData.debts.slice(0, 5).map((debt) => (
              <div key={debt.id} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                <div>
                  <div className="text-sm font-medium text-foreground">{debt.name}</div>
                  <div className="text-xs text-muted-foreground">
                    {debt.rate.toFixed(1)}% APR • {formatCurrency(debt.payment)}/mo
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-semibold text-foreground">{formatCurrency(debt.balance)}</div>
                  <div className="text-xs text-muted-foreground">{debt.burden_percent.toFixed(1)}% of income</div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Freedom Date */}
        {defaultData.freedom_date && (
          <div className="mt-4 pt-4 border-t border-border">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <TrendingDown className="h-4 w-4 text-emerald-400" />
                <span className="text-sm text-muted-foreground">Debt Freedom Date</span>
              </div>
              <span className="text-sm font-semibold text-emerald-400">
                {formatDate(defaultData.freedom_date)}
              </span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
