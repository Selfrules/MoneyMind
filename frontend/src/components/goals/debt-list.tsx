"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import type { Debt } from "@/lib/api-types";
import { CreditCard, Calendar, Percent, Banknote } from "lucide-react";

interface DebtListProps {
  debts: Debt[];
}

function formatAmount(amount: number): string {
  return new Intl.NumberFormat("it-IT", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(amount);
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "—";
  const date = new Date(dateStr);
  return date.toLocaleDateString("it-IT", {
    month: "short",
    year: "numeric",
  });
}

function getDebtTypeIcon(type: string): string {
  switch (type.toLowerCase()) {
    case "mortgage":
    case "mutuo":
      return "🏠";
    case "car_loan":
    case "auto":
      return "🚗";
    case "student_loan":
    case "studio":
      return "🎓";
    case "credit_card":
    case "carta":
      return "💳";
    case "personal_loan":
    case "personale":
      return "💰";
    default:
      return "📋";
  }
}

function DebtItem({ debt }: { debt: Debt }) {
  const progressPercent = debt.original_amount > 0
    ? ((debt.original_amount - debt.current_balance) / debt.original_amount) * 100
    : 0;

  return (
    <div className="space-y-3 py-4 border-b border-border/50 last:border-0">
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xl">{getDebtTypeIcon(debt.type)}</span>
          <div>
            <h4 className="font-medium text-sm">{debt.name}</h4>
            <p className="text-xs text-muted-foreground capitalize">
              {debt.type}
            </p>
          </div>
        </div>
        <div className="text-right">
          <p className="font-bold text-expense">
            {formatAmount(debt.current_balance)}
          </p>
          <p className="text-xs text-muted-foreground">
            di {formatAmount(debt.original_amount)}
          </p>
        </div>
      </div>

      {/* Progress bar */}
      <div className="space-y-1">
        <Progress value={progressPercent} className="h-2" />
        <p className="text-xs text-muted-foreground text-right">
          {progressPercent.toFixed(0)}% pagato
        </p>
      </div>

      {/* Details */}
      <div className="grid grid-cols-3 gap-2 text-xs">
        <div className="flex items-center gap-1 text-muted-foreground">
          <Banknote className="w-3 h-3" />
          <span>{formatAmount(debt.monthly_payment)}/mese</span>
        </div>
        <div className="flex items-center gap-1 text-muted-foreground">
          <Percent className="w-3 h-3" />
          <span>{debt.interest_rate}% TAN</span>
        </div>
        <div className="flex items-center gap-1 text-muted-foreground">
          <Calendar className="w-3 h-3" />
          <span>Giorno {debt.payment_day}</span>
        </div>
      </div>

      {/* Payoff info */}
      {debt.payoff_date && (
        <div className="flex items-center justify-between text-xs bg-muted/50 rounded-lg px-3 py-2">
          <span className="text-muted-foreground">Estinzione prevista</span>
          <div className="text-right">
            <span className="font-medium">{formatDate(debt.payoff_date)}</span>
            {debt.months_remaining && (
              <span className="text-muted-foreground ml-1">
                ({debt.months_remaining} mesi)
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export function DebtList({ debts }: DebtListProps) {
  if (debts.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <CreditCard className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">Nessun debito attivo</p>
        </CardContent>
      </Card>
    );
  }

  // Sort debts: by interest rate descending (avalanche strategy)
  const sortedDebts = [...debts].sort((a, b) => b.interest_rate - a.interest_rate);

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base">I Tuoi Debiti</CardTitle>
          <Badge variant="outline" className="text-xs">
            Ordinati per tasso
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        {sortedDebts.map((debt) => (
          <DebtItem key={debt.id} debt={debt} />
        ))}
      </CardContent>
    </Card>
  );
}
