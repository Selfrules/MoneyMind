"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { KPIHistoryResponse, HealthScore } from "@/lib/api-types";
import {
  TrendingUp,
  TrendingDown,
  Minus,
  Activity,
  Wallet,
  CreditCard,
  Shield,
  PiggyBank,
} from "lucide-react";

interface HealthKPIsProps {
  healthScore: HealthScore;
  kpiHistory?: KPIHistoryResponse;
}

function formatAmount(amount: number): string {
  return new Intl.NumberFormat("it-IT", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(amount);
}

function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}

function TrendIcon({ direction }: { direction: string }) {
  switch (direction) {
    case "improving":
      return <TrendingUp className="w-4 h-4 text-income" />;
    case "declining":
      return <TrendingDown className="w-4 h-4 text-expense" />;
    default:
      return <Minus className="w-4 h-4 text-muted-foreground" />;
  }
}

function getGradeColor(grade: string): string {
  switch (grade) {
    case "A":
      return "text-income";
    case "B":
      return "text-primary";
    case "C":
      return "text-warning";
    default:
      return "text-expense";
  }
}

function ScoreRing({ score, grade }: { score: number; grade: string }) {
  const circumference = 2 * Math.PI * 45;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="relative w-32 h-32 mx-auto">
      <svg className="w-full h-full transform -rotate-90">
        <circle
          cx="64"
          cy="64"
          r="45"
          fill="none"
          stroke="currentColor"
          strokeWidth="8"
          className="text-muted"
        />
        <circle
          cx="64"
          cy="64"
          r="45"
          fill="none"
          stroke="currentColor"
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          className={getGradeColor(grade)}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`text-3xl font-bold ${getGradeColor(grade)}`}>
          {grade}
        </span>
        <span className="text-sm text-muted-foreground">{score}/100</span>
      </div>
    </div>
  );
}

function KPIItem({
  icon,
  label,
  value,
  subValue,
  status,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  subValue?: string;
  status?: "good" | "warning" | "bad";
}) {
  const statusColor =
    status === "good"
      ? "text-income"
      : status === "warning"
      ? "text-warning"
      : status === "bad"
      ? "text-expense"
      : "text-foreground";

  return (
    <div className="flex items-center justify-between py-3 border-b border-border/50 last:border-0">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center">
          {icon}
        </div>
        <div>
          <p className="text-sm font-medium">{label}</p>
          {subValue && (
            <p className="text-xs text-muted-foreground">{subValue}</p>
          )}
        </div>
      </div>
      <span className={`font-semibold ${statusColor}`}>{value}</span>
    </div>
  );
}

export function HealthKPIs({ healthScore, kpiHistory }: HealthKPIsProps) {
  const getSavingsStatus = (rate: number): "good" | "warning" | "bad" => {
    if (rate >= 20) return "good";
    if (rate >= 10) return "warning";
    return "bad";
  };

  const getDTIStatus = (ratio: number): "good" | "warning" | "bad" => {
    if (ratio <= 20) return "good";
    if (ratio <= 36) return "warning";
    return "bad";
  };

  const getEmergencyStatus = (months: number): "good" | "warning" | "bad" => {
    if (months >= 6) return "good";
    if (months >= 3) return "warning";
    return "bad";
  };

  return (
    <div className="space-y-4">
      {/* Health Score Card */}
      <Card className="border-primary/20">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base flex items-center gap-2">
              <Activity className="w-5 h-5 text-primary" />
              Salute Finanziaria
            </CardTitle>
            {kpiHistory && (
              <Badge variant="outline" className="text-xs">
                <TrendIcon direction={kpiHistory.trend_direction} />
                <span className="ml-1 capitalize">
                  {kpiHistory.trend_direction === "improving"
                    ? "In miglioramento"
                    : kpiHistory.trend_direction === "declining"
                    ? "In calo"
                    : "Stabile"}
                </span>
              </Badge>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <ScoreRing score={healthScore.total_score} grade={healthScore.grade} />
          <div className="text-center mt-4">
            <Badge
              variant="outline"
              className={
                healthScore.phase === "Wealth Building"
                  ? "text-income border-income/30"
                  : "text-primary border-primary/30"
              }
            >
              {healthScore.phase === "Wealth Building"
                ? "🚀 Fase Crescita"
                : "💪 Fase Debiti"}
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* KPI Breakdown */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Dettaglio KPI</CardTitle>
        </CardHeader>
        <CardContent>
          <KPIItem
            icon={<PiggyBank className="w-4 h-4 text-primary" />}
            label="Tasso di Risparmio"
            value={formatPercent(healthScore.savings_score * 4)}
            subValue={`${healthScore.savings_score}/25 punti`}
            status={getSavingsStatus(healthScore.savings_score * 4)}
          />
          <KPIItem
            icon={<CreditCard className="w-4 h-4 text-primary" />}
            label="Rapporto Debiti/Reddito"
            value={formatPercent(healthScore.dti_score * 2)}
            subValue={`${healthScore.dti_score}/25 punti`}
            status={getDTIStatus(50 - healthScore.dti_score * 2)}
          />
          <KPIItem
            icon={<Shield className="w-4 h-4 text-primary" />}
            label="Fondo Emergenza"
            value={`${(healthScore.emergency_fund_score / 25 * 6).toFixed(1)} mesi`}
            subValue={`${healthScore.emergency_fund_score}/25 punti`}
            status={getEmergencyStatus(healthScore.emergency_fund_score / 25 * 6)}
          />
          <KPIItem
            icon={<Wallet className="w-4 h-4 text-primary" />}
            label="Trend Patrimonio"
            value={
              healthScore.net_worth_trend_score > 15
                ? "Positivo"
                : healthScore.net_worth_trend_score > 5
                ? "Stabile"
                : "Negativo"
            }
            subValue={`${healthScore.net_worth_trend_score}/25 punti`}
            status={
              healthScore.net_worth_trend_score > 15
                ? "good"
                : healthScore.net_worth_trend_score > 5
                ? "warning"
                : "bad"
            }
          />
        </CardContent>
      </Card>
    </div>
  );
}
