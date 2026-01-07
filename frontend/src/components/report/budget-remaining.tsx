"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Wallet, TrendingDown, Clock, AlertTriangle, CheckCircle } from "lucide-react";

interface CategoryBudget {
  category: string;
  budget_type: "fixed" | "discretionary";
  monthly_budget: number;
  spent_this_month: number;
  remaining: number;
  days_left_in_month: number;
  daily_budget_remaining: number;
  percent_used: number;
  status: "on_track" | "warning" | "over_budget";
}

// API response interface (snake_case)
interface FixedDiscretionaryData {
  month: string;
  total_income: number;
  total_fixed: number;
  total_discretionary_budget: number;
  total_discretionary_spent: number;
  discretionary_remaining: number;
  savings_potential: number;
  fixed_breakdown: CategoryBudget[];
  discretionary_breakdown: CategoryBudget[];
}

interface BudgetRemainingProps {
  data?: FixedDiscretionaryData;
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

const statusConfig = {
  on_track: {
    icon: CheckCircle,
    bgColor: "bg-emerald-500/10",
    borderColor: "border-emerald-500/30",
    textColor: "text-emerald-400",
    progressColor: "bg-emerald-500",
  },
  warning: {
    icon: AlertTriangle,
    bgColor: "bg-yellow-500/10",
    borderColor: "border-yellow-500/30",
    textColor: "text-yellow-400",
    progressColor: "bg-yellow-500",
  },
  over_budget: {
    icon: TrendingDown,
    bgColor: "bg-red-500/10",
    borderColor: "border-red-500/30",
    textColor: "text-red-400",
    progressColor: "bg-red-500",
  },
};

export function BudgetRemaining({
  data,
  isLoading,
}: BudgetRemainingProps) {
  // Destructure data from API response (snake_case)
  const totalDiscretionaryBudget = data?.total_discretionary_budget ?? 0;
  const totalDiscretionarySpent = data?.total_discretionary_spent ?? 0;
  const discretionaryRemaining = data?.discretionary_remaining ?? 0;
  const savingsPotential = data?.savings_potential ?? 0;
  const discretionaryBreakdown = data?.discretionary_breakdown ?? [];

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Budget Discrezionale</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-16 bg-muted animate-pulse rounded-lg" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const overallPercent = totalDiscretionaryBudget > 0 
    ? Math.min(100, (totalDiscretionarySpent / totalDiscretionaryBudget) * 100)
    : 0;

  const overBudgetCount = discretionaryBreakdown.filter(
    (b) => b.status === "over_budget"
  ).length;
  const warningCount = discretionaryBreakdown.filter(
    (b) => b.status === "warning"
  ).length;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Wallet className="h-5 w-5 text-primary" />
            Budget Discrezionale
            {overBudgetCount > 0 && (
              <Badge variant="destructive" className="text-xs">
                {overBudgetCount} sforato
              </Badge>
            )}
            {overBudgetCount === 0 && warningCount > 0 && (
              <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30 text-xs">
                {warningCount} attenzione
              </Badge>
            )}
          </CardTitle>
        </div>

        {/* Overall Summary */}
        <div className="mt-4 p-4 bg-muted/30 rounded-lg">
          <div className="flex justify-between items-end mb-2">
            <div>
              <span className="text-sm text-muted-foreground">Speso / Budget</span>
              <div className="text-xl font-bold">
                {formatCurrency(totalDiscretionarySpent)} / {formatCurrency(totalDiscretionaryBudget)}
              </div>
            </div>
            <div className="text-right">
              <span className="text-sm text-muted-foreground">Rimanente</span>
              <div className={`text-xl font-bold ${discretionaryRemaining >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                {formatCurrency(discretionaryRemaining)}
              </div>
            </div>
          </div>
          <Progress 
            value={overallPercent} 
            className="h-2"
          />
          <div className="flex justify-between text-xs text-muted-foreground mt-1">
            <span>{overallPercent.toFixed(0)}% utilizzato</span>
            {savingsPotential > 0 && (
              <span className="text-emerald-400">
                Potenziale risparmio: {formatCurrency(savingsPotential)}
              </span>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {discretionaryBreakdown.map((cat, index) => {
          const config = statusConfig[cat.status];
          const StatusIcon = config.icon;

          return (
            <div
              key={index}
              className={`p-3 rounded-lg border ${config.bgColor} ${config.borderColor}`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <StatusIcon className={`h-4 w-4 ${config.textColor}`} />
                  <span className="font-medium text-foreground">{cat.category}</span>
                </div>
                <div className="text-right">
                  <span className="font-bold text-foreground">
                    {formatCurrency(cat.spent_this_month)}
                  </span>
                  <span className="text-muted-foreground"> / {formatCurrency(cat.monthly_budget)}</span>
                </div>
              </div>
              
              <Progress 
                value={Math.min(100, cat.percent_used)} 
                className="h-1.5 mb-2"
              />
              
              <div className="flex justify-between text-xs">
                <span className="text-muted-foreground">
                  {cat.percent_used.toFixed(0)}% utilizzato
                </span>
                {cat.remaining > 0 && cat.days_left_in_month > 0 && (
                  <span className="flex items-center gap-1 text-muted-foreground">
                    <Clock className="h-3 w-3" />
                    {formatCurrency(cat.daily_budget_remaining)}/giorno 
                    <span className="text-muted-foreground/70">
                      ({cat.days_left_in_month}gg)
                    </span>
                  </span>
                )}
                {cat.remaining <= 0 && (
                  <span className="text-red-400">
                    Sforato di {formatCurrency(Math.abs(cat.remaining))}
                  </span>
                )}
              </div>
            </div>
          );
        })}

        {discretionaryBreakdown.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            Nessuna spesa discrezionale questo mese
          </div>
        )}
      </CardContent>
    </Card>
  );
}
