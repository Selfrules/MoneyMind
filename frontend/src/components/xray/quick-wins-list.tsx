"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import {
  Zap,
  Clock,
  TrendingUp,
  ChevronRight,
  CheckCircle,
  X,
  Sparkles,
} from "lucide-react";

interface QuickWin {
  id: string;
  type: string;
  title: string;
  description: string;
  estimated_savings_monthly: number;
  estimated_savings_annual: number;
  payoff_impact_days: number;
  effort_level: string;
  time_to_complete: string;
  quick_win_score: number;
  confidence: number;
  action_steps: string[];
  cta_text: string;
  icon: string;
  priority_badge: string;
  category?: string;
  provider?: string;
}

interface QuickWinsListProps {
  wins?: QuickWin[];
  totalMonthlySavings?: number;
  totalAnnualSavings?: number;
  easyWinsCount?: number;
  isLoading?: boolean;
  onComplete?: (winId: string) => void;
  onDismiss?: (winId: string) => void;
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("it-IT", {
    style: "currency",
    currency: "EUR",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

function getEffortColor(effort: string): string {
  switch (effort) {
    case "trivial":
      return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
    case "easy":
      return "bg-green-500/20 text-green-400 border-green-500/30";
    case "medium":
      return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
    case "hard":
      return "bg-red-500/20 text-red-400 border-red-500/30";
    default:
      return "bg-muted text-muted-foreground border-border";
  }
}

function getEffortLabel(effort: string): string {
  switch (effort) {
    case "trivial":
      return "Super facile";
    case "easy":
      return "Facile";
    case "medium":
      return "Media";
    case "hard":
      return "Difficile";
    default:
      return effort;
  }
}

interface QuickWinCardProps {
  win: QuickWin;
  onComplete?: () => void;
  onDismiss?: () => void;
}

function QuickWinCard({ win, onComplete, onDismiss }: QuickWinCardProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="rounded-lg border border-border bg-card p-4 hover:border-primary/30 transition-colors">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3 flex-1">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-xl">
            {win.icon}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h4 className="text-sm font-medium text-foreground">{win.title}</h4>
              <Badge variant="outline" className={getEffortColor(win.effort_level)}>
                {getEffortLabel(win.effort_level)}
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
              {win.description}
            </p>
          </div>
        </div>
        <div className="text-right shrink-0">
          <div className="text-lg font-bold text-emerald-400">
            {formatCurrency(win.estimated_savings_monthly)}
          </div>
          <div className="text-xs text-muted-foreground">/mese</div>
        </div>
      </div>

      {/* Metrics */}
      <div className="flex items-center gap-4 mt-3 text-xs text-muted-foreground">
        <div className="flex items-center gap-1">
          <Clock className="h-3.5 w-3.5" />
          <span>{win.time_to_complete}</span>
        </div>
        {win.payoff_impact_days > 0 && (
          <div className="flex items-center gap-1">
            <TrendingUp className="h-3.5 w-3.5 text-emerald-400" />
            <span className="text-emerald-400">{win.payoff_impact_days} giorni prima</span>
          </div>
        )}
        <div className="flex items-center gap-1">
          <Sparkles className="h-3.5 w-3.5" />
          <span>Score: {win.quick_win_score.toFixed(0)}</span>
        </div>
      </div>

      {/* Confidence bar */}
      <div className="mt-3">
        <div className="flex items-center justify-between text-xs mb-1">
          <span className="text-muted-foreground">Confidenza stima</span>
          <span className="text-foreground">{(win.confidence * 100).toFixed(0)}%</span>
        </div>
        <Progress value={win.confidence * 100} className="h-1.5" />
      </div>

      {/* Expand/Collapse */}
      <Button
        variant="ghost"
        size="sm"
        className="w-full mt-3 text-xs"
        onClick={() => setExpanded(!expanded)}
      >
        {expanded ? "Nascondi dettagli" : "Mostra come fare"}
        <ChevronRight className={`h-4 w-4 ml-1 transition-transform ${expanded ? "rotate-90" : ""}`} />
      </Button>

      {/* Expanded content */}
      {expanded && (
        <div className="mt-3 pt-3 border-t border-border">
          <div className="text-xs font-medium text-foreground mb-2">Come procedere:</div>
          <ol className="space-y-2">
            {win.action_steps.map((step, index) => (
              <li key={index} className="flex items-start gap-2 text-xs text-muted-foreground">
                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-primary/20 text-primary shrink-0">
                  {index + 1}
                </span>
                <span>{step}</span>
              </li>
            ))}
          </ol>

          {/* Actions */}
          <div className="flex items-center gap-2 mt-4">
            <Button size="sm" className="flex-1" onClick={onComplete}>
              <CheckCircle className="h-4 w-4 mr-1.5" />
              {win.cta_text}
            </Button>
            <Button variant="outline" size="sm" onClick={onDismiss}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

export function QuickWinsList({
  wins = [],
  totalMonthlySavings = 0,
  totalAnnualSavings = 0,
  easyWinsCount = 0,
  isLoading,
  onComplete,
  onDismiss,
}: QuickWinsListProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Quick Wins
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-32 bg-muted animate-pulse rounded-lg" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (wins.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Quick Wins
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Sparkles className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-muted-foreground">
              Nessun quick win disponibile al momento.
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Continua a tracciare le tue spese per sbloccare opportunità!
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Zap className="h-5 w-5 text-yellow-400" />
            Quick Wins
          </CardTitle>
          <Badge variant="outline" className="bg-yellow-500/10 text-yellow-400 border-yellow-500/30">
            {easyWinsCount} facili
          </Badge>
        </div>
        {/* Summary */}
        <div className="flex items-center gap-4 mt-2 text-sm">
          <div>
            <span className="text-muted-foreground">Risparmio potenziale:</span>
            <span className="font-semibold text-emerald-400 ml-1.5">
              {formatCurrency(totalMonthlySavings)}/mese
            </span>
          </div>
          <div className="text-muted-foreground">
            ({formatCurrency(totalAnnualSavings)}/anno)
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {wins.map((win) => (
            <QuickWinCard
              key={win.id}
              win={win}
              onComplete={() => onComplete?.(win.id)}
              onDismiss={() => onDismiss?.(win.id)}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
