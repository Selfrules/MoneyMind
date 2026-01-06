"use client";

import { useQuery } from "@tanstack/react-query";
import { getFixedDiscretionary } from "@/lib/api";
import type { FixedDiscretionaryResponse } from "@/lib/api";

// Query keys
export const budgetQueryKeys = {
  fixedDiscretionary: (month?: string) => ["fixed-discretionary", month] as const,
};

// Fixed vs Discretionary Budget hook
export function useFixedDiscretionary(month?: string) {
  return useQuery({
    queryKey: budgetQueryKeys.fixedDiscretionary(month),
    queryFn: () => getFixedDiscretionary(month),
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchOnWindowFocus: false,
  });
}

// Re-export types for convenience
export type { FixedDiscretionaryResponse };
