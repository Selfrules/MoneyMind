"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import type { MonthlyReportResponse } from "@/lib/api-types";
import {
  Calendar,
  TrendingUp,
  TrendingDown,
  CheckCircle,
  Target,
  Lightbulb,
  Receipt,
} from "lucide-react";

interface MonthlyReviewProps {
  report: MonthlyReportResponse;
}

function formatAmount(amount: number): string {
  return new Intl.NumberFormat("it-IT", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(amount);
}

function formatMonth(monthStr: string): string {
  const [year, month] = monthStr.split("-");
  const date = new Date(parseInt(year), parseInt(month) - 1);
  return date.toLocaleDateString("it-IT", {
    month: "long",
    year: "numeric",
  });
}

export function MonthlyReview({ report }: MonthlyReviewProps) {
  const savingsPositive = report.savings >= 0;

  return (
    <div className="space-y-4">
      {/* Month Header */}
      <Card>
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base flex items-center gap-2">
              <Calendar className="w-5 h-5 text-primary" />
              Review {formatMonth(report.month)}
            </CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Income/Expenses/Savings Summary */}
          <div className="grid grid-cols-3 gap-2 text-center">
            <div className="bg-income/10 rounded-lg p-3">
              <p className="text-xs text-muted-foreground">Entrate</p>
              <p className="text-lg font-bold text-income">
                {formatAmount(report.income)}
              </p>
            </div>
            <div className="bg-expense/10 rounded-lg p-3">
              <p className="text-xs text-muted-foreground">Uscite</p>
              <p className="text-lg font-bold text-expense">
                {formatAmount(report.expenses)}
              </p>
            </div>
            <div
              className={`rounded-lg p-3 ${
                savingsPositive ? "bg-primary/10" : "bg-expense/10"
              }`}
            >
              <p className="text-xs text-muted-foreground">Risparmio</p>
              <p
                className={`text-lg font-bold ${
                  savingsPositive ? "text-primary" : "text-expense"
                }`}
              >
                {formatAmount(report.savings)}
              </p>
            </div>
          </div>

          {/* Savings Rate */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Tasso di risparmio</span>
              <span className="font-medium">
                {report.savings_rate.toFixed(1)}%
              </span>
            </div>
            <Progress
              value={Math.max(0, Math.min(100, report.savings_rate * 5))}
              className="h-2"
            />
            <p className="text-xs text-muted-foreground">
              Obiettivo: 20% | Tu:{" "}
              {report.savings_rate >= 20 ? (
                <span className="text-income">Raggiunto! ✓</span>
              ) : (
                <span className="text-warning">
                  Mancano {(20 - report.savings_rate).toFixed(1)}%
                </span>
              )}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Top Categories */}
      {report.top_expense_categories.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Top Spese</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {report.top_expense_categories.map((cat, index) => (
              <div
                key={cat.category}
                className="flex items-center justify-between"
              >
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">
                    {index + 1}.
                  </span>
                  <span className="text-sm">{cat.category}</span>
                </div>
                <span className="font-medium text-expense">
                  {formatAmount(cat.amount)}
                </span>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Performance Metrics */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Performance</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {/* Budget Performance */}
          <div className="flex items-center justify-between py-2 border-b border-border/50">
            <div className="flex items-center gap-2">
              <Target className="w-4 h-4 text-primary" />
              <span className="text-sm">Budget rispettati</span>
            </div>
            <Badge
              variant="outline"
              className={
                report.budget_performance >= 80
                  ? "text-income border-income/30"
                  : report.budget_performance >= 50
                  ? "text-warning border-warning/30"
                  : "text-expense border-expense/30"
              }
            >
              {report.budget_performance.toFixed(0)}%
            </Badge>
          </div>

          {/* Debt Payments */}
          <div className="flex items-center justify-between py-2 border-b border-border/50">
            <div className="flex items-center gap-2">
              <Receipt className="w-4 h-4 text-primary" />
              <span className="text-sm">Pagamenti debiti</span>
            </div>
            <span className="font-medium">
              {formatAmount(report.debt_payments_made)}
            </span>
          </div>

          {/* Actions */}
          <div className="flex items-center justify-between py-2 border-b border-border/50">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-primary" />
              <span className="text-sm">Azioni completate</span>
            </div>
            <Badge variant="outline">
              {report.actions_completed}/{report.actions_total}
            </Badge>
          </div>

          {/* Insights */}
          <div className="flex items-center justify-between py-2">
            <div className="flex items-center gap-2">
              <Lightbulb className="w-4 h-4 text-primary" />
              <span className="text-sm">Insight generati</span>
            </div>
            <Badge variant="outline">{report.insights_generated}</Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
