"use client";

import { Wallet } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { TransactionsList, BudgetProgress, TrendChart, RecurringList } from "@/components/money";
import { useTransactions, useBudgets, useRecurring, useTrends } from "@/hooks/use-money";
import { Skeleton } from "@/components/ui/skeleton";

function LoadingState() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-32 w-full" />
      <Skeleton className="h-48 w-full" />
      <Skeleton className="h-48 w-full" />
    </div>
  );
}

function TransactionsTab() {
  const { data, isLoading, error } = useTransactions();

  if (isLoading) return <LoadingState />;
  if (error) return <p className="text-expense">Errore nel caricamento</p>;
  if (!data) return null;

  return (
    <TransactionsList
      groups={data.transactions}
      totalIncome={data.total_income}
      totalExpenses={data.total_expenses}
    />
  );
}

function BudgetTab() {
  const { data, isLoading, error } = useBudgets();

  if (isLoading) return <LoadingState />;
  if (error) return <p className="text-expense">Errore nel caricamento</p>;
  if (!data) return null;

  return (
    <BudgetProgress
      categories={data.categories}
      totalBudget={data.total_budget}
      totalSpent={data.total_spent}
      overBudgetCount={data.over_budget_count}
      warningCount={data.warning_count}
    />
  );
}

function TrendsTab() {
  const { data, isLoading, error } = useTrends(6);

  if (isLoading) return <LoadingState />;
  if (error) return <p className="text-expense">Errore nel caricamento</p>;
  if (!data) return null;

  return (
    <TrendChart
      months={data.months}
      monthlyTotals={data.monthly_totals}
      topCategories={data.top_categories}
      averageMonthlySpending={data.average_monthly_spending}
      spendingTrendPercent={data.spending_trend_percent}
    />
  );
}

function RecurringTab() {
  const { data, isLoading, error } = useRecurring();

  if (isLoading) return <LoadingState />;
  if (error) return <p className="text-expense">Errore nel caricamento</p>;
  if (!data) return null;

  return (
    <RecurringList
      expenses={data.expenses}
      totalMonthly={data.total_monthly}
      essentialMonthly={data.essential_monthly}
      nonEssentialMonthly={data.non_essential_monthly}
      potentialSavings={data.potential_savings}
      optimizableCount={data.optimizable_count}
      dueThisMonthCount={data.due_this_month_count}
      dueThisMonthTotal={data.due_this_month_total}
      highPriorityActions={data.high_priority_actions}
    />
  );
}

export default function MoneyPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Wallet className="h-6 w-6 text-primary" />
            Money
          </h1>
          <p className="text-muted-foreground text-sm">
            Transazioni, budget e trend
          </p>
        </div>
      </div>

      <Tabs defaultValue="transactions" className="w-full">
        <TabsList className="mb-6">
          <TabsTrigger value="transactions">
            Transazioni
          </TabsTrigger>
          <TabsTrigger value="budget">
            Budget
          </TabsTrigger>
          <TabsTrigger value="trends">
            Trend
          </TabsTrigger>
          <TabsTrigger value="recurring">
            Ricorrenti
          </TabsTrigger>
        </TabsList>

        <TabsContent value="transactions">
          <TransactionsTab />
        </TabsContent>

        <TabsContent value="budget">
          <BudgetTab />
        </TabsContent>

        <TabsContent value="trends">
          <TrendsTab />
        </TabsContent>

        <TabsContent value="recurring">
          <RecurringTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}
