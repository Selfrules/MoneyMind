"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import type { HealthScore } from "@/lib/api-types";

interface FreedomScoreProps {
  healthScore: HealthScore;
}

const gradeColors: Record<string, string> = {
  A: "text-green-500",
  B: "text-emerald-500",
  C: "text-yellow-500",
  D: "text-orange-500",
  F: "text-red-500",
};

export function FreedomScore({ healthScore }: FreedomScoreProps) {
  const gradeColor = gradeColors[healthScore.grade] || "text-muted-foreground";

  return (
    <Card className="bg-gradient-to-br from-primary/10 to-primary/5 border-primary/20">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-medium">Freedom Score</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-baseline gap-2">
            <span className="text-5xl font-bold text-primary">
              {healthScore.total_score}
            </span>
            <span className="text-muted-foreground">/100</span>
          </div>
          <div className="text-right">
            <span className={`text-3xl font-bold ${gradeColor}`}>
              {healthScore.grade}
            </span>
            <p className="text-xs text-muted-foreground">{healthScore.phase}</p>
          </div>
        </div>

        <Progress value={healthScore.total_score} className="h-2 mb-4" />

        <div className="grid grid-cols-2 gap-3 text-sm">
          <ScoreItem
            label="Risparmio"
            score={healthScore.savings_score}
            max={25}
          />
          <ScoreItem
            label="DTI"
            score={healthScore.dti_score}
            max={25}
          />
          <ScoreItem
            label="Fondo Emergenza"
            score={healthScore.emergency_fund_score}
            max={25}
          />
          <ScoreItem
            label="Trend Patrimonio"
            score={healthScore.net_worth_trend_score}
            max={25}
          />
        </div>
      </CardContent>
    </Card>
  );
}

function ScoreItem({
  label,
  score,
  max,
}: {
  label: string;
  score: number;
  max: number;
}) {
  const percentage = (score / max) * 100;

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-medium">
          {score}/{max}
        </span>
      </div>
      <Progress value={percentage} className="h-1" />
    </div>
  );
}
