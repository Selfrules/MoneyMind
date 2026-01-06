"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowDownRight, ArrowUpRight, Wallet, CreditCard, ShoppingBag, PiggyBank } from "lucide-react";

interface CashFlowData {
  income: number;
  essential_expenses: number;
  debt_payments: number;
  discretionary: number;
  available_for_savings: number;
  total_expenses: number;
  savings_rate: number;
}

interface CashFlowBreakdownProps {
  data?: CashFlowData;
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

function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

interface FlowItemProps {
  icon: React.ReactNode;
  label: string;
  amount: number;
  percentage: number;
  color: string;
}

function FlowItem({ icon, label, amount, percentage, color }: FlowItemProps) {
  return (
    <div className="flex items-center justify-between py-3 border-b border-border last:border-0">
      <div className="flex items-center gap-3">
        <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${color}`}>
          {icon}
        </div>
        <div>
          <div className="text-sm font-medium text-foreground">{label}</div>
          <div className="text-xs text-muted-foreground">{formatPercent(percentage)} of income</div>
        </div>
      </div>
      <div className="text-right">
        <div className="text-sm font-semibold text-foreground">{formatCurrency(Math.abs(amount))}</div>
      </div>
    </div>
  );
}

export function CashFlowBreakdown({ data, isLoading }: CashFlowBreakdownProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Cash Flow Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-16 bg-muted animate-pulse rounded-lg" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const defaultData: CashFlowData = data || {
    income: 0,
    essential_expenses: 0,
    debt_payments: 0,
    discretionary: 0,
    available_for_savings: 0,
    total_expenses: 0,
    savings_rate: 0,
  };

  const income = defaultData.income || 1; // Avoid division by zero

  const flowItems = [
    {
      icon: <Wallet className="h-5 w-5 text-white" />,
      label: "Essential Expenses",
      amount: defaultData.essential_expenses,
      percentage: defaultData.essential_expenses / income,
      color: "bg-blue-500",
    },
    {
      icon: <CreditCard className="h-5 w-5 text-white" />,
      label: "Debt Payments",
      amount: defaultData.debt_payments,
      percentage: defaultData.debt_payments / income,
      color: "bg-red-500",
    },
    {
      icon: <ShoppingBag className="h-5 w-5 text-white" />,
      label: "Discretionary",
      amount: defaultData.discretionary,
      percentage: defaultData.discretionary / income,
      color: "bg-yellow-500",
    },
    {
      icon: <PiggyBank className="h-5 w-5 text-white" />,
      label: "Available for Savings",
      amount: defaultData.available_for_savings,
      percentage: defaultData.available_for_savings / income,
      color: "bg-emerald-500",
    },
  ];

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">Cash Flow Breakdown</CardTitle>
          <div className="flex items-center gap-1 text-sm">
            <span className="text-muted-foreground">Savings Rate:</span>
            <span className={`font-semibold ${defaultData.savings_rate >= 20 ? "text-emerald-400" : defaultData.savings_rate >= 10 ? "text-yellow-400" : "text-red-400"}`}>
              {defaultData.savings_rate.toFixed(1)}%
            </span>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* Income Header */}
        <div className="flex items-center justify-between py-3 mb-2 border-b-2 border-emerald-500/30 bg-emerald-500/5 -mx-6 px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-500">
              <ArrowDownRight className="h-5 w-5 text-white" />
            </div>
            <div>
              <div className="text-sm font-medium text-foreground">Total Income</div>
              <div className="text-xs text-muted-foreground">Monthly inflow</div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-lg font-bold text-emerald-400">{formatCurrency(defaultData.income)}</div>
          </div>
        </div>

        {/* Flow Items */}
        <div className="space-y-1">
          {flowItems.map((item, index) => (
            <FlowItem key={index} {...item} />
          ))}
        </div>

        {/* Visual Bar */}
        <div className="mt-4 h-3 rounded-full overflow-hidden bg-muted flex">
          <div
            className="bg-blue-500 transition-all"
            style={{ width: `${(defaultData.essential_expenses / income) * 100}%` }}
          />
          <div
            className="bg-red-500 transition-all"
            style={{ width: `${(defaultData.debt_payments / income) * 100}%` }}
          />
          <div
            className="bg-yellow-500 transition-all"
            style={{ width: `${(defaultData.discretionary / income) * 100}%` }}
          />
          <div
            className="bg-emerald-500 transition-all"
            style={{ width: `${(defaultData.available_for_savings / income) * 100}%` }}
          />
        </div>

        {/* Legend */}
        <div className="mt-3 flex flex-wrap gap-4 text-xs text-muted-foreground">
          <div className="flex items-center gap-1.5">
            <div className="h-2 w-2 rounded-full bg-blue-500" />
            <span>Essential</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="h-2 w-2 rounded-full bg-red-500" />
            <span>Debt</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="h-2 w-2 rounded-full bg-yellow-500" />
            <span>Discretionary</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="h-2 w-2 rounded-full bg-emerald-500" />
            <span>Savings</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
