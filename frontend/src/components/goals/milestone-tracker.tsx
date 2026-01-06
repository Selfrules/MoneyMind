"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import {
  Trophy,
  Target,
  CheckCircle,
  Circle,
  Clock,
  Calendar,
  ChevronDown,
  ChevronUp,
  Sparkles,
  PartyPopper,
} from "lucide-react";

interface Milestone {
  id: number;
  goal_id: number;
  milestone_number: number;
  title: string;
  description?: string;
  target_amount?: number;
  target_date?: string;
  status: "pending" | "achieved" | "missed";
  achieved_at?: string;
  actual_amount?: number;
  celebration_shown: boolean;
  goal_name?: string;
}

interface MilestoneTrackerProps {
  milestones: Milestone[];
  goalName: string;
  targetAmount?: number;
  currentAmount?: number;
  isLoading?: boolean;
  onAchieve?: (milestoneId: number, actualAmount?: number) => void;
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
  return date.toLocaleDateString("it-IT", { day: "numeric", month: "short", year: "numeric" });
}

function getStatusColor(status: string): string {
  switch (status) {
    case "achieved":
      return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
    case "missed":
      return "bg-red-500/20 text-red-400 border-red-500/30";
    default:
      return "bg-muted text-muted-foreground border-border";
  }
}

