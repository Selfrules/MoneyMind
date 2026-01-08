/**
 * MoneyMind API Types
 * Auto-generated from FastAPI OpenAPI schema
 */

// Enums
export type ActionStatus = "pending" | "completed" | "skipped" | "postponed";
export type InsightSeverity = "high" | "medium" | "low";

// KPIs
export interface KPIs {
  total_balance: number;
  monthly_income: number;
  monthly_expenses: number;
  savings_rate: number;
  dti_ratio: number;
  emergency_fund_months: number;
  net_worth: number;
  total_debt: number;
}

// Health Score
export interface HealthScore {
  total_score: number;
  grade: string;
  savings_score: number;
  dti_score: number;
  emergency_fund_score: number;
  net_worth_trend_score: number;
  phase: "Debt Payoff" | "Wealth Building";
}

// Month Summary
export interface MonthSummary {
  month: string;
  income: number;
  expenses: number;
  savings: number;
  vs_baseline_savings: number;
  on_track: boolean;
}

// Scenario Comparison
export interface ScenarioComparison {
  current_payoff_date: string | null;
  current_payoff_months: number | null;
  moneymind_payoff_date: string | null;
  moneymind_payoff_months: number | null;
  months_saved: number | null;
  interest_saved: number | null;
}

// Dashboard Response
export interface DashboardResponse {
  kpis: KPIs;
  health_score: HealthScore;
  month_summary: MonthSummary;
  scenario_comparison: ScenarioComparison | null;
  pending_actions_count: number;
  unread_insights_count: number;
}

// Daily Action
export interface DailyAction {
  id: number;
  action_date: string;
  priority: number;
  title: string;
  description: string | null;
  action_type: string | null;
  impact_type: string | null;
  estimated_impact_monthly: number | null;
  estimated_impact_payoff_days: number | null;
  status: ActionStatus;
  completed_at: string | null;
  category_name: string | null;
  debt_name: string | null;
  recurring_expense_name: string | null;
}

// Daily Actions Response
export interface DailyActionsResponse {
  date: string;
  actions: DailyAction[];
  completed_count: number;
  pending_count: number;
}

// Insight
export interface Insight {
  id: number;
  type: string;
  category: string | null;
  severity: InsightSeverity;
  title: string;
  message: string;
  action_text: string | null;
  is_read: boolean;
  is_dismissed: boolean;
  created_at: string;
  category_name: string | null;
  category_icon: string | null;
}

// Insights Response
export interface InsightsResponse {
  insights: Insight[];
  unread_count: number;
  total_count: number;
}

// Complete Action Request
export interface CompleteActionRequest {
  decision: "accepted" | "rejected" | "postponed";
  notes?: string;
}

// ==================== MONEY TAB TYPES ====================

// Transaction
export interface Transaction {
  id: number;
  date: string;
  description: string;
  amount: number;
  category_id: number | null;
  category_name: string | null;
  category_icon: string | null;
  bank: string | null;
  account_type: string | null;
  type: string | null;
  is_recurring: boolean;
}

// Transaction Group (by date)
export interface TransactionGroup {
  date: string;
  transactions: Transaction[];
  daily_total: number;
}

// Transactions Response
export interface TransactionsResponse {
  transactions: TransactionGroup[];
  total_count: number;
  total_income: number;
  total_expenses: number;
  month: string;
}

// Budget Status
export interface BudgetStatus {
  category_id: number;
  category_name: string;
  category_icon: string | null;
  budget_amount: number;
  spent_amount: number;
  remaining: number;
  percent_used: number;
  status: "ok" | "warning" | "exceeded";
}

// Budget Summary Response
export interface BudgetSummaryResponse {
  month: string;
  total_budget: number;
  total_spent: number;
  total_remaining: number;
  categories: BudgetStatus[];
  over_budget_count: number;
  warning_count: number;
}

