"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import type { BudgetStatus } from "@/lib/api-types";
import { AlertTriangle, CheckCircle, XCircle, PiggyBank } from "lucide-react";

interface BudgetProgressProps {
  categories: BudgetStatus[];
  totalBudget: number;
  totalSpent: number;
  overBudgetCount: number;
  warningCount: number;
}

function formatAmount(amount: number): string {
  return new Intl.NumberFormat("it-IT", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(amount);
}

function StatusIcon({ status }: { status: BudgetStatus["status"] }) {
  switch (status) {
    case "exceeded":
      return <XCircle className="w-4 h-4 text-expense" />;
    case "warning":
      return <AlertTriangle className="w-4 h-4 text-warning" />;
    default:
      return <CheckCircle className="w-4 h-4 text-income" />;
  }
}

function BudgetItem({ budget }: { budget: BudgetStatus }) {
  const progressColor =
    budget.status === "exceeded"
      ? "bg-expense"
      : budget.status === "warning"
      ? "bg-warning"
      : "bg-primary";

  return (
    <div className="space-y-2 py-3 border-b border-border/50 last:border-0">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-lg">{budget.category_icon}</span>
          <span className="text-sm font-medium">{budget.category_name}</span>
        </div>
        <div className="flex items-center gap-2">
          <StatusIcon status={budget.status} />
          <span className="text-sm text-muted-foreground">
            {formatAmount(budget.spent_amount)} / {formatAmount(budget.budget_amount)}
          </span>
        </div>
      </div>
      <div className="relative">
        <Progress
          value={Math.min(budget.percent_used, 100)}
          className="h-2"
        />
        {budget.percent_used > 100 && (
          <div
            className="absolute top-0 h-2 bg-expense/50 rounded-r-full"
            style={{
              left: "100%",
              width: `${Math.min(budget.percent_used - 100, 50)}%`,
            }}
          />
        )}
      </div>
      <div className="flex justify-between text-xs text-muted-foreground">
        <span>{Math.round(budget.percent_used)}% usato</span>
        <span
          className={budget.remaining < 0 ? "text-expense" : "text-income"}
        >
          {budget.remaining >= 0 ? "Rimangono" : "Sforato di"}{" "}
          {formatAmount(Math.abs(budget.remaining))}
        </span>
      </div>
    </div>
  );
}

export function BudgetProgress({
  categories,
  totalBudget,
  totalSpent,
  overBudgetCount,
  warningCount,
}: BudgetProgressProps) {
  const totalRemaining = totalBudget - totalSpent;
  const totalPercent = totalBudget > 0 ? (totalSpent / totalBudget) * 100 : 0;

  if (categories.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <PiggyBank className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">
            Nessun budget impostato per questo mese
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
          <CardTitle className="text-base">Riepilogo Budget</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-2xl font-bold">
              {formatAmount(totalSpent)}
            </span>
            <span className="text-muted-foreground">
              di {formatAmount(totalBudget)}
            </span>
          </div>
          <Progress value={Math.min(totalPercent, 100)} className="h-3" />
          <div className="flex gap-2">
            {overBudgetCount > 0 && (
              <Badge variant="destructive" className="text-xs">
                <XCircle className="w-3 h-3 mr-1" />
                {overBudgetCount} sforati
              </Badge>
            )}
            {warningCount > 0 && (
              <Badge
                variant="outline"
                className="text-xs text-warning border-warning/30"
              >
                <AlertTriangle className="w-3 h-3 mr-1" />
                {warningCount} a rischio
              </Badge>
            )}
            {overBudgetCount === 0 && warningCount === 0 && (
              <Badge
                variant="outline"
                className="text-xs text-income border-income/30"
              >
                <CheckCircle className="w-3 h-3 mr-1" />
                Tutto ok
              </Badge>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Categories */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Per Categoria</CardTitle>
        </CardHeader>
        <CardContent>
          {categories.map((budget) => (
            <BudgetItem key={budget.category_id} budget={budget} />
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
