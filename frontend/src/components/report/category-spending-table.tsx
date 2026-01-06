"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { JudgmentBadge, JudgmentDot } from "./judgment-badge";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface CategorySpendingItem {
  category: string;
  icon: string;
  amount_current: number;
  amount_avg_3m: number;
  benchmark: number;
  judgment: "excellent" | "good" | "warning" | "critical";
  variance_percent: number;
  notes: string;
  suggestion: string | null;
}

interface CategorySpendingTableProps {
  data?: CategorySpendingItem[];
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

function VarianceIndicator({ variance }: { variance: number }) {
  if (Math.abs(variance) < 5) {
    return <Minus className="h-4 w-4 text-muted-foreground" />;
  }
  if (variance > 0) {
    return <TrendingUp className="h-4 w-4 text-red-400" />;
  }
  return <TrendingDown className="h-4 w-4 text-emerald-400" />;
}

export function CategorySpendingTable({ data, isLoading }: CategorySpendingTableProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Analisi Spese per Categoria</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-16 bg-muted animate-pulse rounded-lg" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const categories = data || [];

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-lg">Analisi Spese per Categoria</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        {/* Table Header */}
        <div className="grid grid-cols-12 gap-2 px-4 py-2 text-xs font-medium text-muted-foreground border-b border-border bg-muted/30">
          <div className="col-span-4">Categoria</div>
          <div className="col-span-2 text-right">Speso</div>
          <div className="col-span-2 text-right">Media 3m</div>
          <div className="col-span-2 text-right">Benchmark</div>
          <div className="col-span-2 text-center">Giudizio</div>
        </div>

        {/* Table Body */}
        <div className="divide-y divide-border">
          {categories.map((cat, index) => (
            <div
              key={index}
              className={`grid grid-cols-12 gap-2 px-4 py-3 items-center hover:bg-muted/20 transition-colors ${
                cat.judgment === "critical" ? "bg-red-500/5" :
                cat.judgment === "warning" ? "bg-yellow-500/5" : ""
              }`}
            >
              {/* Category */}
              <div className="col-span-4 flex items-center gap-2">
                <span className="text-lg">{cat.icon}</span>
                <div className="min-w-0">
                  <div className="font-medium text-sm truncate">{cat.category}</div>
                  <div className="text-xs text-muted-foreground flex items-center gap-1">
                    <VarianceIndicator variance={cat.variance_percent} />
                    {Math.abs(cat.variance_percent).toFixed(0)}% vs media
                  </div>
                </div>
              </div>

              {/* Current Amount */}
              <div className="col-span-2 text-right">
                <span className={`font-semibold text-sm ${
                  cat.judgment === "critical" ? "text-red-400" :
                  cat.judgment === "warning" ? "text-yellow-400" :
                  "text-foreground"
                }`}>
                  {formatCurrency(cat.amount_current)}
                </span>
              </div>

              {/* 3-Month Average */}
              <div className="col-span-2 text-right text-sm text-muted-foreground">
                {formatCurrency(cat.amount_avg_3m)}
              </div>

              {/* Benchmark */}
              <div className="col-span-2 text-right text-sm text-muted-foreground">
                {formatCurrency(cat.benchmark)}
              </div>

              {/* Judgment */}
              <div className="col-span-2 flex justify-center">
                <JudgmentBadge judgment={cat.judgment} showLabel={false} />
              </div>

              {/* Notes Row (expandable) */}
              {(cat.notes || cat.suggestion) && (
                <div className="col-span-12 mt-1 pl-8">
                  <p className="text-xs text-muted-foreground">{cat.notes}</p>
                  {cat.suggestion && (
                    <p className="text-xs text-yellow-400 mt-1">
                      💡 {cat.suggestion}
                    </p>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Summary Footer */}
        <div className="px-4 py-3 bg-muted/30 border-t border-border">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Totale Spese</span>
            <span className="font-bold">
              {formatCurrency(categories.reduce((sum, cat) => sum + cat.amount_current, 0))}
            </span>
          </div>
          <div className="flex gap-4 mt-2 text-xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <span className="text-red-400">{categories.filter(c => c.judgment === "critical").length}</span> critici
            </span>
            <span className="flex items-center gap-1">
              <span className="text-yellow-400">{categories.filter(c => c.judgment === "warning").length}</span> attenzione
            </span>
            <span className="flex items-center gap-1">
              <span className="text-emerald-400">{categories.filter(c => c.judgment === "excellent" || c.judgment === "good").length}</span> ok
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
