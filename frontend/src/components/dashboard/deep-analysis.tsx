"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { useDeepAnalysis, useQuickInsights } from "@/hooks/use-dashboard";
import type { DeepAnalysisResponse, QuickInsightsResponse } from "@/lib/api-types";

// Icons as inline components for simplicity
const BrainIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 5a3 3 0 1 0-5.997.125 4 4 0 0 0-2.526 5.77 4 4 0 0 0 .556 6.588A4 4 0 1 0 12 18Z"/>
    <path d="M12 5a3 3 0 1 1 5.997.125 4 4 0 0 1 2.526 5.77 4 4 0 0 1-.556 6.588A4 4 0 1 1 12 18Z"/>
    <path d="M15 13a4.5 4.5 0 0 1-3-4 4.5 4.5 0 0 1-3 4"/>
    <path d="M17.599 6.5a3 3 0 0 0 .399-1.375"/>
    <path d="M6.003 5.125A3 3 0 0 0 6.401 6.5"/>
    <path d="M3.477 10.896a4 4 0 0 1 .585-.396"/>
    <path d="M19.938 10.5a4 4 0 0 1 .585.396"/>
    <path d="M6 18a4 4 0 0 1-1.967-.516"/>
    <path d="M19.967 17.484A4 4 0 0 1 18 18"/>
  </svg>
);

const LoaderIcon = () => (
  <svg className="animate-spin" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
  </svg>
);

const recommendationColors: Record<string, string> = {
  keep: "bg-green-500/10 text-green-500 border-green-500/20",
  review: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
  cancel: "bg-red-500/10 text-red-500 border-red-500/20",
  negotiate: "bg-blue-500/10 text-blue-500 border-blue-500/20",
};

const typeIcons: Record<string, string> = {
  subscription: "🔄",
  service: "🛠️",
  financing: "🏦",
  essential: "✅",
};

const gradeColors: Record<string, string> = {
  A: "text-green-500",
  B: "text-emerald-500",
  C: "text-yellow-500",
  D: "text-orange-500",
  F: "text-red-500",
};

function getGrade(score: number): string {
  if (score >= 80) return "A";
  if (score >= 65) return "B";
  if (score >= 50) return "C";
  if (score >= 35) return "D";
  return "F";
}

export function DeepAnalysis() {
  const [showAnalysis, setShowAnalysis] = useState(false);
  const { data: analysis, isLoading, error, refetch } = useDeepAnalysis();
  const { data: quickInsights } = useQuickInsights();

  // Show quick insights by default (fast, no AI)
  if (!showAnalysis) {
    return (
      <Card>
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg font-medium flex items-center gap-2">
              <BrainIcon />
              Analisi AI
            </CardTitle>
            <Button
              size="sm"
              variant="outline"
              onClick={() => {
                setShowAnalysis(true);
                refetch();
              }}
              className="text-xs"
            >
              Analisi Completa
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {quickInsights ? (
            <QuickInsightsView data={quickInsights} />
          ) : (
            <p className="text-sm text-muted-foreground">
              Caricamento insights...
            </p>
          )}
        </CardContent>
      </Card>
    );
  }

  // Loading state for AI analysis
  if (isLoading) {
    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-lg font-medium flex items-center gap-2">
            <LoaderIcon />
            Analisi AI in corso...
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-8 space-y-4">
            <p className="text-sm text-muted-foreground text-center">
              L&apos;AI sta analizzando le tue transazioni...
              <br />
              <span className="text-xs">(10-30 secondi)</span>
            </p>
            <Progress value={33} className="w-48 h-2" />
          </div>
        </CardContent>
      </Card>
    );
  }

  // Error state
  if (error) {
    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-lg font-medium text-red-500">
            Errore Analisi
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            {error instanceof Error ? error.message : "Errore sconosciuto"}
          </p>
          <Button
            size="sm"
            variant="outline"
            onClick={() => {
              setShowAnalysis(false);
            }}
          >
            Torna agli Insights
          </Button>
        </CardContent>
      </Card>
    );
  }

  // Full analysis view
  if (analysis) {
    return <DeepAnalysisView data={analysis} onBack={() => setShowAnalysis(false)} />;
  }

  return null;
}

