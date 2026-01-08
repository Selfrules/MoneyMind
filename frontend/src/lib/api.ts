/**
 * MoneyMind API Client
 */
import type {
  DashboardResponse,
  DailyActionsResponse,
  InsightsResponse,
  CompleteActionRequest,
  XRayResponse,
  DeepAnalysisResponse,
  QuickInsightsResponse,
} from "./api-types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

class ApiError extends Error {
  constructor(
    public status: number,
    message: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new ApiError(response.status, errorText || response.statusText);
  }

  return response.json();
}

// Dashboard API
export async function getDashboard(): Promise<DashboardResponse> {
  return fetchApi<DashboardResponse>("/api/dashboard");
}

// Actions API
export async function getTodayActions(): Promise<DailyActionsResponse> {
  return fetchApi<DailyActionsResponse>("/api/actions/today");
}

export async function completeAction(
  actionId: number,
  request: CompleteActionRequest
): Promise<{ success: boolean; status: string }> {
  return fetchApi(`/api/actions/${actionId}/complete`, {
    method: "POST",
    body: JSON.stringify(request),
  });
}

export async function getActionsHistory(
  days: number = 7
): Promise<{ actions: unknown[]; days: number }> {
  return fetchApi(`/api/actions/history?days=${days}`);
}

// Insights API
export async function getInsights(
  unreadOnly: boolean = false,
  limit: number = 20
): Promise<InsightsResponse> {
  const params = new URLSearchParams();
  if (unreadOnly) params.append("unread_only", "true");
  params.append("limit", limit.toString());
  return fetchApi<InsightsResponse>(`/api/insights?${params}`);
}

export async function markInsightRead(
  insightId: number
): Promise<{ success: boolean }> {
  return fetchApi(`/api/insights/${insightId}/read`, {
    method: "POST",
  });
}

export async function dismissInsight(
  insightId: number
): Promise<{ success: boolean }> {
  return fetchApi(`/api/insights/${insightId}/dismiss`, {
    method: "POST",
  });
}

// Health check
export async function healthCheck(): Promise<{ status: string; version: string }> {
  return fetchApi("/health");
}

// X-Ray API
export async function getXRay(month?: string): Promise<XRayResponse> {
  const params = new URLSearchParams();
  if (month) params.append("month", month);
  const queryString = params.toString();
  return fetchApi<XRayResponse>(`/api/xray${queryString ? `?${queryString}` : ""}`);
}

// Quick Wins API
export interface QuickWin {
  id: string;
  type: string;
  title: string;
  description: string;
  estimated_savings_monthly: number;
  estimated_savings_annual: number;
  payoff_impact_days: number;
  effort_level: string;
  time_to_complete: string;
  quick_win_score: number;
  confidence: number;
  action_steps: string[];
  cta_text: string;
  cta_url?: string;
  category?: string;
  provider?: string;
  recurring_expense_id?: number;
  debt_id?: number;
  icon: string;
  priority_badge: string;
}

export interface QuickWinsResponse {
  wins: QuickWin[];
  total_monthly_savings: number;
  total_annual_savings: number;
  total_payoff_days_saved: number;
  easy_wins_count: number;
  medium_wins_count: number;
  execution_order: string[];
}

export async function getQuickWins(limit: number = 10): Promise<QuickWinsResponse> {
  return fetchApi<QuickWinsResponse>(`/api/quickwins?limit=${limit}`);
}

export async function getTopQuickWins(limit: number = 3): Promise<{ wins: QuickWin[]; total_count: number; total_monthly_savings: number }> {
  return fetchApi(`/api/quickwins/top?limit=${limit}`);
}

// Impact Calculator API
export interface ScenarioPreset {
  id: string;
  name: string;
  description: string;
  type: string;
  config: Record<string, unknown>;
}

export interface FinancialState {
  monthly_income: number;
  monthly_expenses: number;
  monthly_savings: number;
  savings_rate: number;
  total_debt: number;
  monthly_debt_payment: number;
  debt_payoff_date: string | null;
  debt_payoff_months: number;
  emergency_fund_months: number;
  fire_number: number;
  fire_date: string | null;
  fire_years: number;
}

