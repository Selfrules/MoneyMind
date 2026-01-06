"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  api,
  getMilestones,
  createMilestone,
  achieveMilestone,
  markCelebrationShown,
  getPendingCelebrations,
  getDebtJourney,
  type MilestoneListResponse,
  type Milestone,
  type CelebrationsResponse,
  type DebtJourneyResponse,
} from "@/lib/api";
import type {
  DebtSummaryResponse,
  DebtTimelineResponse,
  GoalsSummaryResponse,
  Goal,
} from "@/lib/api-types";

/**
 * Hook to fetch debts summary
 */
export function useDebts(activeOnly: boolean = true) {
  return useQuery<DebtSummaryResponse>({
    queryKey: ["debts", activeOnly],
    queryFn: () => api.get(`/api/debts?active_only=${activeOnly}`),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Hook to fetch debt payoff timeline
 */
export function useDebtTimeline(strategy: "avalanche" | "snowball" = "avalanche", extraPayment: number = 0) {
  return useQuery<DebtTimelineResponse>({
    queryKey: ["debt-timeline", strategy, extraPayment],
    queryFn: () => api.get(`/api/debts/timeline?strategy=${strategy}&extra_payment=${extraPayment}`),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Hook to fetch goals summary
 */
export function useGoals(status?: string) {
  const queryParams = status ? `?status=${status}` : "";

  return useQuery<GoalsSummaryResponse>({
    queryKey: ["goals", status || "all"],
    queryFn: () => api.get(`/api/goals${queryParams}`),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Hook to create a new goal
 */
export function useCreateGoal() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (goalData: {
      name: string;
      type: string;
      target_amount: number;
      current_amount?: number;
      priority?: number;
      target_date?: string;
    }) => api.post("/api/goals", goalData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["goals"] });
    },
  });
}

/**
 * Hook to update a goal
 */
export function useUpdateGoal() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      goalId,
      updates,
    }: {
      goalId: number;
      updates: Partial<Goal>;
    }) => api.put(`/api/goals/${goalId}`, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["goals"] });
    },
  });
}

/**
 * Hook to delete a goal
 */
export function useDeleteGoal() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (goalId: number) => api.delete(`/api/goals/${goalId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["goals"] });
    },
  });
}

/**
 * Hook to fetch milestones for a goal
 */
export function useMilestones(goalId: number) {
  return useQuery<MilestoneListResponse>({
    queryKey: ["milestones", goalId],
    queryFn: () => getMilestones(goalId),
    staleTime: 1000 * 60 * 5,
    enabled: goalId > 0,
  });
}

/**
 * Hook to create a milestone
 */
export function useCreateMilestone() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      goalId,
      data,
    }: {
      goalId: number;
      data: {
        milestone_number: number;
        title: string;
        description?: string;
        target_amount?: number;
        target_date?: string;
      };
    }) => createMilestone(goalId, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ["milestones", variables.goalId] });
    },
  });
}

/**
 * Hook to mark milestone as achieved
 */
export function useAchieveMilestone() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      milestoneId,
      actualAmount,
    }: {
      milestoneId: number;
      actualAmount?: number;
    }) => achieveMilestone(milestoneId, actualAmount),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["milestones"] });
      queryClient.invalidateQueries({ queryKey: ["celebrations"] });
    },
  });
}

/**
 * Hook to mark celebration as shown
 */
export function useMarkCelebrationShown() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (milestoneId: number) => markCelebrationShown(milestoneId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["celebrations"] });
    },
  });
}

/**
 * Hook to fetch pending celebrations
 */
export function usePendingCelebrations() {
  return useQuery<CelebrationsResponse>({
    queryKey: ["celebrations", "pending"],
    queryFn: getPendingCelebrations,
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

/**
 * Hook to fetch debt journey data
 */
export function useDebtJourney() {
  return useQuery<DebtJourneyResponse>({
    queryKey: ["debt-journey"],
    queryFn: getDebtJourney,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}