function MilestoneCard({
  milestone,
  isNext,
  onAchieve,
}: {
  milestone: Milestone;
  isNext: boolean;
  onAchieve?: () => void;
}) {
  const isAchieved = milestone.status === "achieved";
  const isMissed = milestone.status === "missed";

  return (
    <div
      className={`relative flex items-start gap-4 p-4 rounded-lg border transition-colors ${
        isAchieved
          ? "border-emerald-500/30 bg-emerald-500/5"
          : isNext
            ? "border-primary/30 bg-primary/5"
            : "border-border bg-card"
      }`}
    >
      {/* Milestone Number/Status Icon */}
      <div
        className={`flex h-10 w-10 items-center justify-center rounded-full shrink-0 ${
          isAchieved
            ? "bg-emerald-500/20 text-emerald-400"
            : isNext
              ? "bg-primary/20 text-primary"
              : "bg-muted text-muted-foreground"
        }`}
      >
        {isAchieved ? (
          <CheckCircle className="h-5 w-5" />
        ) : (
          <span className="font-bold">{milestone.milestone_number}</span>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <div>
            <h4 className={`font-medium ${isAchieved ? "text-emerald-400" : "text-foreground"}`}>
              {milestone.title}
            </h4>
            {milestone.description && (
              <p className="text-sm text-muted-foreground mt-0.5">{milestone.description}</p>
            )}
          </div>
          <Badge variant="outline" className={getStatusColor(milestone.status)}>
            {isAchieved ? "Raggiunto" : isMissed ? "Mancato" : isNext ? "Prossimo" : "In attesa"}
          </Badge>
        </div>

        {/* Metrics */}
        <div className="flex items-center gap-4 mt-3 text-xs">
          {milestone.target_amount && (
            <div className="flex items-center gap-1 text-muted-foreground">
              <Target className="h-3.5 w-3.5" />
              <span>
                {isAchieved && milestone.actual_amount
                  ? formatCurrency(milestone.actual_amount)
                  : formatCurrency(milestone.target_amount)}
              </span>
            </div>
          )}
          {milestone.target_date && !isAchieved && (
            <div className="flex items-center gap-1 text-muted-foreground">
              <Calendar className="h-3.5 w-3.5" />
              <span>{formatDate(milestone.target_date)}</span>
            </div>
          )}
          {milestone.achieved_at && (
            <div className="flex items-center gap-1 text-emerald-400">
              <CheckCircle className="h-3.5 w-3.5" />
              <span>Raggiunto il {formatDate(milestone.achieved_at)}</span>
            </div>
          )}
        </div>

        {/* Action for next milestone */}
        {isNext && !isAchieved && onAchieve && (
          <Button size="sm" className="mt-3" onClick={onAchieve}>
            <CheckCircle className="h-4 w-4 mr-1.5" />
            Segna come raggiunto
          </Button>
        )}
      </div>
    </div>
  );
}

export function MilestoneTracker({
  milestones,
  goalName,
  targetAmount,
  currentAmount,
  isLoading,
  onAchieve,
}: MilestoneTrackerProps) {
  const [expanded, setExpanded] = useState(false);

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Trophy className="h-5 w-5" />
            Milestone
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-24 bg-muted animate-pulse rounded-lg" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const achievedCount = milestones.filter((m) => m.status === "achieved").length;
  const nextMilestone = milestones.find((m) => m.status === "pending");
  const overallProgress = milestones.length > 0 ? (achievedCount / milestones.length) * 100 : 0;

  // Show only first 3 if not expanded
  const displayMilestones = expanded ? milestones : milestones.slice(0, 3);

  if (milestones.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Trophy className="h-5 w-5" />
            Milestone - {goalName}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Target className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground">Nessun milestone definito per questo obiettivo.</p>
            <p className="text-xs text-muted-foreground mt-1">
              I milestone ti aiutano a tracciare il progresso verso il tuo obiettivo.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Trophy className="h-5 w-5 text-yellow-400" />
            {goalName}
          </CardTitle>
          <Badge variant="outline" className="bg-primary/10 text-primary">
            {achievedCount}/{milestones.length}
          </Badge>
        </div>

        {/* Overall progress */}
        <div className="mt-3">
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-muted-foreground">Progresso milestone</span>
            <span className="font-medium text-foreground">{overallProgress.toFixed(0)}%</span>
          </div>
          <Progress value={overallProgress} className="h-2" />
        </div>

        {/* Amount progress if applicable */}
        {targetAmount && currentAmount !== undefined && (
          <div className="mt-3 flex items-center gap-3 text-sm">
            <span className="text-muted-foreground">Importo:</span>
            <span className="font-medium text-foreground">{formatCurrency(currentAmount)}</span>
            <span className="text-muted-foreground">/</span>
            <span className="text-muted-foreground">{formatCurrency(targetAmount)}</span>
          </div>
        )}
      </CardHeader>

      <CardContent>
        {/* Next milestone highlight */}
        {nextMilestone && (
          <div className="mb-4 p-3 rounded-lg bg-primary/5 border border-primary/20">
            <div className="flex items-center gap-2 text-sm text-primary mb-1">
              <Sparkles className="h-4 w-4" />
              <span className="font-medium">Prossimo traguardo</span>
            </div>
            <p className="text-foreground font-medium">{nextMilestone.title}</p>
            {nextMilestone.target_amount && (
              <p className="text-sm text-muted-foreground mt-0.5">
                Obiettivo: {formatCurrency(nextMilestone.target_amount)}
              </p>
            )}
          </div>
        )}

        {/* Milestone list */}
        <div className="space-y-3">
          {displayMilestones.map((milestone) => (
            <MilestoneCard
              key={milestone.id}
              milestone={milestone}
              isNext={milestone.id === nextMilestone?.id}
              onAchieve={onAchieve ? () => onAchieve(milestone.id) : undefined}
            />
          ))}
        </div>

        {/* Expand/Collapse */}
        {milestones.length > 3 && (
          <Button
            variant="ghost"
            size="sm"
            className="w-full mt-4 text-xs"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? "Mostra meno" : `Mostra tutti (${milestones.length})`}
            {expanded ? (
              <ChevronUp className="h-4 w-4 ml-1" />
            ) : (
              <ChevronDown className="h-4 w-4 ml-1" />
            )}
          </Button>
        )}

        {/* Celebration for completed goal */}
        {achievedCount === milestones.length && milestones.length > 0 && (
          <div className="mt-4 p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-center">
            <PartyPopper className="h-8 w-8 text-emerald-400 mx-auto mb-2" />
            <p className="font-medium text-emerald-400">Obiettivo completato!</p>
            <p className="text-sm text-muted-foreground mt-1">
              Hai raggiunto tutti i milestone di questo obiettivo.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
