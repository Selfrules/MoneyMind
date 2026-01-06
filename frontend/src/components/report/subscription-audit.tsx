"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { XCircle, ArrowDownCircle, Eye, Check, MessageSquare, AlertTriangle } from "lucide-react";

interface SubscriptionAuditItem {
  name: string;
  category: string;
  monthly_cost: number;
  annual_cost: number;
  action: "cancel" | "downgrade" | "review" | "keep" | "negotiate";
  reason: string;
  potential_savings: number;
  value_score: number;
  alternative: string | null;
}

interface SubscriptionAuditProps {
  data?: SubscriptionAuditItem[];
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

const actionConfig = {
  cancel: {
    label: "Cancella",
    icon: XCircle,
    bgColor: "bg-red-500/20",
    textColor: "text-red-400",
    borderColor: "border-red-500/30",
  },
  downgrade: {
    label: "Downgrade",
    icon: ArrowDownCircle,
    bgColor: "bg-orange-500/20",
    textColor: "text-orange-400",
    borderColor: "border-orange-500/30",
  },
  review: {
    label: "Rivedi",
    icon: Eye,
    bgColor: "bg-yellow-500/20",
    textColor: "text-yellow-400",
    borderColor: "border-yellow-500/30",
  },
  negotiate: {
    label: "Negozia",
    icon: MessageSquare,
    bgColor: "bg-blue-500/20",
    textColor: "text-blue-400",
    borderColor: "border-blue-500/30",
  },
  keep: {
    label: "Mantieni",
    icon: Check,
    bgColor: "bg-emerald-500/20",
    textColor: "text-emerald-400",
    borderColor: "border-emerald-500/30",
  },
};

function ValueScore({ score }: { score: number }) {
  const getColor = () => {
    if (score >= 8) return "text-emerald-400";
    if (score >= 6) return "text-green-400";
    if (score >= 4) return "text-yellow-400";
    return "text-red-400";
  };

  return (
    <div className="flex items-center gap-1">
      <span className={`text-sm font-bold ${getColor()}`}>{score}</span>
      <span className="text-xs text-muted-foreground">/10</span>
    </div>
  );
}

export function SubscriptionAudit({ data, isLoading }: SubscriptionAuditProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Audit Abbonamenti</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-24 bg-muted animate-pulse rounded-lg" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const subscriptions = data || [];
  const totalMonthlyCost = subscriptions.reduce((sum, s) => sum + s.monthly_cost, 0);
  const totalPotentialSavings = subscriptions.reduce((sum, s) => sum + s.potential_savings, 0);
  const cancelCount = subscriptions.filter(s => s.action === "cancel").length;
  const downgradeCount = subscriptions.filter(s => s.action === "downgrade").length;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            Audit Abbonamenti
            {(cancelCount > 0 || downgradeCount > 0) && (
              <Badge variant="destructive" className="text-xs">
                <AlertTriangle className="h-3 w-3 mr-1" />
                {cancelCount + downgradeCount} azioni
              </Badge>
            )}
          </CardTitle>
          <div className="text-right">
            <div className="text-sm text-muted-foreground">Totale Mensile</div>
            <div className="text-lg font-bold text-foreground">{formatCurrency(totalMonthlyCost)}</div>
          </div>
        </div>
        {totalPotentialSavings > 0 && (
          <div className="mt-2 p-2 bg-emerald-500/10 border border-emerald-500/20 rounded-lg">
            <div className="text-sm text-emerald-400 font-medium">
              Risparmio Potenziale: {formatCurrency(totalPotentialSavings)}/mese ({formatCurrency(totalPotentialSavings * 12)}/anno)
            </div>
          </div>
        )}
      </CardHeader>
      <CardContent className="space-y-3">
        {subscriptions.map((sub, index) => {
          const config = actionConfig[sub.action];
          const Icon = config.icon;

          return (
            <div
              key={index}
              className={`p-4 rounded-lg border ${
                sub.action === "cancel" ? "border-red-500/30 bg-red-500/5" :
                sub.action === "downgrade" ? "border-orange-500/30 bg-orange-500/5" :
                "border-border bg-muted/20"
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-foreground">{sub.name}</span>
                    <Badge variant="outline" className="text-xs">
                      {sub.category}
                    </Badge>
                    <Badge
                      variant="outline"
                      className={`${config.bgColor} ${config.textColor} ${config.borderColor} text-xs`}
                    >
                      <Icon className="h-3 w-3 mr-1" />
                      {config.label}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">{sub.reason}</p>
                  {sub.alternative && (
                    <p className="text-xs text-blue-400 mt-1">
                      Alternativa: {sub.alternative}
                    </p>
                  )}
                </div>

                <div className="text-right flex-shrink-0">
                  <div className="text-lg font-bold text-foreground">
                    {formatCurrency(sub.monthly_cost)}/m
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {formatCurrency(sub.annual_cost)}/anno
                  </div>
                  <div className="mt-1">
                    <ValueScore score={sub.value_score} />
                  </div>
                  {sub.potential_savings > 0 && (
                    <div className="text-xs text-emerald-400 mt-1">
                      Risparmia {formatCurrency(sub.potential_savings)}/m
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}

        {subscriptions.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            Nessun abbonamento trovato
          </div>
        )}
      </CardContent>
    </Card>
  );
}
