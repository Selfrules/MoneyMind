"use client";

import { Flame } from "lucide-react";
import {
  FIRECalculator,
  FIREMilestones,
  ScenarioComparison,
  ExtraSavingsSimulator,
} from "@/components/fire";
import {
  useFIRESummary,
  useSimulateExtraSavings,
} from "@/hooks/use-fire";
import { Skeleton } from "@/components/ui/skeleton";

function LoadingState() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-48 w-full" />
      <Skeleton className="h-64 w-full" />
      <Skeleton className="h-48 w-full" />
    </div>
  );
}

export default function FIREPage() {
  const { data, isLoading, error } = useFIRESummary();
  const simulateExtra = useSimulateExtraSavings();

  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
              <Flame className="h-6 w-6 text-orange-500" />
              FIRE Calculator
            </h1>
            <p className="text-muted-foreground text-sm">
              Financial Independence, Retire Early
            </p>
          </div>
        </div>
        <p className="text-expense text-center py-8">
          Errore nel caricamento dei dati FIRE
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Flame className="h-6 w-6 text-orange-500" />
            FIRE Calculator
          </h1>
          <p className="text-muted-foreground text-sm">
            Financial Independence, Retire Early
          </p>
        </div>
      </div>

      {isLoading ? (
        <LoadingState />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Main FIRE Calculator */}
          <FIRECalculator data={data} isLoading={isLoading} />

          {/* FIRE Milestones */}
          <FIREMilestones
            milestones={data?.milestones}
            currentNetWorth={data?.current_net_worth}
            isLoading={isLoading}
          />

          {/* Scenario Comparison */}
          <ScenarioComparison
            scenarios={data?.scenarios}
            isLoading={isLoading}
          />

          {/* Extra Savings Simulator */}
          <ExtraSavingsSimulator
            onSimulate={(amount) => simulateExtra.mutate(amount)}
            result={simulateExtra.data}
            isSimulating={simulateExtra.isPending}
          />
        </div>
      )}
    </div>
  );
}
