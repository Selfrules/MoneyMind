"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type {
  TransactionsResponse,
  BudgetSummaryResponse,
  RecurringSummaryResponse,
  TrendsResponse,
} from "@/lib/api-types";

/**
 * Hook to fetch transactions for a month
 */
export function useTransactions(month?: string) {
  const currentMonth = month || new Date().toISOString().slice(0, 7);

  return useQuery<TransactionsResponse>({
    queryKey: ["transactions", currentMonth],
    queryFn: () => api.get(`/api/transactions?month=${currentMonth}`),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Hook to fetch budget summary for a month
 */
export function useBudgets(month?: string) {
  const endpoint = month ? `/api/budgets/${month}` : "/api/budgets";

  return useQuery<BudgetSummaryResponse>({
    queryKey: ["budgets", month || "current"],
    queryFn: () => api.get(endpoint),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Hook to fetch recurring expenses summary
 */
export function useRecurring() {
  return useQuery<RecurringSummaryResponse>({
    queryKey: ["recurring"],
    queryFn: () => api.get("/api/recurring"),
    staleTime: 1000 * 60 * 10, // 10 minutes
  });
}

/**
 * Hook to fetch spending trends
 */
export function useTrends(months: number = 6) {
  return useQuery<TrendsResponse>({
    queryKey: ["trends", months],
    queryFn: () => api.get(`/api/trends?months=${months}`),
    staleTime: 1000 * 60 * 10, // 10 minutes
  });
}
