"use client";

import { Card, CardContent } from "@/components/ui/card";
import {
  Wallet,
  TrendingUp,
  TrendingDown,
  PiggyBank,
  CreditCard,
  Shield,
  BarChart3,
} from "lucide-react";
import type { KPIs } from "@/lib/api-types";

interface KPICardsProps {
  kpis: KPIs;
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("it-IT", {
    style: "currency",
    currency: "EUR",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

function formatPercent(value: number): string {
  return `${value.toFixed(1)}%`;
}

export function KPICards({ kpis }: KPICardsProps) {
  const kpiItems = [
    {
      label: "Saldo Totale",
      value: formatCurrency(kpis.total_balance),
      icon: Wallet,
      color: kpis.total_balance >= 0 ? "text-income" : "text-expense",
    },
    {
      label: "Entrate Mensili",
      value: formatCurrency(kpis.monthly_income),
      icon: TrendingUp,
      color: "text-income",
    },
    {
      label: "Uscite Mensili",
      value: formatCurrency(kpis.monthly_expenses),
      icon: TrendingDown,
      color: "text-expense",
    },
    {
      label: "Tasso di Risparmio",
      value: formatPercent(kpis.savings_rate),
      icon: PiggyBank,
      color: kpis.savings_rate >= 20 ? "text-income" : kpis.savings_rate >= 10 ? "text-warning" : "text-expense",
    },
    {
      label: "Debito Totale",
      value: formatCurrency(kpis.total_debt),
      icon: CreditCard,
      color: kpis.total_debt > 0 ? "text-expense" : "text-income",
    },
    {
      label: "DTI Ratio",
      value: formatPercent(kpis.dti_ratio),
      icon: BarChart3,
      color: kpis.dti_ratio <= 20 ? "text-income" : kpis.dti_ratio <= 36 ? "text-warning" : "text-expense",
    },
    {
      label: "Patrimonio Netto",
      value: formatCurrency(kpis.net_worth),
      icon: Shield,
      color: kpis.net_worth >= 0 ? "text-income" : "text-expense",
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-3">
      {kpiItems.map((item) => (
        <Card key={item.label} className="bg-card/50">
          <CardContent className="p-3">
            <div className="flex items-center gap-2 mb-1">
              <item.icon className={`h-4 w-4 ${item.color}`} />
              <span className="text-xs text-muted-foreground">{item.label}</span>
            </div>
            <p className={`text-lg font-semibold ${item.color}`}>{item.value}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
