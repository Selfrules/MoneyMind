"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import type { DebtSummaryResponse } from "@/lib/api-types";
import { Trophy, Calendar, TrendingDown, Banknote } from "lucide-react";

interface DebtFreedomCardProps {
  data: DebtSummaryResponse;
}

function formatAmount(amount: number): string {
  return new Intl.NumberFormat("it-IT", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(amount);
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "Non calcolato";
  const date = new Date(dateStr);
  return date.toLocaleDateString("it-IT", {
    month: "long",
    year: "numeric",
  });
}

export function DebtFreedomCard({ data }: DebtFreedomCardProps) {
  const {
    total_debt,
    total_monthly_payment,
    active_count,
    projected_debt_free_date,
    months_to_freedom,
  } = data;

  // Calculate total original debt
  const totalOriginal = data.debts.reduce((sum, d) => sum + d.original_amount, 0);
  const progressPercent = totalOriginal > 0
    ? ((totalOriginal - total_debt) / totalOriginal) * 100
    : 0;

  const hasDebt = total_debt > 0;

  return (
    <Card className="border-primary/20">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base flex items-center gap-2">
            <Trophy className="w-5 h-5 text-primary" />
            Libertà dai Debiti
          </CardTitle>
          <Badge variant={hasDebt ? "outline" : "default"} className="text-xs">
            {hasDebt ? `${active_count} attivi` : "Debt Free! 🎉"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {hasDebt ? (
          <>
            {/* Progress toward debt freedom */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Progresso</span>
                <span className="font-medium">{progressPercent.toFixed(0)}%</span>
              </div>
              <Progress value={progressPercent} className="h-3" />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>Pagato: {formatAmount(totalOriginal - total_debt)}</span>
                <span>Rimanente: {formatAmount(total_debt)}</span>
              </div>
            </div>

            {/* Key metrics */}
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-card border rounded-lg p-3 space-y-1">
                <div className="flex items-center gap-1 text-muted-foreground text-xs">
                  <Banknote className="w-3 h-3" />
                  Debito Totale
                </div>
                <p className="text-lg font-bold text-expense">
                  {formatAmount(total_debt)}
                </p>
              </div>
              <div className="bg-card border rounded-lg p-3 space-y-1">
                <div className="flex items-center gap-1 text-muted-foreground text-xs">
                  <TrendingDown className="w-3 h-3" />
                  Rata Mensile
                </div>
                <p className="text-lg font-bold">
                  {formatAmount(total_monthly_payment)}
                </p>
              </div>
            </div>

            {/* Freedom date */}
            {projected_debt_free_date && (
              <div className="bg-primary/10 border border-primary/20 rounded-lg p-3">
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-primary" />
                  <div>
                    <p className="text-sm font-medium">
                      Debt Free: {formatDate(projected_debt_free_date)}
                    </p>
                    {months_to_freedom && (
                      <p className="text-xs text-muted-foreground">
                        Tra {months_to_freedom} mesi
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-6">
            <Trophy className="w-12 h-12 text-income mx-auto mb-3" />
            <h3 className="font-bold text-lg text-income">Congratulazioni!</h3>
            <p className="text-sm text-muted-foreground">
              Sei libero dai debiti. Continua così!
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
