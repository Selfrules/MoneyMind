"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { JudgmentBadge } from "./judgment-badge";
import { TrendingUp, TrendingDown, Wallet, CreditCard, PiggyBank, Calendar, AlertTriangle, CheckCircle2 } from "lucide-react";

interface ExecutiveSummaryData {
  health_score: number;
  health_grade: string;
  total_income: number;
  total_expenses: number;
  net_savings: number;
  savings_rate: number;
  total_debt: number;
  debt_payment_monthly: number;
  months_to_debt_free: number | null;
  overall_judgment: "excellent" | "good" | "warning" | "critical";
  key_issues: string[];
  key_wins: string[];
}

interface ExecutiveSummaryProps {
  data?: ExecutiveSummaryData;
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

function getGradeColor(grade: string): string {
  switch (grade) {
    case "A": return "text-emerald-400";
    case "B": return "text-green-400";
    case "C": return "text-yellow-400";
    case "D": return "text-orange-400";
    case "F": return "text-red-400";
    default: return "text-muted-foreground";
  }
}

function getScoreRingColor(score: number): string {
  if (score >= 80) return "stroke-emerald-500";
  if (score >= 65) return "stroke-green-500";
  if (score >= 50) return "stroke-yellow-500";
  if (score >= 35) return "stroke-orange-500";
  return "stroke-red-500";
}

export function ExecutiveSummary({ data, isLoading }: ExecutiveSummaryProps) {
  if (isLoading) {
    return (
      <Card className="bg-gradient-to-br from-card to-card/50">
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-6">
            <div className="h-32 w-32 bg-muted animate-pulse rounded-full mx-auto md:mx-0" />
            <div className="flex-1 space-y-4">
              <div className="h-8 bg-muted animate-pulse rounded w-1/2" />
              <div className="grid grid-cols-2 gap-4">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="h-16 bg-muted animate-pulse rounded-lg" />
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const defaultData: ExecutiveSummaryData = data || {
    health_score: 0,
    health_grade: "F",
    total_income: 0,
    total_expenses: 0,
    net_savings: 0,
    savings_rate: 0,
    total_debt: 0,
    debt_payment_monthly: 0,
    months_to_debt_free: null,
    overall_judgment: "warning",
    key_issues: [],
    key_wins: [],
  };

  const circumference = 2 * Math.PI * 45;
  const strokeDashoffset = circumference - (defaultData.health_score / 100) * circumference;

  return (
    <Card className="bg-gradient-to-br from-card to-card/50 border-border/50">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-xl font-bold">Executive Summary</CardTitle>
          <JudgmentBadge judgment={defaultData.overall_judgment} size="md" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Freedom Score Ring */}
          <div className="flex flex-col items-center">
            <div className="relative w-32 h-32">
              <svg className="w-full h-full transform -rotate-90">
                <circle
                  cx="64"
                  cy="64"
                  r="45"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="8"
                  className="text-muted/30"
                />
                <circle
                  cx="64"
                  cy="64"
                  r="45"
                  fill="none"
                  strokeWidth="8"
                  strokeLinecap="round"
                  strokeDasharray={circumference}
                  strokeDashoffset={strokeDashoffset}
                  className={`${getScoreRingColor(defaultData.health_score)} transition-all duration-1000`}
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className={`text-3xl font-bold ${getGradeColor(defaultData.health_grade)}`}>
                  {defaultData.health_grade}
                </span>
                <span className="text-sm text-muted-foreground">{defaultData.health_score}/100</span>
              </div>
            </div>
            <span className="mt-2 text-sm font-medium text-muted-foreground">Freedom Score</span>
          </div>

          {/* KPI Grid */}
          <div className="flex-1 grid grid-cols-2 md:grid-cols-4 gap-4">
            {/* Income */}
            <div className="bg-muted/30 rounded-lg p-3">
              <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
                <TrendingUp className="h-3.5 w-3.5 text-emerald-400" />
                Entrate
              </div>
              <div className="text-lg font-bold text-emerald-400">
                {formatCurrency(defaultData.total_income)}
              </div>
            </div>

            {/* Expenses */}
            <div className="bg-muted/30 rounded-lg p-3">
              <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
                <TrendingDown className="h-3.5 w-3.5 text-red-400" />
                Uscite
              </div>
              <div className="text-lg font-bold text-red-400">
                {formatCurrency(defaultData.total_expenses)}
              </div>
            </div>

            {/* Savings Rate */}
            <div className="bg-muted/30 rounded-lg p-3">
              <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
                <PiggyBank className="h-3.5 w-3.5 text-emerald-400" />
                Savings Rate
              </div>
              <div className={`text-lg font-bold ${defaultData.savings_rate >= 20 ? "text-emerald-400" : defaultData.savings_rate >= 10 ? "text-yellow-400" : "text-red-400"}`}>
                {defaultData.savings_rate.toFixed(1)}%
              </div>
            </div>

            {/* Net Savings */}
            <div className="bg-muted/30 rounded-lg p-3">
              <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
                <Wallet className="h-3.5 w-3.5" />
                Risparmio Netto
              </div>
              <div className={`text-lg font-bold ${defaultData.net_savings >= 0 ? "text-emerald-400" : "text-red-400"}`}>
                {formatCurrency(defaultData.net_savings)}
              </div>
            </div>

            {/* Total Debt */}
            <div className="bg-muted/30 rounded-lg p-3">
              <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
                <CreditCard className="h-3.5 w-3.5 text-red-400" />
                Debito Totale
              </div>
              <div className="text-lg font-bold text-foreground">
                {formatCurrency(defaultData.total_debt)}
              </div>
            </div>

            {/* Monthly Debt Payment */}
            <div className="bg-muted/30 rounded-lg p-3">
              <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
                <CreditCard className="h-3.5 w-3.5" />
                Rata Debiti
              </div>
              <div className="text-lg font-bold text-foreground">
                {formatCurrency(defaultData.debt_payment_monthly)}/m
              </div>
            </div>

            {/* Months to Debt Free */}
            <div className="bg-muted/30 rounded-lg p-3 col-span-2">
              <div className="flex items-center gap-2 text-xs text-muted-foreground mb-1">
                <Calendar className="h-3.5 w-3.5" />
                Debt-Free in
              </div>
              <div className="text-lg font-bold text-foreground">
                {defaultData.months_to_debt_free
                  ? `${defaultData.months_to_debt_free} mesi (${Math.floor(defaultData.months_to_debt_free / 12)} anni ${defaultData.months_to_debt_free % 12}m)`
                  : "N/A"}
              </div>
            </div>
          </div>
        </div>

        {/* Issues and Wins */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Key Issues */}
          {defaultData.key_issues.length > 0 && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
              <div className="flex items-center gap-2 text-sm font-medium text-red-400 mb-2">
                <AlertTriangle className="h-4 w-4" />
                Attenzione
              </div>
              <ul className="space-y-1">
                {defaultData.key_issues.map((issue, i) => (
                  <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                    <span className="text-red-400 mt-0.5">•</span>
                    {issue}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Key Wins */}
          {defaultData.key_wins.length > 0 && (
            <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-4">
              <div className="flex items-center gap-2 text-sm font-medium text-emerald-400 mb-2">
                <CheckCircle2 className="h-4 w-4" />
                Punti di Forza
              </div>
              <ul className="space-y-1">
                {defaultData.key_wins.map((win, i) => (
                  <li key={i} className="text-sm text-muted-foreground flex items-start gap-2">
                    <span className="text-emerald-400 mt-0.5">•</span>
                    {win}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
