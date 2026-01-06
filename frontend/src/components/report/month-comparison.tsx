"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, TrendingDown, Minus, ArrowLeftRight } from "lucide-react";

interface MonthComparisonItem {
  category: string;
  current_month: number;
  previous_month: number;
  delta: number;
  delta_percent: number;
  trend: "up" | "down" | "stable";
}

interface MonthComparisonProps {
  data?: MonthComparisonItem[];
  isLoading?: boolean;
  currentMonth?: string;
  previousMonth?: string;
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("it-IT", {
    style: "currency",
    currency: "EUR",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

function TrendIcon({ trend, delta }: { trend: string; delta: number }) {
  if (trend === "stable" || Math.abs(delta) < 10) {
    return <Minus className="h-4 w-4 text-muted-foreground" />;
  }
  if (trend === "up" || delta > 0) {
    return <TrendingUp className="h-4 w-4 text-red-400" />;
  }
  return <TrendingDown className="h-4 w-4 text-emerald-400" />;
}

function DeltaBadge({ delta, deltaPercent }: { delta: number; deltaPercent: number }) {
  if (Math.abs(delta) < 10) {
    return (
      <span className="text-xs text-muted-foreground">
        stabile
      </span>
    );
  }

  const isIncrease = delta > 0;
  const color = isIncrease ? "text-red-400" : "text-emerald-400";
  const sign = isIncrease ? "+" : "";

  return (
    <span className={`text-xs font-medium ${color}`}>
      {sign}{formatCurrency(delta)} ({sign}{deltaPercent.toFixed(0)}%)
    </span>
  );
}

export function MonthComparison({ data, isLoading, currentMonth, previousMonth }: MonthComparisonProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Confronto Mese</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-12 bg-muted animate-pulse rounded-lg" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const comparisons = data || [];
  const totalCurrentSpend = comparisons.reduce((sum, c) => sum + c.current_month, 0);
  const totalPreviousSpend = comparisons.reduce((sum, c) => sum + c.previous_month, 0);
  const totalDelta = totalCurrentSpend - totalPreviousSpend;
  const increasedCategories = comparisons.filter(c => c.delta > 10).length;
  const decreasedCategories = comparisons.filter(c => c.delta < -10).length;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <ArrowLeftRight className="h-5 w-5" />
            Confronto Mensile
          </CardTitle>
        </div>

        {/* Summary */}
        <div className="grid grid-cols-3 gap-3 mt-3">
          <div className="bg-muted/30 rounded-lg p-3 text-center">
            <div className="text-xs text-muted-foreground">Mese Corrente</div>
            <div className="text-lg font-bold">{formatCurrency(totalCurrentSpend)}</div>
          </div>
          <div className="bg-muted/30 rounded-lg p-3 text-center">
            <div className="text-xs text-muted-foreground">Mese Precedente</div>
            <div className="text-lg font-bold">{formatCurrency(totalPreviousSpend)}</div>
          </div>
          <div className={`rounded-lg p-3 text-center ${
            totalDelta > 50 ? "bg-red-500/10" :
            totalDelta < -50 ? "bg-emerald-500/10" :
            "bg-muted/30"
          }`}>
            <div className="text-xs text-muted-foreground">Variazione</div>
            <div className={`text-lg font-bold ${
              totalDelta > 50 ? "text-red-400" :
              totalDelta < -50 ? "text-emerald-400" :
              "text-foreground"
            }`}>
              {totalDelta > 0 ? "+" : ""}{formatCurrency(totalDelta)}
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="flex items-center gap-4 mt-3 text-xs text-muted-foreground">
          {increasedCategories > 0 && (
            <span className="flex items-center gap-1">
              <TrendingUp className="h-3 w-3 text-red-400" />
              {increasedCategories} categorie aumentate
            </span>
          )}
          {decreasedCategories > 0 && (
            <span className="flex items-center gap-1">
              <TrendingDown className="h-3 w-3 text-emerald-400" />
              {decreasedCategories} categorie diminuite
            </span>
          )}
        </div>
      </CardHeader>

      <CardContent className="p-0">
        {/* Table Header */}
        <div className="grid grid-cols-12 gap-2 px-4 py-2 text-xs font-medium text-muted-foreground border-b border-border bg-muted/30">
          <div className="col-span-4">Categoria</div>
          <div className="col-span-3 text-right">Corrente</div>
          <div className="col-span-3 text-right">Precedente</div>
          <div className="col-span-2 text-right">Delta</div>
        </div>

        {/* Table Body */}
        <div className="divide-y divide-border">
          {comparisons.map((item, index) => (
            <div
              key={index}
              className={`grid grid-cols-12 gap-2 px-4 py-3 items-center hover:bg-muted/20 transition-colors ${
                item.delta > 50 ? "bg-red-500/5" :
                item.delta < -50 ? "bg-emerald-500/5" : ""
              }`}
            >
              {/* Category */}
              <div className="col-span-4 flex items-center gap-2">
                <TrendIcon trend={item.trend} delta={item.delta} />
                <span className="font-medium text-sm">{item.category}</span>
              </div>

              {/* Current Month */}
              <div className="col-span-3 text-right text-sm font-medium">
                {formatCurrency(item.current_month)}
              </div>

              {/* Previous Month */}
              <div className="col-span-3 text-right text-sm text-muted-foreground">
                {formatCurrency(item.previous_month)}
              </div>

              {/* Delta */}
              <div className="col-span-2 text-right">
                <DeltaBadge delta={item.delta} deltaPercent={item.delta_percent} />
              </div>
            </div>
          ))}
        </div>

        {comparisons.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            Nessun dato per il confronto
          </div>
        )}
      </CardContent>
    </Card>
  );
}