// Recurring Expense
export interface RecurringExpense {
  id: number;
  pattern_name: string;
  category_id: number | null;
  category_name: string | null;
  category_icon: string | null;
  frequency: "monthly" | "quarterly" | "annual";
  avg_amount: number;
  last_amount: number | null;
  trend_percent: number | null;
  last_occurrence: string | null;
  occurrence_count: number;
  provider: string | null;
  is_essential: boolean;
  optimization_status: string;
  optimization_suggestion: string | null;
  estimated_savings_monthly: number | null;
  // FASE 2: Due dates and AI suggestions
  next_due_date: string | null;
  days_until_due: number | null;
  budget_impact_percent: number | null;
  ai_action: "keep" | "cancel" | "renegotiate" | "review" | null;
  ai_reason: string | null;
  ai_priority: "high" | "medium" | "low" | null;
}

// Recurring Summary Response
export interface RecurringSummaryResponse {
  total_monthly: number;
  essential_monthly: number;
  non_essential_monthly: number;
  potential_savings: number;
  expenses: RecurringExpense[];
  optimizable_count: number;
  // FASE 2: Due this month and priorities
  due_this_month_count: number;
  due_this_month_total: number;
  high_priority_actions: number;
}

// Monthly Trend
export interface MonthlyTrend {
  month: string;
  income: number;
  expenses: number;
  savings: number;
}

// Category Trend
export interface CategoryTrend {
  category_name: string;
  category_icon: string | null;
  monthly_data: number[];
  average: number;
  trend_percent: number | null;
}

// Trends Response
export interface TrendsResponse {
  months: string[];
  monthly_totals: MonthlyTrend[];
  top_categories: CategoryTrend[];
  average_monthly_spending: number;
  spending_trend_percent: number | null;
}

// ==================== GOALS TAB TYPES ====================

// Debt
export interface Debt {
  id: number;
  name: string;
  type: string;
  original_amount: number;
  current_balance: number;
  interest_rate: number;
  monthly_payment: number;
  payment_day: number;
  start_date: string | null;
  is_active: boolean;
  payoff_date: string | null;
  months_remaining: number | null;
  total_interest: number | null;
  priority_rank?: number | null;
}

// Debt Summary Response
export interface DebtSummaryResponse {
  total_debt: number;
  total_monthly_payment: number;
  debts: Debt[];
  active_count: number;
  projected_debt_free_date: string | null;
  months_to_freedom: number | null;
}

// Debt Timeline Entry
export interface DebtTimelineEntry {
  month: string;
  debt_id: number;
  debt_name: string;
  planned_payment: number;
  extra_payment: number;
  balance_after: number;
  is_payoff_month: boolean;
}

// Debt Timeline Response
export interface DebtTimelineResponse {
  strategy: string;
  timeline: DebtTimelineEntry[];
  total_months: number;
  total_interest_paid: number;
  debt_free_date: string | null;
  monthly_extra_available: number;
}

// Goal
export interface Goal {
  id: number;
  name: string;
  type: string;
  target_amount: number;
  current_amount: number;
  priority: number;
  status: string;
  target_date: string | null;
  progress_percent: number;
  monthly_contribution_needed: number | null;
  months_remaining: number | null;
}

// Goals Summary Response
export interface GoalsSummaryResponse {
  goals: Goal[];
  total_target: number;
  total_current: number;
  overall_progress: number;
  active_count: number;
  completed_count: number;
}

// ==================== PROFILE TAB TYPES ====================

// User Profile
export interface UserProfile {
  id: number;
  income_type: string | null;
  monthly_net_income: number;
  risk_tolerance: string | null;
  financial_knowledge: string | null;
  coaching_style: string | null;
  emergency_fund_target_months: number;
  created_at: string | null;
}

// KPI History Entry
export interface KPIHistoryEntry {
  month: string;
  net_worth: number;
  total_debt: number;
  savings_rate: number;
  dti_ratio: number;
  emergency_fund_months: number;
}

// KPI History Response
export interface KPIHistoryResponse {
  entries: KPIHistoryEntry[];
  months_count: number;
  trend_direction: string;
}

// Top Category in Report
export interface TopCategory {
  category: string;
  amount: number;
}

// Monthly Report Response
export interface MonthlyReportResponse {
  month: string;
  income: number;
  expenses: number;
  savings: number;
  savings_rate: number;
  vs_previous_month_savings: number | null;
  top_expense_categories: TopCategory[];
  budget_performance: number;
  debt_payments_made: number;
  debt_balance_reduction: number;
  insights_generated: number;
  actions_completed: number;
  actions_total: number;
}

