"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, AlertCircle, Calendar } from "lucide-react";
import type { MonthSummary as MonthSummaryType } from "@/lib/api-types";

interface MonthSummaryProps {
  summary: MonthSummaryType;
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("it-IT", {
    style: "currency",
    currency: "EUR",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

function formatMonth(monthStr: string): string {
  const [year, month] = monthStr.split("-");
  const date = new Date(parseInt(year), parseInt(month) - 1);
  return date.toLocaleDateString("it-IT", { month: "long", year: "numeric" });
}

export function MonthSummary({ summary }: MonthSummaryProps) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Calendar className="h-5 w-5 text-primary" />
            {formatMonth(summary.month)}
          </CardTitle>
          <Badge
            variant={summary.on_track ? "default" : "destructive"}
            className="flex items-center gap-1"
          >
            {summary.on_track ? (
              <>
                <CheckCircle className="h-3 w-3" />
                In Target
              </>
            ) : (
              <>
                <AlertCircle className="h-3 w-3" />
                Attenzione
              </>
            )}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <p className="text-xs text-muted-foreground mb-1">Entrate</p>
            <p className="text-lg font-semibold text-income">
              {formatCurrency(summary.income)}
            </p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground mb-1">Uscite</p>
            <p className="text-lg font-semibold text-expense">
              {formatCurrency(summary.expenses)}
            </p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground mb-1">Risparmio</p>
            <p
              className={`text-lg font-semibold ${
                summary.savings >= 0 ? "text-income" : "text-expense"
              }`}
            >
              {formatCurrency(summary.savings)}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
