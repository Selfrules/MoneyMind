"use client";

import { useQuery } from "@tanstack/react-query";
import { getFullReport } from "@/lib/api";
import type { FullFinancialReport } from "@/lib/api";

// Query keys
export const reportQueryKeys = {
  fullReport: (month?: string) => ["full-report", month] as const,
};

// Full Report hook
export function useFullReport(month?: string) {
  return useQuery({
    queryKey: reportQueryKeys.fullReport(month),
    queryFn: () => getFullReport(month),
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchOnWindowFocus: false,
  });
}

// Re-export types for convenience
export type { FullFinancialReport };
