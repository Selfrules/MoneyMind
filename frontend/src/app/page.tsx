"use client";

import { useFullReport } from "@/hooks/use-report";
import { useFixedDiscretionary } from "@/hooks/use-budget";
import {
  ExecutiveSummary,
  CategorySpendingTable,
  SubscriptionAudit,
  DebtPriorityMatrix,
  RecommendationsList,
  MonthComparison,
  BudgetRemaining,
} from "@/components/report";
import { DeepAnalysis } from "@/components/dashboard/deep-analysis";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Loader2, AlertCircle, RefreshCw, Calendar, FileBarChart } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  const currentMonth = new Date().toISOString().slice(0, 7);

  const {
    data: report,
    isLoading,
    error,
    refetch,
  } = useFullReport(currentMonth);

  // v7.0 - Fixed vs Discretionary Budget
  const { data: budgetData, isLoading: budgetLoading } = useFixedDiscretionary(currentMonth);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto mb-2" />
          <p className="text-muted-foreground">Generando il tuo report finanziario...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center max-w-md">
          <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
          <h2 className="text-lg font-semibold mb-2">Errore di Connessione</h2>
          <p className="text-muted-foreground mb-4 text-sm">
            Impossibile connettersi al server. Assicurati che il backend sia in esecuzione su
            http://localhost:8001
          </p>
          <Button onClick={() => refetch()} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Riprova
          </Button>
        </div>
      </div>
    );
  }

  const formatMonth = (month: string) => {
    const date = new Date(month + "-01");
    return date.toLocaleDateString("it-IT", { month: "long", year: "numeric" });
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <FileBarChart className="h-6 w-6 text-primary" />
            Report Finanziario
          </h1>
          <p className="text-muted-foreground text-sm">
            Analisi completa della tua situazione finanziaria
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Badge variant="outline" className="text-sm">
            <Calendar className="h-3.5 w-3.5 mr-1.5" />
            {report ? formatMonth(report.month) : formatMonth(currentMonth)}
          </Badge>
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            <RefreshCw className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Executive Summary */}
      <ExecutiveSummary
        data={report?.executive_summary}
        isLoading={isLoading}
      />

      {/* v7.0 - Fixed vs Discretionary Budget Overview */}
      <BudgetRemaining
        data={budgetData}
        isLoading={budgetLoading}
      />

      {/* AI Deep Analysis */}
      <DeepAnalysis />

      {/* Main Report Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Category Spending Analysis */}
        <div className="xl:col-span-2">
          <CategorySpendingTable
            data={report?.category_spending}
            isLoading={isLoading}
          />
        </div>

        {/* Subscription Audit */}
        <SubscriptionAudit
          data={report?.subscription_audit}
          isLoading={isLoading}
        />

        {/* Debt Priority Matrix */}
        <DebtPriorityMatrix
          data={report?.debt_priority}
          isLoading={isLoading}
        />

        {/* Recommendations */}
        <div className="xl:col-span-2">
          <RecommendationsList
            data={report?.recommendations}
            isLoading={isLoading}
          />
        </div>

        {/* Month Comparison */}
        <div className="xl:col-span-2">
          <MonthComparison
            data={report?.month_comparison}
            isLoading={isLoading}
          />
        </div>
      </div>

      {/* Report Date Footer */}
      <Card className="bg-muted/30">
        <CardContent className="py-4">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>Report generato il {report?.report_date || new Date().toISOString().split('T')[0]}</span>
            <span>MoneyMind v7.1 - Il tuo consulente finanziario AI</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
