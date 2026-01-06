"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getDashboard,
  getTodayActions,
  completeAction,
  getInsights,
  markInsightRead,
  dismissInsight,
  getXRay,
  getQuickWins,
  getTopQuickWins,
  getScenarioPresets,
  simulatePreset,
} from "@/lib/api";
import type { QuickWinsResponse, ScenarioPreset, ScenarioResult } from "@/lib/api";
import type { CompleteActionRequest } from "@/lib/api-types";

// Query keys
export const queryKeys = {
  dashboard: ["dashboard"] as const,
  actions: ["actions"] as const,
  actionsToday: ["actions", "today"] as const,
  insights: ["insights"] as const,
  xray: ["xray"] as const,
  quickwins: ["quickwins"] as const,
  scenarioPresets: ["scenario", "presets"] as const,
  scenarioResult: ["scenario", "result"] as const,
};

// Dashboard hook
export function useDashboard() {
  return useQuery({
    queryKey: queryKeys.dashboard,
    queryFn: getDashboard,
    staleTime: 1000 * 60, // 1 minute
    refetchOnWindowFocus: true,
  });
}

// Today's actions hook
export function useTodayActions() {
  return useQuery({
    queryKey: queryKeys.actionsToday,
    queryFn: getTodayActions,
    staleTime: 1000 * 30, // 30 seconds
  });
}

// Complete action mutation
export function useCompleteAction() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      actionId,
      request,
    }: {
      actionId: number;
      request: CompleteActionRequest;
    }) => completeAction(actionId, request),
    onSuccess: () => {
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: queryKeys.actionsToday });
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboard });
    },
  });
}

// Insights hook
export function useInsights(unreadOnly = false, limit = 20) {
  return useQuery({
    queryKey: [...queryKeys.insights, { unreadOnly, limit }],
    queryFn: () => getInsights(unreadOnly, limit),
    staleTime: 1000 * 60, // 1 minute
  });
}

// Mark insight read mutation
export function useMarkInsightRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: markInsightRead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.insights });
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboard });
    },
  });
}

// Dismiss insight mutation
export function useDismissInsight() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: dismissInsight,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.insights });
      queryClient.invalidateQueries({ queryKey: queryKeys.dashboard });
    },
  });
}

// X-Ray hook
export function useXRay(month?: string) {
  return useQuery({
    queryKey: [...queryKeys.xray, month],
    queryFn: () => getXRay(month),
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchOnWindowFocus: false,
  });
}

// Quick Wins hook
export function useQuickWins(limit: number = 10) {
  return useQuery({
    queryKey: [...queryKeys.quickwins, limit],
    queryFn: () => getQuickWins(limit),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

// Top Quick Wins hook (for dashboard summary)
export function useTopQuickWins(limit: number = 3) {
  return useQuery({
    queryKey: [...queryKeys.quickwins, "top", limit],
    queryFn: () => getTopQuickWins(limit),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

// Scenario Presets hook
export function useScenarioPresets() {
  return useQuery({
    queryKey: queryKeys.scenarioPresets,
    queryFn: getScenarioPresets,
    staleTime: 1000 * 60 * 30, // 30 minutes (presets don't change often)
  });
}

// Simulate Preset mutation
export function useSimulatePreset() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (presetId: string) => simulatePreset(presetId),
    onSuccess: (data) => {
      // Cache the result
      queryClient.setQueryData([...queryKeys.scenarioResult, data.scenario_name], data);
    },
  });
}
