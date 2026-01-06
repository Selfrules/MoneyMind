"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Check, X, Clock, Zap } from "lucide-react";
import type { DailyAction } from "@/lib/api-types";
import { useCompleteAction } from "@/hooks/use-dashboard";

interface DailyActionsProps {
  actions: DailyAction[];
  pendingCount: number;
}

export function DailyActions({ actions, pendingCount }: DailyActionsProps) {
  const completeAction = useCompleteAction();

  const handleComplete = (actionId: number, decision: "accepted" | "rejected" | "postponed") => {
    completeAction.mutate({ actionId, request: { decision } });
  };

  if (actions.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Zap className="h-5 w-5 text-primary" />
            Azioni Giornaliere
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-center py-4">
            Nessuna azione da completare oggi
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Zap className="h-5 w-5 text-primary" />
            Azioni Giornaliere
          </CardTitle>
          <Badge variant="secondary">{pendingCount} da fare</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {actions.map((action) => (
          <ActionItem
            key={action.id}
            action={action}
            onComplete={handleComplete}
            isLoading={completeAction.isPending}
          />
        ))}
      </CardContent>
    </Card>
  );
}

interface ActionItemProps {
  action: DailyAction;
  onComplete: (id: number, decision: "accepted" | "rejected" | "postponed") => void;
  isLoading: boolean;
}

function ActionItem({ action, onComplete, isLoading }: ActionItemProps) {
  const impactColor =
    action.impact_type === "savings"
      ? "text-income"
      : action.impact_type === "payoff_acceleration"
        ? "text-primary"
        : "text-warning";

  return (
    <div className="rounded-lg border bg-secondary/30 p-3">
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex-1">
          <p className="font-medium text-sm">{action.title}</p>
          {action.description && (
            <p className="text-xs text-muted-foreground mt-1">
              {action.description}
            </p>
          )}
        </div>
        <Badge variant="outline" className="text-xs">
          #{action.priority}
        </Badge>
      </div>

      {action.estimated_impact_monthly && (
        <p className={`text-xs ${impactColor} mb-2`}>
          Risparmio stimato: {action.estimated_impact_monthly.toFixed(0)}€/mese
        </p>
      )}

      <div className="flex gap-2">
        <Button
          size="sm"
          variant="default"
          className="flex-1"
          onClick={() => onComplete(action.id, "accepted")}
          disabled={isLoading}
        >
          <Check className="h-4 w-4 mr-1" />
          Fatto
        </Button>
        <Button
          size="sm"
          variant="outline"
          onClick={() => onComplete(action.id, "postponed")}
          disabled={isLoading}
        >
          <Clock className="h-4 w-4" />
        </Button>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => onComplete(action.id, "rejected")}
          disabled={isLoading}
        >
          <X className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
