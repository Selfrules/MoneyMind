"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type {
  UserProfile,
  KPIHistoryResponse,
  MonthlyReportResponse,
} from "@/lib/api-types";

/**
 * Hook to fetch user profile
 */
export function useProfile() {
  return useQuery<UserProfile>({
    queryKey: ["profile"],
    queryFn: () => api.get("/api/profile"),
    staleTime: 1000 * 60 * 10, // 10 minutes
  });
}

/**
 * Hook to update user profile
 */
export function useUpdateProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (updates: Partial<UserProfile>) =>
      api.put("/api/profile", updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["profile"] });
    },
  });
}

/**
 * Hook to fetch KPI history
 */
export function useKPIHistory(months: number = 12) {
  return useQuery<KPIHistoryResponse>({
    queryKey: ["kpi-history", months],
    queryFn: () => api.get(`/api/profile/kpi-history?months=${months}`),
    staleTime: 1000 * 60 * 10, // 10 minutes
  });
}

/**
 * Hook to fetch monthly report
 */
export function useMonthlyReport(month?: string) {
  const currentMonth = month || new Date().toISOString().slice(0, 7);

  return useQuery<MonthlyReportResponse>({
    queryKey: ["monthly-report", currentMonth],
    queryFn: () => api.get(`/api/reports/monthly/${currentMonth}`),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}
