"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import type { Goal } from "@/lib/api-types";
import {
  Target,
  PiggyBank,
  Shield,
  Sparkles,
  Calendar,
  CheckCircle,
  Pause,
} from "lucide-react";

interface GoalCardProps {
  goal: Goal;
}

function formatAmount(amount: number): string {
  return new Intl.NumberFormat("it-IT", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(amount);
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "—";
  const date = new Date(dateStr);
  return date.toLocaleDateString("it-IT", {
    month: "short",
    year: "numeric",
  });
}

function getGoalIcon(type: string) {
  switch (type.toLowerCase()) {
    case "emergency_fund":
    case "emergenza":
      return <Shield className="w-5 h-5 text-warning" />;
    case "savings":
    case "risparmio":
      return <PiggyBank className="w-5 h-5 text-income" />;
    default:
      return <Sparkles className="w-5 h-5 text-primary" />;
  }
}

function getStatusBadge(status: string) {
  switch (status.toLowerCase()) {
    case "completed":
      return (
        <Badge className="text-xs bg-income/20 text-income border-income/30">
          <CheckCircle className="w-3 h-3 mr-1" />
          Completato
        </Badge>
      );
    case "paused":
      return (
        <Badge variant="outline" className="text-xs text-muted-foreground">
          <Pause className="w-3 h-3 mr-1" />
          In pausa
        </Badge>
      );
    default:
      return (
        <Badge variant="outline" className="text-xs text-primary border-primary/30">
          <Target className="w-3 h-3 mr-1" />
          Attivo
        </Badge>
      );
  }
}

export function GoalCard({ goal }: GoalCardProps) {
  const isCompleted = goal.status === "completed" || goal.progress_percent >= 100;

  return (
    <Card className={isCompleted ? "border-income/30" : undefined}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {getGoalIcon(goal.type)}
            <CardTitle className="text-base">{goal.name}</CardTitle>
          </div>
          {getStatusBadge(goal.status)}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Progress */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Progresso</span>
            <span className="font-medium">{goal.progress_percent.toFixed(0)}%</span>
          </div>
          <Progress
            value={Math.min(goal.progress_percent, 100)}
            className={`h-2 ${isCompleted ? "[&>div]:bg-income" : ""}`}
          />
        </div>

        {/* Amounts */}
        <div className="flex justify-between items-center">
          <div>
            <p className="text-2xl font-bold">{formatAmount(goal.current_amount)}</p>
            <p className="text-xs text-muted-foreground">
              di {formatAmount(goal.target_amount)}
            </p>
          </div>
          <div className="text-right">
            {goal.target_date && (
              <div className="flex items-center gap-1 text-xs text-muted-foreground">
                <Calendar className="w-3 h-3" />
                <span>Obiettivo: {formatDate(goal.target_date)}</span>
              </div>
            )}
            {goal.months_remaining && goal.monthly_contribution_needed && (
              <p className="text-xs text-muted-foreground mt-1">
                {formatAmount(goal.monthly_contribution_needed)}/mese per {goal.months_remaining} mesi
              </p>
            )}
          </div>
        </div>

        {/* Remaining amount */}
        {!isCompleted && (
          <div className="bg-muted/50 rounded-lg px-3 py-2">
            <p className="text-xs text-muted-foreground">
              Mancano ancora{" "}
              <span className="font-medium text-foreground">
                {formatAmount(goal.target_amount - goal.current_amount)}
              </span>
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
