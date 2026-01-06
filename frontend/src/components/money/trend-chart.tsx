"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { MonthlyTrend, CategoryTrend } from "@/lib/api-types";
import { TrendingUp, TrendingDown, Minus, BarChart3 } from "lucide-react";

interface TrendChartProps {
  months: string[];
  monthlyTotals: MonthlyTrend[];
  topCategories: CategoryTrend[];
  averageMonthlySpending: number;
  spendingTrendPercent: number | null;
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
  return date.toLocaleDateString("it-IT", { month: "short" });
}

function TrendIndicator({ percent }: { percent: number | null }) {
  if (percent === null) return null;

  const isUp = percent > 0;
  const isFlat = Math.abs(percent) < 5;

  if (isFlat) {
    return (
      <Badge variant="outline" className="text-muted-foreground">
        <Minus className="w-3 h-3 mr-1" />
        Stabile
      </Badge>
    );
  }

  return (
    <Badge
      variant="outline"
      className={isUp ? "text-expense border-expense/30" : "text-income border-income/30"}
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

function SimpleBarChart({ data, months }: { data: MonthlyTrend[]; months: string[] }) {
  const maxExpense = Math.max(...data.map((d) => d.expenses), 1);

  return (
    <div className="flex items-end gap-1 h-32">
      {data.map((item, index) => {
        const height = (item.expenses / maxExpense) * 100;
        const savingsHeight = item.savings > 0 ? (item.savings / maxExpense) * 100 : 0;

        return (
          <div key={item.month} className="flex-1 flex flex-col items-center gap-1">
            <div className="w-full flex flex-col items-center justify-end h-24">
              {/* Savings bar (if positive) */}
              {item.savings > 0 && (
                <div
                  className="w-full bg-income/30 rounded-t"
                  style={{ height: `${savingsHeight}%` }}
                />
              )}
              {/* Expenses bar */}
              <div
                className="w-full bg-primary rounded-t"
                style={{ height: `${height}%` }}
              />
            </div>
            <span className="text-[10px] text-muted-foreground">
              {formatMonth(item.month)}
            </span>
          </div>
        );
      })}
    </div>
  );
}

function CategoryBar({ category, maxAverage }: { category: CategoryTrend; maxAverage: number }) {
  const width = (category.average / maxAverage) * 100;

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-sm">
        <span className="flex items-center gap-2">
          <span>{category.category_icon}</span>
          <span className="text-muted-foreground">{category.category_name}</span>
        </span>
        <span className="font-medium">{formatAmount(category.average)}/mese</span>
      </div>
      <div className="h-2 bg-muted rounded-full overflow-hidden">
        <div
          className="h-full bg-primary rounded-full transition-all"
          style={{ width: `${width}%` }}
        />
      </div>
    </div>
  );
}

export function TrendChart({
  months,
  monthlyTotals,
  topCategories,
  averageMonthlySpending,
  spendingTrendPercent,
}: TrendChartProps) {
  if (monthlyTotals.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <BarChart3 className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">
            Dati insufficienti per mostrare i trend
          </p>
        </CardContent>
      </Card>
    );
  }

  const maxCategoryAverage = Math.max(...topCategories.map((c) => c.average), 1);

  return (
    <div className="space-y-4">
      {/* Monthly Overview */}
      <Card>
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base">Andamento Spese</CardTitle>
            <TrendIndicator percent={spendingTrendPercent} />
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="text-center">
            <span className="text-2xl font-bold">
              {formatAmount(averageMonthlySpending)}
            </span>
            <span className="text-sm text-muted-foreground">/mese</span>
          </div>
          <SimpleBarChart data={monthlyTotals} months={months} />
          <div className="flex justify-center gap-4 text-xs">
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-primary rounded" />
              <span className="text-muted-foreground">Spese</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-income/30 rounded" />
              <span className="text-muted-foreground">Risparmi</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Top Categories */}
      {topCategories.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Top Categorie</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {topCategories.slice(0, 5).map((category) => (
              <CategoryBar
                key={category.category_name}
                category={category}
                maxAverage={maxCategoryAverage}
              />
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