function QuickInsightsView({ data }: { data: QuickInsightsResponse }) {
  return (
    <div className="space-y-4">
      {/* Monthly Summary */}
      <div className="grid grid-cols-2 gap-3 text-sm">
        <div className="bg-card-foreground/5 rounded-lg p-3">
          <p className="text-xs text-muted-foreground">Media Entrate</p>
          <p className="font-semibold text-green-500">
            +{data.monthly_summary.avg_income.toLocaleString("it-IT", { style: "currency", currency: "EUR" })}
          </p>
        </div>
        <div className="bg-card-foreground/5 rounded-lg p-3">
          <p className="text-xs text-muted-foreground">Media Uscite</p>
          <p className="font-semibold text-red-500">
            -{data.monthly_summary.avg_expenses.toLocaleString("it-IT", { style: "currency", currency: "EUR" })}
          </p>
        </div>
      </div>

      {/* Insights List */}
      <div className="space-y-2">
        {data.insights.map((insight, index) => (
          <div
            key={index}
            className={`p-3 rounded-lg border ${
              insight.type === "positive"
                ? "bg-green-500/10 border-green-500/20"
                : insight.type === "warning"
                ? "bg-yellow-500/10 border-yellow-500/20"
                : "bg-card-foreground/5 border-transparent"
            }`}
          >
            <p className="text-sm font-medium">{insight.title}</p>
            <p className="text-xs text-muted-foreground">{insight.message}</p>
          </div>
        ))}
      </div>

      {/* Top Categories */}
      <div>
        <p className="text-xs text-muted-foreground mb-2">Top 3 Categorie Spesa</p>
        <div className="space-y-1">
          {data.top_categories.slice(0, 3).map((cat, index) => (
            <div key={index} className="flex justify-between text-sm">
              <span>{cat.category}</span>
              <span className="font-medium">
                {cat.monthly_avg.toLocaleString("it-IT", { style: "currency", currency: "EUR" })}/mese
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function DeepAnalysisView({ data, onBack }: { data: DeepAnalysisResponse; onBack: () => void }) {
  const grade = getGrade(data.financial_health_score);
  const gradeColor = gradeColors[grade] || "text-muted-foreground";

  return (
    <div className="space-y-4">
      {/* Header Card */}
      <Card className="bg-gradient-to-br from-primary/10 to-primary/5 border-primary/20">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg font-medium flex items-center gap-2">
              <BrainIcon />
              Analisi AI Completa
            </CardTitle>
            <Button size="sm" variant="ghost" onClick={onBack}>
              Chiudi
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {/* Health Score */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-bold text-primary">
                {data.financial_health_score}
              </span>
              <span className="text-muted-foreground">/100</span>
            </div>
            <span className={`text-2xl font-bold ${gradeColor}`}>{grade}</span>
          </div>
          <Progress value={data.financial_health_score} className="h-2 mb-4" />

          {/* Summary */}
          <p className="text-sm text-muted-foreground">{data.summary}</p>
        </CardContent>
      </Card>

      {/* Monthly Overview */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base font-medium">Panoramica Mensile</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <OverviewItem
              label="Entrate"
              value={data.monthly_overview.income}
              isPositive
            />
            <OverviewItem
              label="Spese Fisse"
              value={data.monthly_overview.fixed_expenses}
            />
            <OverviewItem
              label="Spese Discrezionali"
              value={data.monthly_overview.discretionary_expenses}
            />
            <OverviewItem
              label="Rate Debiti"
              value={data.monthly_overview.debt_payments}
            />
          </div>
          <div className="mt-3 pt-3 border-t">
            <div className="flex justify-between">
              <span className="text-sm font-medium">Risparmio</span>
              <span
                className={`font-semibold ${
                  data.monthly_overview.savings >= 0 ? "text-green-500" : "text-red-500"
                }`}
              >
                {data.monthly_overview.savings.toLocaleString("it-IT", {
                  style: "currency",
                  currency: "EUR",
                })}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recommendations */}
      {data.recommendations.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-medium">Raccomandazioni AI</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {data.recommendations.map((rec, index) => (
                <li key={index} className="flex gap-2 text-sm">
                  <span className="text-primary mt-0.5">•</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Savings Opportunities */}
      {data.savings_opportunities.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-medium">
              Opportunita di Risparmio
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {data.savings_opportunities.map((opp, index) => (
                <div key={index} className="p-3 bg-card-foreground/5 rounded-lg">
                  <div className="flex justify-between items-start mb-1">
                    <span className="font-medium text-sm">{opp.area}</span>
                    <Badge variant="outline" className="bg-green-500/10 text-green-500 border-green-500/20">
                      {opp.potential_savings.toLocaleString("it-IT", {
                        style: "currency",
                        currency: "EUR",
                      })}/mese
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">{opp.action}</p>
                  <div className="flex gap-4 mt-2 text-xs text-muted-foreground">
                    <span>
                      Attuale: {opp.current_spending.toLocaleString("it-IT", { style: "currency", currency: "EUR" })}
                    </span>
                    <span>→</span>
                    <span>
                      Target: {opp.suggested_target.toLocaleString("it-IT", { style: "currency", currency: "EUR" })}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recurring Insights */}
      {data.recurring_insights.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-medium">Analisi Abbonamenti</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {data.recurring_insights.map((insight, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-2 rounded-lg bg-card-foreground/5"
                >
                  <div className="flex items-center gap-2">
                    <span>{typeIcons[insight.type] || "📌"}</span>
                    <div>
                      <p className="text-sm font-medium">{insight.name}</p>
                      <p className="text-xs text-muted-foreground">{insight.category}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge
                      variant="outline"
                      className={recommendationColors[insight.recommendation] || ""}
                    >
                      {insight.recommendation}
                    </Badge>
                    <p className="text-xs text-muted-foreground mt-1">
                      {insight.monthly_amount.toLocaleString("it-IT", {
                        style: "currency",
                        currency: "EUR",
                      })}/mese
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Anomalies */}
      {data.anomalies.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-medium text-yellow-500">
              Anomalie Rilevate
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {data.anomalies.map((anomaly, index) => (
                <div
                  key={index}
                  className="p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20"
                >
                  <div className="flex justify-between items-start">
                    <p className="text-sm font-medium">{anomaly.description}</p>
                    <span className="text-sm font-semibold">
                      {anomaly.amount.toLocaleString("it-IT", {
                        style: "currency",
                        currency: "EUR",
                      })}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">{anomaly.explanation}</p>
                  <p className="text-xs text-muted-foreground">
                    {new Date(anomaly.date).toLocaleDateString("it-IT")}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Categorization Issues */}
      {data.categorization_issues.length > 0 && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base font-medium">Suggerimenti Categoria</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {data.categorization_issues.map((issue, index) => (
                <div key={index} className="text-sm p-2 bg-card-foreground/5 rounded">
                  <p className="font-medium">{issue.transaction_desc}</p>
                  <p className="text-xs text-muted-foreground">
                    {issue.current_category} → <span className="text-primary">{issue.suggested_category}</span>
                  </p>
                  <p className="text-xs text-muted-foreground">{issue.reason}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

function OverviewItem({
  label,
  value,
  isPositive = false,
}: {
  label: string;
  value: number;
  isPositive?: boolean;
}) {
  return (
    <div className="bg-card-foreground/5 rounded-lg p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className={`font-semibold ${isPositive ? "text-green-500" : ""}`}>
        {value.toLocaleString("it-IT", { style: "currency", currency: "EUR" })}
      </p>
    </div>
  );
}
