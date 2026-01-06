"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Lightbulb, Zap, Clock, CheckCircle2, ChevronRight } from "lucide-react";
import { useState } from "react";

interface RecommendationItem {
  id: string;
  title: string;
  description: string;
  impact_monthly: number;
  impact_annual: number;
  difficulty: "easy" | "medium" | "hard";
  category: string;
  action_steps: string[];
  priority: number;
}

interface RecommendationsListProps {
  data?: RecommendationItem[];
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

const difficultyConfig = {
  easy: {
    label: "Facile",
    icon: "5 min",
    bgColor: "bg-emerald-500/20",
    textColor: "text-emerald-400",
  },
  medium: {
    label: "Media",
    icon: "30 min",
    bgColor: "bg-yellow-500/20",
    textColor: "text-yellow-400",
  },
  hard: {
    label: "Difficile",
    icon: "giorni",
    bgColor: "bg-red-500/20",
    textColor: "text-red-400",
  },
};

const categoryConfig: Record<string, { label: string; color: string }> = {
  subscriptions: { label: "Abbonamenti", color: "bg-purple-500/20 text-purple-400" },
  spending: { label: "Spese", color: "bg-blue-500/20 text-blue-400" },
  debt: { label: "Debiti", color: "bg-red-500/20 text-red-400" },
  income: { label: "Entrate", color: "bg-emerald-500/20 text-emerald-400" },
};

function RecommendationCard({ rec, expanded, onToggle }: {
  rec: RecommendationItem;
  expanded: boolean;
  onToggle: () => void;
}) {
  const diffConfig = difficultyConfig[rec.difficulty];
  const catConfig = categoryConfig[rec.category] || { label: rec.category, color: "bg-muted text-muted-foreground" };

  return (
    <div
      className={`p-4 rounded-lg border transition-all cursor-pointer hover:border-primary/50 ${
        rec.priority === 1 ? "border-emerald-500/30 bg-emerald-500/5" : "border-border bg-muted/20"
      }`}
      onClick={onToggle}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            {rec.priority === 1 && (
              <Zap className="h-4 w-4 text-yellow-400 flex-shrink-0" />
            )}
            <span className="font-medium text-foreground">{rec.title}</span>
            <Badge variant="outline" className={`text-xs ${catConfig.color}`}>
              {catConfig.label}
            </Badge>
            <Badge variant="outline" className={`text-xs ${diffConfig.bgColor} ${diffConfig.textColor}`}>
              <Clock className="h-3 w-3 mr-1" />
              {diffConfig.icon}
            </Badge>
          </div>
          <p className="text-sm text-muted-foreground mt-1">{rec.description}</p>
        </div>

        <div className="text-right flex-shrink-0">
          {rec.impact_monthly > 0 && (
            <div className="text-lg font-bold text-emerald-400">
              +{formatCurrency(rec.impact_monthly)}/m
            </div>
          )}
          {rec.impact_annual > 0 && (
            <div className="text-xs text-muted-foreground">
              {formatCurrency(rec.impact_annual)}/anno
            </div>
          )}
          <ChevronRight
            className={`h-5 w-5 text-muted-foreground mt-1 transition-transform ${
              expanded ? "rotate-90" : ""
            }`}
          />
        </div>
      </div>

      {/* Expanded Action Steps */}
      {expanded && rec.action_steps.length > 0 && (
        <div className="mt-4 pt-4 border-t border-border/50">
          <div className="text-xs font-medium text-muted-foreground mb-2">
            PASSI DA SEGUIRE
          </div>
          <ol className="space-y-2">
            {rec.action_steps.map((step, index) => (
              <li key={index} className="flex items-start gap-3 text-sm">
                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-primary/20 text-xs font-medium text-primary flex-shrink-0">
                  {index + 1}
                </span>
                <span className="text-muted-foreground">{step}</span>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}

export function RecommendationsList({ data, isLoading }: RecommendationsListProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [filter, setFilter] = useState<"all" | "easy" | "medium" | "hard">("all");

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Raccomandazioni</CardTitle>
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

  const recommendations = data || [];
  const filtered = filter === "all"
    ? recommendations
    : recommendations.filter(r => r.difficulty === filter);

  const totalImpact = recommendations.reduce((sum, r) => sum + r.impact_monthly, 0);
  const easyCount = recommendations.filter(r => r.difficulty === "easy").length;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Lightbulb className="h-5 w-5 text-yellow-400" />
            Raccomandazioni
          </CardTitle>
          <div className="text-right">
            <div className="text-xs text-muted-foreground">Risparmio Totale</div>
            <div className="text-lg font-bold text-emerald-400">
              +{formatCurrency(totalImpact)}/m
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="flex items-center gap-2 mt-3">
          <Badge
            variant={filter === "all" ? "default" : "outline"}
            className="cursor-pointer"
            onClick={() => setFilter("all")}
          >
            Tutte ({recommendations.length})
          </Badge>
          <Badge
            variant={filter === "easy" ? "default" : "outline"}
            className={`cursor-pointer ${filter !== "easy" ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30" : ""}`}
            onClick={() => setFilter("easy")}
          >
            Facili ({easyCount})
          </Badge>
          <Badge
            variant={filter === "medium" ? "default" : "outline"}
            className={`cursor-pointer ${filter !== "medium" ? "bg-yellow-500/20 text-yellow-400 border-yellow-500/30" : ""}`}
            onClick={() => setFilter("medium")}
          >
            Medie ({recommendations.filter(r => r.difficulty === "medium").length})
          </Badge>
          <Badge
            variant={filter === "hard" ? "default" : "outline"}
            className={`cursor-pointer ${filter !== "hard" ? "bg-red-500/20 text-red-400 border-red-500/30" : ""}`}
            onClick={() => setFilter("hard")}
          >
            Difficili ({recommendations.filter(r => r.difficulty === "hard").length})
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-3">
        {filtered.map((rec) => (
          <RecommendationCard
            key={rec.id}
            rec={rec}
            expanded={expandedId === rec.id}
            onToggle={() => setExpandedId(expandedId === rec.id ? null : rec.id)}
          />
        ))}

        {filtered.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            <CheckCircle2 className="h-12 w-12 mx-auto mb-2 text-emerald-400" />
            <p>Nessuna raccomandazione per questo filtro</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
