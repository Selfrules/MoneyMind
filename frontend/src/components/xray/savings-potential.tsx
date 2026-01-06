"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Lightbulb, TrendingDown, ArrowRight, Sparkles } from "lucide-react";

interface SavingOpportunity {
  category: string;
  current: number;
  baseline: number;
  potential_savings: number;
  impact_monthly: number;
  impact_annual: number;
  recommendation: string;
  priority: number;
}

interface SavingsPotentialProps {
  opportunities?: SavingOpportunity[];
  totalMonthly?: number;
  totalAnnual?: number;
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

function getPriorityColor(priority: number): string {
  if (priority === 1) return "bg-red-500/20 text-red-400 border-red-500/30";
  if (priority === 2) return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
  return "bg-blue-500/20 text-blue-400 border-blue-500/30";
}

function getPriorityLabel(priority: number): string {
  if (priority === 1) return "High";
  if (priority === 2) return "Medium";
  return "Low";
}

export function SavingsPotential({
  opportunities = [],
  totalMonthly = 0,
  totalAnnual = 0,
  isLoading,
}: SavingsPotentialProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Savings Potential</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-24 bg-muted animate-pulse rounded-lg" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const hasOpportunities = opportunities.length > 0;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Lightbulb className="h-5 w-5 text-yellow-400" />
            Savings Potential
          </CardTitle>
          {hasOpportunities && (
            <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30">
              <Sparkles className="h-3 w-3 mr-1" />
              {formatCurrency(totalMonthly)}/mo
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {/* Total Potential Card */}
        {hasOpportunities && (
          <div className="rounded-lg bg-emerald-500/10 border border-emerald-500/20 p-4 mb-4">
            <div className="text-xs text-muted-foreground uppercase tracking-wider mb-2">
              Total Savings Potential
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-xs text-muted-foreground">Monthly</div>
                <div className="text-2xl font-bold text-emerald-400">
                  {formatCurrency(totalMonthly)}
                </div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">Annual</div>
                <div className="text-2xl font-bold text-emerald-300">
                  {formatCurrency(totalAnnual)}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!hasOpportunities && (
          <div className="text-center py-8">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-emerald-500/10 mx-auto mb-3">
              <Sparkles className="h-6 w-6 text-emerald-400" />
            </div>
            <div className="text-sm font-medium text-foreground mb-1">No Optimization Found</div>
            <div className="text-xs text-muted-foreground">
              Your spending patterns look efficient!
            </div>
          </div>
        )}

        {/* Opportunities List */}
        {hasOpportunities && (
          <div className="space-y-3">
            {opportunities.slice(0, 5).map((opp, index) => (
              <div
                key={index}
                className="rounded-lg border border-border bg-card p-4 hover:border-primary/30 transition-colors"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-foreground">{opp.category}</span>
                    <Badge variant="outline" className={getPriorityColor(opp.priority)}>
                      {getPriorityLabel(opp.priority)}
                    </Badge>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-semibold text-emerald-400">
                      -{formatCurrency(opp.potential_savings)}
                    </div>
                    <div className="text-xs text-muted-foreground">/month</div>
                  </div>
                </div>

                {/* Current vs Baseline */}
                <div className="flex items-center gap-2 text-xs text-muted-foreground mb-2">
                  <span>Current: {formatCurrency(opp.current)}</span>
                  <ArrowRight className="h-3 w-3" />
                  <span className="text-emerald-400">Target: {formatCurrency(opp.baseline)}</span>
                </div>

                {/* Recommendation */}
                <div className="text-xs text-muted-foreground bg-muted/50 rounded-md p-2">
                  <TrendingDown className="h-3 w-3 inline mr-1 text-emerald-400" />
                  {opp.recommendation}
                </div>

                {/* Annual Impact */}
                <div className="mt-2 text-xs text-muted-foreground">
                  Annual impact: <span className="text-emerald-400 font-medium">{formatCurrency(opp.impact_annual)}</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Show More Prompt */}
        {opportunities.length > 5 && (
          <div className="mt-4 text-center">
            <button className="text-sm text-primary hover:underline">
              View {opportunities.length - 5} more opportunities
            </button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