export interface ScenarioImpact {
  monthly_savings_delta: number;
  annual_savings_delta: number;
  debt_payoff_months_delta: number;
  debt_payoff_days_delta: number;
  fire_years_delta: number;
  total_interest_saved: number;
  savings_rate_delta: number;
  summary: string;
  highlights: string[];
}

export interface ScenarioResult {
  scenario_name: string;
  scenario_type: string;
  description: string;
  current_state: FinancialState;
  simulated_state: FinancialState;
  impact: ScenarioImpact;
  confidence: number;
  assumptions: string[];
  warnings: string[];
  preset?: ScenarioPreset;
}

export async function getScenarioPresets(): Promise<{ presets: ScenarioPreset[] }> {
  return fetchApi(`/api/impact/presets`);
}

export async function simulatePreset(presetId: string): Promise<ScenarioResult> {
  return fetchApi(`/api/impact/simulate-preset/${presetId}`, {
    method: "POST",
  });
}

export async function simulateExpenseChange(category: string, changePercent?: number, changeAmount?: number): Promise<ScenarioResult> {
  return fetchApi(`/api/impact/expense`, {
    method: "POST",
    body: JSON.stringify({ category, change_percent: changePercent, change_amount: changeAmount }),
  });
}

export async function simulateIncomeChange(changeAmount: number): Promise<ScenarioResult> {
  return fetchApi(`/api/impact/income`, {
    method: "POST",
    body: JSON.stringify({ change_amount: changeAmount }),
  });
}

// Milestone Types
export interface Milestone {
  id: number;
  goal_id: number;
  milestone_number: number;
  title: string;
  description?: string;
  target_amount?: number;
  target_date?: string;
  status: "pending" | "achieved" | "missed";
  achieved_at?: string;
  actual_amount?: number;
  celebration_shown: boolean;
  goal_name?: string;
}

export interface MilestoneListResponse {
  milestones: Milestone[];
  total_count: number;
  achieved_count: number;
  pending_count: number;
}

export interface Celebration {
  id: number;
  goal_id: number;
  goal_name: string;
  milestone_number: number;
  title: string;
  description?: string;
  target_amount?: number;
  actual_amount?: number;
  achieved_at: string;
}

export interface CelebrationsResponse {
  celebrations: Celebration[];
  total_count: number;
}

// Debt Journey Types
export interface DebtPhaseProgress {
  phase: string;
  phase_number: number;
  progress_percent: number;
  next_milestone?: {
    title: string;
    debt_name?: string;
    remaining?: number;
  };
  debts_total: number;
  debts_eliminated: number;
  debts_remaining: number;
  is_debt_free: boolean;
  message: string;
}

export interface DebtJourneyMilestone {
  order: number;
  debt_name: string;
  estimated_date: string;
  estimated_months: number;
}

export interface DebtJourneyResponse {
  phase_info: DebtPhaseProgress;
  total_original_debt: number;
  total_current_debt: number;
  total_paid: number;
  overall_progress_percent: number;
  monthly_payment: number;
  projected_payoff_date?: string;
  months_remaining: number;
  interest_remaining: number;
  potential_interest_saved: number;
  milestones: DebtJourneyMilestone[];
}

// Milestone API
export async function getMilestones(goalId: number): Promise<MilestoneListResponse> {
  return fetchApi(`/api/goals/${goalId}/milestones`);
}

export async function createMilestone(goalId: number, data: {
  milestone_number: number;
  title: string;
  description?: string;
  target_amount?: number;
  target_date?: string;
}): Promise<Milestone> {
  return fetchApi(`/api/goals/${goalId}/milestones`, {
    method: "POST",
    body: JSON.stringify({ ...data, goal_id: goalId }),
  });
}

export async function achieveMilestone(milestoneId: number, actualAmount?: number): Promise<{ status: string }> {
  const params = actualAmount ? `?actual_amount=${actualAmount}` : "";
  return fetchApi(`/api/milestones/${milestoneId}/achieve${params}`, {
    method: "POST",
  });
}

export async function markCelebrationShown(milestoneId: number): Promise<{ status: string }> {
  return fetchApi(`/api/milestones/${milestoneId}/celebration-shown`, {
    method: "POST",
  });
}