// ==================== X-RAY TYPES ====================

// Cash Flow Breakdown
export interface CashFlowBreakdown {
  income: number;
  essential_expenses: number;
  debt_payments: number;
  discretionary: number;
  available_for_savings: number;
  total_expenses: number;
  savings_rate: number;
}

// Debt Detail
export interface DebtDetail {
  id: number;
  name: string;
  balance: number;
  rate: number;
  payment: number;
  burden_percent: number;
}

// Highest Rate Debt
export interface HighestRateDebt {
  name: string;
  rate: number;
  balance: number;
}

// Debt Analysis
export interface DebtAnalysis {
  total_debt: number;
  total_monthly_payments: number;
  total_interest_paid_ytd: number;
  total_interest_remaining: number;
  debt_burden_percent: number;
  months_to_freedom: number | null;
  freedom_date: string | null;
  highest_rate_debt: HighestRateDebt | null;
  debts: DebtDetail[];
}

// Saving Opportunity
export interface SavingOpportunity {
  category: string;
  current: number;
  baseline: number;
  potential_savings: number;
  impact_monthly: number;
  impact_annual: number;
  recommendation: string;
  priority: number;
}

// Risk Indicators
export interface RiskIndicators {
  dti_ratio: number;
  emergency_fund_months: number;
  savings_rate: number;
  status: "low" | "moderate" | "high" | "critical";
  issues: string[];
}

// Phase Info
export interface PhaseInfo {
  current_phase: string;
  progress_percent: number;
  next_milestone: string;
  days_in_phase: number;
}

// X-Ray Response
export interface XRayResponse {
  analysis_date: string;
  month: string;
  cash_flow: CashFlowBreakdown;
  debt_analysis: DebtAnalysis;
  savings_potential: SavingOpportunity[];
  risk_indicators: RiskIndicators;
  phase: string;
  phase_info: PhaseInfo;
  health_score: number;
  health_grade: string;
  summary: string;
}

// ==================== DEEP ANALYSIS TYPES ====================

// Recurring Insight from AI Analysis
export interface RecurringInsight {
  name: string;
  category: string;
  monthly_amount: number;
  type: "subscription" | "service" | "financing" | "essential";
  recommendation: "keep" | "review" | "cancel" | "negotiate";
  reason: string;
  potential_savings: number | null;
}

// Anomaly Detail
export interface AnomalyDetail {
  description: string;
  date: string;
  amount: number;
  anomaly_type: "unusual_amount" | "duplicate" | "unexpected_category" | "timing";
  explanation: string;
}

// Savings Opportunity from Deep Analysis
export interface DeepSavingsOpportunity {
  area: string;
  current_spending: number;
  suggested_target: number;
  potential_savings: number;
  action: string;
}

// Categorization Issue
export interface CategorizationIssue {
  transaction_desc: string;
  current_category: string;
  suggested_category: string;
  reason: string;
}

// Monthly Overview
export interface MonthlyOverview {
  income: number;
  fixed_expenses: number;
  discretionary_expenses: number;
  savings: number;
  debt_payments: number;
}

// Deep Analysis Response
export interface DeepAnalysisResponse {
  summary: string;
  financial_health_score: number;
  monthly_overview: MonthlyOverview;
  recurring_insights: RecurringInsight[];
  anomalies: AnomalyDetail[];
  savings_opportunities: DeepSavingsOpportunity[];
  categorization_issues: CategorizationIssue[];
  recommendations: string[];
}

// Quick Insights Types (non-AI)
export interface QuickInsight {
  type: "positive" | "neutral" | "warning" | "info";
  title: string;
  message: string;
}

export interface QuickInsightsResponse {
  monthly_summary: {
    avg_income: number;
    avg_expenses: number;
    avg_savings: number;
    savings_rate: number;
  };
  top_categories: Array<{
    category: string;
    total: number;
    monthly_avg: number;
  }>;
  recurring_summary: {
    active_count: number;
    total_monthly: number;
    percent_of_income: number;
  };
  insights: QuickInsight[];
}
