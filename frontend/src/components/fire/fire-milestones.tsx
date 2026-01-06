"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Flag,
  CheckCircle,
  Circle,
  Coffee,
  Leaf,
  Sparkles,
  Calendar,
} from "lucide-react";
import type { FIREMilestone } from "@/lib/api";

interface FIREMilestonesProps {
  milestones?: FIREMilestone[];
  currentNetWorth?: number;
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
  return date.toLocaleDateString("it-IT", { month: "short", year: "numeric" });
}

function getMilestoneIcon(name: string) {
  switch (name) {
    case "Coast FI":
      return <Coffee className="h-4 w-4" />;
    case "Barista FI":
      return <Coffee className="h-4 w-4" />;
    case "Lean FI":
      return <Leaf className="h-4 w-4" />;
    case "Full FI":
      return <Sparkles className="h-4 w-4" />;
    default:
      return <Flag className="h-4 w-4" />;
  }
}

function getMilestoneColor(name: string, isAchieved: boolean) {
  if (isAchieved) return "bg-emerald-500/10 border-emerald-500/30 text-emerald-400";

  switch (name) {
    case "Coast FI":
      return "bg-blue-500/10 border-blue-500/30 text-blue-400";
    case "Barista FI":
      return "bg-purple-500/10 border-purple-500/30 text-purple-400";
    case "Lean FI":
      return "bg-amber-500/10 border-amber-500/30 text-amber-400";
    case "Full FI":
      return "bg-orange-500/10 border-orange-500/30 text-orange-400";
    default:
      return "bg-muted border-border text-muted-foreground";
  }
}

export function FIREMilestones({
  milestones,
  currentNetWorth = 0,
  isLoading,
}: FIREMilestonesProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Flag className="h-5 w-5" />
            Milestones FI
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-20 bg-muted animate-pulse rounded-lg" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!milestones || milestones.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Flag className="h-5 w-5" />
            Milestones FI
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-center py-4">
            Nessun milestone calcolato
          </p>
        </CardContent>
      </Card>
    );
  }

  const achievedCount = milestones.filter((m) => m.is_achieved).length;

  return (
    <Card>
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Flag className="h-5 w-5 text-primary" />
            Milestones FI
          </CardTitle>
          <Badge variant="outline">
            {achievedCount}/{milestones.length} raggiunti
          </Badge>
        </div>
      </CardHeader>

      <CardContent>
        <div className="space-y-4">
          {milestones.map((milestone, index) => {
            const progress = currentNetWorth > 0
              ? Math.min((currentNetWorth / milestone.target_amount) * 100, 100)
              : 0;

            return (
              <div
                key={milestone.name}
                className={`rounded-lg border p-4 ${getMilestoneColor(milestone.name, milestone.is_achieved)}`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {milestone.is_achieved ? (
                      <CheckCircle className="h-5 w-5 text-emerald-400" />
                    ) : (
                      getMilestoneIcon(milestone.name)
                    )}
                    <div>
                      <div className="font-medium text-foreground">
                        {milestone.name}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {milestone.description}
                      </div>
                    </div>
                  </div>
                  <Badge
                    variant="outline"
                    className={milestone.is_achieved ? "bg-emerald-500/20" : ""}
                  >
                    {milestone.target_percent}%
                  </Badge>
                </div>

                <div className="space-y-2">
                  {/* Progress bar */}
                  <Progress
                    value={progress}
                    className={`h-2 ${milestone.is_achieved ? "[&>div]:bg-emerald-500" : ""}`}
                  />

                  <div className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground">
                      {formatCurrency(milestone.target_amount)}
                    </span>
                    {milestone.is_achieved ? (
                      <span className="text-emerald-400 font-medium">
                        Raggiunto!
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 text-muted-foreground">
                        <Calendar className="h-3 w-3" />
                        {milestone.years_to_reach.toFixed(1)} anni ({formatDate(milestone.projected_date)})
                      </span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Legend */}
        <div className="mt-4 pt-4 border-t border-border">
          <div className="text-xs text-muted-foreground space-y-1">
            <div className="flex items-center gap-2">
              <Coffee className="h-3 w-3" />
              <strong>Coast FI:</strong> Smetti di risparmiare, raggiungi FI a 65 anni
            </div>
            <div className="flex items-center gap-2">
              <Coffee className="h-3 w-3" />
              <strong>Barista FI:</strong> Lavoro part-time copre le spese
            </div>
            <div className="flex items-center gap-2">
              <Leaf className="h-3 w-3" />
              <strong>Lean FI:</strong> FI con stile di vita minimalista
            </div>
            <div className="flex items-center gap-2">
              <Sparkles className="h-3 w-3" />
              <strong>Full FI:</strong> Indipendenza finanziaria completa
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