export async function getPendingCelebrations(): Promise<CelebrationsResponse> {
  return fetchApi(`/api/celebrations/pending`);
}

// Debt Journey API
export async function getDebtJourney(): Promise<DebtJourneyResponse> {
  return fetchApi(`/api/debts/journey`);
}

// FIRE Calculator Types
export interface FIREMilestone {
  name: string;
  target_amount: number;
  target_percent: number;
  years_to_reach: number;
  projected_date: string;
  description: string;
  is_achieved: boolean;
}

export interface FIREScenario {
  return_rate: number;
  expenses: number;
  fire_number: number;
  years_to_fire: number;
  fire_date: string;
}

export interface FIRESummaryResponse {
  fire_number: number;
  current_net_worth: number;
  progress_percent: number;
  years_to_fire: number;
  months_to_fire: number;
  fire_date: string;
  monthly_investment: number;
  annual_expenses: number;
  expected_return: number;
  withdrawal_rate: number;
  savings_rate: number;
  milestones: FIREMilestone[];
  scenarios: {
    conservative: FIREScenario;
    expected: FIREScenario;
    optimistic: FIREScenario;
  };
}

export interface FIREProjection {
  month: string;
  months_from_now: number;
  net_worth: number;
  contributions: number;
  investment_gains: number;
  fire_percent: number;
}

export interface FIREProjectionsResponse {
  projections: FIREProjection[];
  fire_number: number;
  fire_date: string;
  years_to_fire: number;
}

export interface FIRESensitivityEntry {
  return_rate?: number;
  delta?: number;
  expenses_change?: number;
  new_expenses?: number;
  new_fire_number?: number;
  years_to_fire: number;
  fire_date: string;
}

export interface FIRESensitivityResponse {
  base_case: {
    years_to_fire: number;
    fire_date: string;
    fire_number: number;
  };
  return_sensitivity: FIRESensitivityEntry[];
  expense_sensitivity: FIRESensitivityEntry[];
  scenarios: {
    conservative: FIREScenario;
    expected: FIREScenario;
    optimistic: FIREScenario;
  };
}

export interface FIREExtraSavingsResponse {
  current: {
    monthly_savings: number;
    years_to_fire: number;
    fire_date: string;
  };
  with_extra: {
    monthly_savings: number;
    extra_amount: number;
    years_to_fire: number;
    fire_date: string;
  };
  impact: {
    years_saved: number;
    months_saved: number;
    time_saved_description: string;
  };
}

// FIRE Calculator API
export async function getFIRESummary(
  expectedReturn: number = 0.07,
  withdrawalRate: number = 0.04
): Promise<FIRESummaryResponse> {
  const params = new URLSearchParams({
    expected_return: expectedReturn.toString(),
    withdrawal_rate: withdrawalRate.toString(),
  });
  return fetchApi(`/api/fire/summary?${params}`);
}

