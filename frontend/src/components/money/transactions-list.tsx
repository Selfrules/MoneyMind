"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { TransactionGroup, Transaction } from "@/lib/api-types";
import { ArrowDownLeft, ArrowUpRight, Receipt } from "lucide-react";

interface TransactionsListProps {
  groups: TransactionGroup[];
  totalIncome: number;
  totalExpenses: number;
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  if (date.toDateString() === today.toDateString()) {
    return "Oggi";
  } else if (date.toDateString() === yesterday.toDateString()) {
    return "Ieri";
  } else {
    return date.toLocaleDateString("it-IT", {
      weekday: "short",
      day: "numeric",
      month: "short",
    });
  }
}

function formatAmount(amount: number): string {
  const absAmount = Math.abs(amount);
  return new Intl.NumberFormat("it-IT", {
    style: "currency",
    currency: "EUR",
  }).format(absAmount);
}

function TransactionItem({ transaction }: { transaction: Transaction }) {
  const isIncome = transaction.amount > 0;

  return (
    <div className="flex items-center justify-between py-3 border-b border-border/50 last:border-0">
      <div className="flex items-center gap-3">
        <div
          className={`w-8 h-8 rounded-full flex items-center justify-center ${
            isIncome ? "bg-income/20" : "bg-expense/20"
          }`}
        >
          {isIncome ? (
            <ArrowDownLeft className="w-4 h-4 text-income" />
          ) : (
            <ArrowUpRight className="w-4 h-4 text-expense" />
          )}
        </div>
        <div className="flex flex-col">
          <span className="text-sm font-medium line-clamp-1">
            {transaction.description}
          </span>
          <span className="text-xs text-muted-foreground">
            {transaction.category_icon} {transaction.category_name || "Altro"}
          </span>
        </div>
      </div>
      <span
        className={`text-sm font-semibold ${
          isIncome ? "text-income" : "text-expense"
        }`}
      >
        {isIncome ? "+" : "-"}
        {formatAmount(transaction.amount)}
      </span>
    </div>
  );
}

export function TransactionsList({
  groups,
  totalIncome,
  totalExpenses,
}: TransactionsListProps) {
  if (groups.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <Receipt className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <p className="text-muted-foreground">
            Nessuna transazione per questo mese
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Summary */}
      <div className="flex gap-2">
        <Badge variant="outline" className="text-income border-income/30">
          <ArrowDownLeft className="w-3 h-3 mr-1" />
          {formatAmount(totalIncome)}
        </Badge>
        <Badge variant="outline" className="text-expense border-expense/30">
          <ArrowUpRight className="w-3 h-3 mr-1" />
          {formatAmount(totalExpenses)}
        </Badge>
      </div>

      {/* Transaction Groups */}
      {groups.map((group) => (
        <Card key={group.date}>
          <CardHeader className="py-3 px-4">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium">
                {formatDate(group.date)}
              </CardTitle>
              <span
                className={`text-sm font-semibold ${
                  group.daily_total >= 0 ? "text-income" : "text-expense"
                }`}
              >
                {group.daily_total >= 0 ? "+" : ""}
                {formatAmount(group.daily_total)}
              </span>
            </div>
          </CardHeader>
          <CardContent className="py-0 px-4">
            {group.transactions.map((tx) => (
              <TransactionItem key={tx.id} transaction={tx} />
            ))}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
