"use client";

import { Target, PiggyBank, Map, Trophy } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  DebtFreedomCard,
  DebtList,
  GoalCard,
  JourneyMap,
  DebtProgressBars,
} from "@/components/goals";
import { useDebts, useGoals, useDebtJourney, usePendingCelebrations, useMarkCelebrationShown } from "@/hooks/use-goals";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useEffect } from "react";

function LoadingState() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-40 w-full" />
      <Skeleton className="h-48 w-full" />
      <Skeleton className="h-48 w-full" />
    </div>
  );
}

function CelebrationBanner() {
  const { data } = usePendingCelebrations();
  const markShown = useMarkCelebrationShown();

  useEffect(() => {
    // Auto-dismiss after showing (in a real app, you'd show a modal first)
    if (data?.celebrations && data.celebrations.length > 0) {
      // Could show a celebration modal here
    }
  }, [data]);

  if (!data?.celebrations || data.celebrations.length === 0) return null;

  const celebration = data.celebrations[0];

  return (
    <Card className="bg-gradient-to-r from-yellow-500/10 to-amber-500/10 border-yellow-500/30 mb-4">
      <CardContent className="py-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-full bg-yellow-500/20">
            <Trophy className="h-6 w-6 text-yellow-400" />
          </div>
          <div className="flex-1">
            <p className="font-bold text-yellow-400">Traguardo Raggiunto!</p>
            <p className="text-sm text-foreground">{celebration.title}</p>
            <p className="text-xs text-muted-foreground">
              {celebration.goal_name}
            </p>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => markShown.mutate(celebration.id)}
          >
            Chiudi
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

function JourneyTab() {
  const { data: journeyData, isLoading: journeyLoading } = useDebtJourney();
  const { data: debtsData, isLoading: debtsLoading } = useDebts(true);

  if (journeyLoading || debtsLoading) return <LoadingState />;

  return (
    <div className="space-y-4">
      {/* Journey Map - 4 Phase Visualization */}
      <JourneyMap
        currentPhase={journeyData?.phase_info?.phase || "diagnosi"}
        phaseProgress={journeyData?.phase_info?.progress_percent || 0}
        overallProgress={journeyData?.overall_progress_percent || 0}
        projectedDebtFreeDate={journeyData?.projected_payoff_date}
        isLoading={journeyLoading}
      />

      {/* Debt Progress Bars */}
      {debtsData && (
        <DebtProgressBars
          debts={debtsData.debts.map((d) => ({
            id: d.id,
            name: d.name,
            type: d.type,
            original_amount: d.original_amount,
            current_balance: d.current_balance,
            interest_rate: d.interest_rate,
            monthly_payment: d.monthly_payment,
            expected_end_date: d.payoff_date ?? undefined,
            is_active: d.is_active,
            priority_order: d.priority_rank ?? undefined,
          }))}
          totalOriginal={debtsData.debts.reduce((sum, d) => sum + d.original_amount, 0)}
          totalCurrent={debtsData.total_debt}
          projectedPayoffDate={debtsData.projected_debt_free_date ?? undefined}
          monthlyPayment={debtsData.total_monthly_payment}
          isLoading={debtsLoading}
        />
      )}
    </div>
  );
}

function DebtsTab() {
  const { data, isLoading, error } = useDebts(true);

  if (isLoading) return <LoadingState />;
  if (error) return <p className="text-expense">Errore nel caricamento</p>;
  if (!data) return null;

  return (
    <div className="space-y-4">
      <DebtFreedomCard data={data} />
      <DebtList debts={data.debts} />
    </div>
  );
}

function GoalsTab() {
  const { data, isLoading, error } = useGoals();

  if (isLoading) return <LoadingState />;
  if (error) return <p className="text-expense">Errore nel caricamento</p>;
  if (!data) return null;

  if (data.goals.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <PiggyBank className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">
            Nessun obiettivo impostato
          </p>
          <p className="text-xs text-muted-foreground mt-2">
            Crea il tuo primo obiettivo di risparmio!
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Summary Card */}
      <Card>
        <CardContent className="py-4">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-sm text-muted-foreground">Progresso totale</p>
              <p className="text-2xl font-bold">{data.overall_progress.toFixed(0)}%</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-muted-foreground">
                {data.active_count} attivi • {data.completed_count} completati
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Goals List */}
      {data.goals.map((goal) => (
        <GoalCard key={goal.id} goal={goal} />
      ))}
    </div>
  );
}

export default function GoalsPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Target className="h-6 w-6 text-primary" />
            Goals
          </h1>
          <p className="text-muted-foreground text-sm">
            Obiettivi finanziari e debiti
          </p>
        </div>
      </div>

      {/* Celebration Banner */}
      <CelebrationBanner />

      <Tabs defaultValue="journey" className="w-full">
        <TabsList className="mb-6">
          <TabsTrigger value="journey" className="flex items-center gap-1">
            <Map className="h-3.5 w-3.5" />
            Percorso
          </TabsTrigger>
          <TabsTrigger value="debts">Debiti</TabsTrigger>
          <TabsTrigger value="goals">Obiettivi</TabsTrigger>
        </TabsList>

        <TabsContent value="journey">
          <JourneyTab />
        </TabsContent>

        <TabsContent value="debts">
          <DebtsTab />
        </TabsContent>

        <TabsContent value="goals">
          <GoalsTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}