export async function calculateFIRE(data: {
  annual_expenses: number;
  current_net_worth?: number;
  monthly_investment: number;
  expected_return?: number;
  inflation_rate?: number;
  withdrawal_rate?: number;
}): Promise<FIRESummaryResponse> {
  return fetchApi("/api/fire/calculate", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getFIREProjections(
  years: number = 30,
  expectedReturn: number = 0.07,
  withdrawalRate: number = 0.04
): Promise<FIREProjectionsResponse> {
  const params = new URLSearchParams({
    years: years.toString(),
    expected_return: expectedReturn.toString(),
    withdrawal_rate: withdrawalRate.toString(),
  });
  return fetchApi(`/api/fire/projections?${params}`);
}

export async function getFIRESensitivity(): Promise<FIRESensitivityResponse> {
  return fetchApi("/api/fire/sensitivity");
}

export async function simulateExtraSavings(
  extraMonthly: number
): Promise<FIREExtraSavingsResponse> {
  return fetchApi(`/api/fire/simulate-extra-savings?extra_monthly=${extraMonthly}`, {
    method: "POST",
  });
}

// Generic API methods for flexible use
export const api = {
  get: <T>(endpoint: string) => fetchApi<T>(endpoint),

  post: <T>(endpoint: string, data?: unknown) =>
    fetchApi<T>(endpoint, {
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    }),

  put: <T>(endpoint: string, data?: unknown) =>
    fetchApi<T>(endpoint, {
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
    }),

  delete: <T>(endpoint: string) =>
    fetchApi<T>(endpoint, {
      method: "DELETE",
    }),
};

export { ApiError };

// Full Financial Report Types
export interface FullReportExecutiveSummary {
  health_score: number;
  health_grade: string;
  total_income: number;
  total_expenses: number;
  net_savings: number;
  savings_rate: number;
  total_debt: number;
  debt_payment_monthly: number;
  months_to_debt_free: number | null;
  overall_judgment: "excellent" | "good" | "warning" | "critical";
  key_issues: string[];
  key_wins: string[];
}

export interface CategorySpendingItem {
  category: string;
  icon: string;
  amount_current: number;
  amount_avg_3m: number;
  benchmark: number;
  judgment: "excellent" | "good" | "warning" | "critical";
  variance_percent: number;
  notes: string;
  suggestion: string | null;
}

export interface SubscriptionAuditItem {
  name: string;
  category: string;
  monthly_cost: number;
  annual_cost: number;
  action: "cancel" | "downgrade" | "review" | "keep" | "negotiate";
  reason: string;
  potential_savings: number;
  value_score: number;
  alternative: string | null;
}

export interface DebtPriorityItem {
  id: number;
  name: string;
  balance: number;
  apr: number;
  monthly_payment: number;
  interest_monthly: number;
  principal_monthly: number;
  priority_score: number;
  months_remaining: number;
  payoff_date: string | null;
  total_remaining_cost: number;
}

export interface RecommendationItem {
  id: string;
  title: string;
  description: string;
  impact_monthly: number;
  impact_annual: number;
  difficulty: "easy" | "medium" | "hard";
  category: string;
  action_steps: string[];
  priority: number;
}

export interface MonthComparisonItem {
  category: string;
  current_month: number;
  previous_month: number;
  delta: number;
  delta_percent: number;
  trend: "up" | "down" | "stable";
}

export interface FullFinancialReport {
  report_date: string;
  month: string;
  executive_summary: FullReportExecutiveSummary;
  category_spending: CategorySpendingItem[];
  subscription_audit: SubscriptionAuditItem[];
  debt_priority: DebtPriorityItem[];
  recommendations: RecommendationItem[];
  month_comparison: MonthComparisonItem[];
}

// Full Financial Report API
export async function getFullReport(month?: string): Promise<FullFinancialReport> {
  const params = new URLSearchParams();
  if (month) params.append("month", month);
  const queryString = params.toString();
  return fetchApi<FullFinancialReport>(`/api/report/full${queryString ? `?${queryString}` : ""}`);
}


// Fixed vs Discretionary Budget Types (v7.0)
export interface CategoryBudgetItem {
  category: string;
  budget_type: "fixed" | "discretionary";
  monthly_budget: number;
  spent_this_month: number;
  remaining: number;
  days_left_in_month: number;
  daily_budget_remaining: number;
  percent_used: number;
  status: "on_track" | "warning" | "over_budget";
}

export interface FixedDiscretionaryResponse {
  month: string;
  total_income: number;
  total_fixed: number;
  total_discretionary_budget: number;
  total_discretionary_spent: number;
  discretionary_remaining: number;
  savings_potential: number;
  fixed_breakdown: CategoryBudgetItem[];
  discretionary_breakdown: CategoryBudgetItem[];
}

// Fixed vs Discretionary Budget API
export async function getFixedDiscretionary(month?: string): Promise<FixedDiscretionaryResponse> {
  const params = new URLSearchParams();
  if (month) params.append("month", month);
  const queryString = params.toString();
  return fetchApi<FixedDiscretionaryResponse>(`/api/budgets/fixed-discretionary${queryString ? `?${queryString}` : ""}`);
}

// Deep Analysis API (AI-powered)
export async function getDeepAnalysis(): Promise<DeepAnalysisResponse> {
  return fetchApi<DeepAnalysisResponse>("/api/deep-analysis");
}

// Quick Insights API (rule-based, no AI)
export async function getQuickInsights(): Promise<QuickInsightsResponse> {
  return fetchApi<QuickInsightsResponse>("/api/quick-insights");
}
