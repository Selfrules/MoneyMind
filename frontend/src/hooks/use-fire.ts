"use client";

import { useQuery, useMutation } from "@tanstack/react-query";
import {
  getFIRESummary,
  calculateFIRE,
  getFIREProjections,
  getFIRESensitivity,
  simulateExtraSavings,
  type FIRESummaryResponse,
  type FIREProjectionsResponse,
  type FIRESensitivityResponse,
  type FIREExtraSavingsResponse,
} from "@/lib/api";

export const fireQueryKeys = {
  summary: ["fire", "summary"] as const,
  projections: ["fire", "projections"] as const,
  sensitivity: ["fire", "sensitivity"] as const,
  extraSavings: ["fire", "extra-savings"] as const,
};

/**
 * Hook to fetch FIRE summary based on user's financial data
 */
export function useFIRESummary(
  expectedReturn: number = 0.07,
  withdrawalRate: number = 0.04
) {
  return useQuery<FIRESummaryResponse>({
    queryKey: [...fireQueryKeys.summary, expectedReturn, withdrawalRate],
    queryFn: () => getFIRESummary(expectedReturn, withdrawalRate),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Hook to calculate FIRE with custom parameters
 */
export function useCalculateFIRE() {
  return useMutation({
    mutationFn: (data: {
      annual_expenses: number;
      current_net_worth?: number;
      monthly_investment: number;
      expected_return?: number;
      inflation_rate?: number;
      withdrawal_rate?: number;
    }) => calculateFIRE(data),
  });
}

/**
 * Hook to fetch FIRE projections for charting
 */
export function useFIREProjections(
  years: number = 30,
  expectedReturn: number = 0.07,
  withdrawalRate: number = 0.04
) {
  return useQuery<FIREProjectionsResponse>({
    queryKey: [...fireQueryKeys.projections, years, expectedReturn, withdrawalRate],
    queryFn: () => getFIREProjections(years, expectedReturn, withdrawalRate),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Hook to fetch FIRE sensitivity analysis
 */
export function useFIRESensitivity() {
  return useQuery<FIRESensitivityResponse>({
    queryKey: fireQueryKeys.sensitivity,
    queryFn: getFIRESensitivity,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Hook to simulate extra savings impact
 */
export function useSimulateExtraSavings() {
  return useMutation({
    mutationFn: (extraMonthly: number) => simulateExtraSavings(extraMonthly),
  });
}
