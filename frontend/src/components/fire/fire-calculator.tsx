"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Flame,
  Calendar,
  TrendingUp,
  PiggyBank,
  Target,
  Wallet,
  Percent,
} from "lucide-react";
import type { FIRESummaryResponse } from "@/lib/api";

interface FIRECalculatorProps {
  data?: FIRESummaryResponse;
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

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString("it-IT", { month: "long", year: "numeric" });
}

function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}

export function FIRECalculator({ data, isLoading }: FIRECalculatorProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Flame className="h-5 w-5 text-orange-500" />
            FIRE Calculator
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="h-24 bg-muted animate-pulse rounded-lg" />
            <div className="h-16 bg-muted animate-pulse rounded-lg" />
            <div className="h-16 bg-muted animate-pulse rounded-lg" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!data) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Flame className="h-5 w-5 text-orange-500" />
            FIRE Calculator
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-center py-8">
            Dati insufficienti per il calcolo FIRE
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Flame className="h-5 w-5 text-orange-500" />
            FIRE Calculator
          </CardTitle>
          <Badge variant="outline" className="bg-orange-500/10 text-orange-400 border-orange-500/30">
            {formatPercent(data.progress_percent)} verso FI
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Main Stats Grid */}
        <div className="grid grid-cols-2 gap-4">
          {/* FIRE Number */}
          <div className="rounded-lg bg-gradient-to-br from-orange-500/10 to-red-500/10 border border-orange-500/20 p-4">
            <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
              <Target className="h-3.5 w-3.5" />
              FIRE Number
            </div>
            <div className="text-2xl font-bold text-foreground">
              {formatCurrency(data.fire_number)}
            </div>
            <div className="text-xs text-muted-foreground">
              25x spese annuali
            </div>
          </div>

          {/* Years to FIRE */}
          <div className="rounded-lg bg-gradient-to-br from-blue-500/10 to-purple-500/10 border border-blue-500/20 p-4">
            <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
              <Calendar className="h-3.5 w-3.5" />
              Tempo a FI
            </div>
            <div className="text-2xl font-bold text-foreground">
              {data.years_to_fire.toFixed(1)} anni
            </div>
            <div className="text-xs text-muted-foreground">
              {formatDate(data.fire_date)}
            </div>
          </div>
        </div>

        {/* Progress Bar */}
        <div>
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-muted-foreground">Progresso verso FI</span>
            <span className="font-medium text-foreground">
              {formatPercent(data.progress_percent)}
            </span>
          </div>
          <Progress value={Math.min(data.progress_percent, 100)} className="h-3" />
          <div className="flex justify-between text-xs text-muted-foreground mt-1">
            <span>{formatCurrency(data.current_net_worth)}</span>
            <span>{formatCurrency(data.fire_number)}</span>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-3 gap-3">
          <div className="text-center p-3 rounded-lg bg-card border border-border">
            <Wallet className="h-4 w-4 mx-auto text-muted-foreground mb-1" />
            <div className="text-sm font-medium">{formatCurrency(data.monthly_investment)}</div>
            <div className="text-xs text-muted-foreground">Risparmio/mese</div>
          </div>
          <div className="text-center p-3 rounded-lg bg-card border border-border">
            <Percent className="h-4 w-4 mx-auto text-muted-foreground mb-1" />
            <div className="text-sm font-medium">{formatPercent(data.savings_rate)}</div>
            <div className="text-xs text-muted-foreground">Savings Rate</div>
          </div>
          <div className="text-center p-3 rounded-lg bg-card border border-border">
            <TrendingUp className="h-4 w-4 mx-auto text-muted-foreground mb-1" />
            <div className="text-sm font-medium">{formatPercent(data.expected_return * 100)}</div>
            <div className="text-xs text-muted-foreground">Rendimento</div>
          </div>
        </div>

        {/* Assumptions */}
        <div className="text-xs text-muted-foreground bg-muted/30 rounded-lg p-3">
          <div className="font-medium mb-1">Assunzioni:</div>
          <ul className="space-y-0.5">
            <li>• Rendimento annuo atteso: {formatPercent(data.expected_return * 100)}</li>
            <li>• Tasso di prelievo sicuro (SWR): {formatPercent(data.withdrawal_rate * 100)}</li>
            <li>• Spese annuali: {formatCurrency(data.annual_expenses)}</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}
