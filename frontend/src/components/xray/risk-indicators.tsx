"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Shield,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Percent,
  Wallet,
  PiggyBank,
} from "lucide-react";

interface RiskIndicatorsData {
  dti_ratio: number;
  emergency_fund_months: number;
  savings_rate: number;
  status: string; // "low", "moderate", "high", "critical"
  issues: string[];
}

interface RiskIndicatorsProps {
  data?: RiskIndicatorsData;
  isLoading?: boolean;
}

function getStatusConfig(status: string) {
  switch (status) {
    case "low":
      return {
        label: "Low Risk",
        color: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
        icon: <CheckCircle className="h-4 w-4" />,
        bgColor: "bg-emerald-500/10",
        borderColor: "border-emerald-500/20",
      };
    case "moderate":
      return {
        label: "Moderate Risk",
        color: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
        icon: <AlertTriangle className="h-4 w-4" />,
        bgColor: "bg-yellow-500/10",
        borderColor: "border-yellow-500/20",
      };
    case "high":
      return {
        label: "High Risk",
        color: "bg-orange-500/20 text-orange-400 border-orange-500/30",
        icon: <AlertTriangle className="h-4 w-4" />,
        bgColor: "bg-orange-500/10",
        borderColor: "border-orange-500/20",
      };
    case "critical":
      return {
        label: "Critical Risk",
        color: "bg-red-500/20 text-red-400 border-red-500/30",
        icon: <XCircle className="h-4 w-4" />,
        bgColor: "bg-red-500/10",
        borderColor: "border-red-500/20",
      };
    default:
      return {
        label: "Unknown",
        color: "bg-muted text-muted-foreground border-border",
        icon: <Shield className="h-4 w-4" />,
        bgColor: "bg-muted/50",
        borderColor: "border-border",
      };
  }
}

interface MetricCardProps {
  icon: React.ReactNode;
  label: string;
  value: string;
  status: "good" | "warning" | "danger";
  description: string;
}

function MetricCard({ icon, label, value, status, description }: MetricCardProps) {
  const statusColors = {
    good: "text-emerald-400",
    warning: "text-yellow-400",
    danger: "text-red-400",
  };

  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <div className="flex items-center gap-2 mb-2">
        <div className="text-muted-foreground">{icon}</div>
        <span className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
          {label}
        </span>
      </div>
      <div className={`text-2xl font-bold ${statusColors[status]}`}>{value}</div>
      <div className="text-xs text-muted-foreground mt-1">{description}</div>
    </div>
  );
}

export function RiskIndicators({ data, isLoading }: RiskIndicatorsProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Risk Indicators</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-24 bg-muted animate-pulse rounded-lg" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const defaultData: RiskIndicatorsData = data || {
    dti_ratio: 0,
    emergency_fund_months: 0,
    savings_rate: 0,
    status: "moderate",
    issues: [],
  };

  const statusConfig = getStatusConfig(defaultData.status);

  // Determine status for each metric
  const getDtiStatus = (dti: number): "good" | "warning" | "danger" => {
    if (dti <= 20) return "good";
    if (dti <= 36) return "warning";
    return "danger";
  };

  const getEmergencyFundStatus = (months: number): "good" | "warning" | "danger" => {
    if (months >= 6) return "good";
    if (months >= 3) return "warning";
    return "danger";
  };

  const getSavingsRateStatus = (rate: number): "good" | "warning" | "danger" => {
    if (rate >= 0.2) return "good";
    if (rate >= 0.1) return "warning";
    return "danger";
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Risk Indicators
          </CardTitle>
          <Badge className={statusConfig.color}>
            {statusConfig.icon}
            <span className="ml-1">{statusConfig.label}</span>
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        {/* Overall Risk Status */}
        <div className={`rounded-lg ${statusConfig.bgColor} border ${statusConfig.borderColor} p-4 mb-4`}>
          <div className="flex items-center gap-2 mb-2">
            {statusConfig.icon}
            <span className="text-sm font-medium text-foreground">Financial Health Status</span>
          </div>
          <div className="text-sm text-muted-foreground">
            {defaultData.status === "low" && "Your finances are in good shape. Keep up the good work!"}
            {defaultData.status === "moderate" && "Some areas need attention. Focus on the issues below."}
            {defaultData.status === "high" && "Multiple risk factors detected. Take action soon."}
            {defaultData.status === "critical" && "Urgent attention needed. Your financial health is at risk."}
          </div>
        </div>

        {/* Metric Cards */}
        <div className="grid grid-cols-3 gap-4 mb-4">
          <MetricCard
            icon={<Percent className="h-4 w-4" />}
            label="DTI Ratio"
            value={`${defaultData.dti_ratio.toFixed(1)}%`}
            status={getDtiStatus(defaultData.dti_ratio)}
            description={
              defaultData.dti_ratio <= 20
                ? "Healthy debt level"
                : defaultData.dti_ratio <= 36
                ? "Manageable but stretched"
                : "Too much debt"
            }
          />
          <MetricCard
            icon={<Wallet className="h-4 w-4" />}
            label="Emergency Fund"
            value={`${defaultData.emergency_fund_months.toFixed(1)} mo`}
            status={getEmergencyFundStatus(defaultData.emergency_fund_months)}
            description={
              defaultData.emergency_fund_months >= 6
                ? "Well protected"
                : defaultData.emergency_fund_months >= 3
                ? "Basic coverage"
                : "Needs building"
            }
          />
          <MetricCard
            icon={<PiggyBank className="h-4 w-4" />}
            label="Savings Rate"
            value={`${defaultData.savings_rate.toFixed(1)}%`}
            status={getSavingsRateStatus(defaultData.savings_rate / 100)}
            description={
              defaultData.savings_rate >= 20
                ? "Excellent saving"
                : defaultData.savings_rate >= 10
                ? "Good progress"
                : "Needs improvement"
            }
          />
        </div>

        {/* Issues List */}
        {defaultData.issues.length > 0 && (
          <div>
            <div className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">
              Issues to Address
            </div>
            <div className="space-y-2">
              {defaultData.issues.map((issue, index) => (
                <div
                  key={index}
                  className="flex items-start gap-2 text-sm text-muted-foreground bg-muted/50 rounded-md p-2"
                >
                  <AlertTriangle className="h-4 w-4 text-yellow-400 mt-0.5 flex-shrink-0" />
                  <span>{issue}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* No Issues State */}
        {defaultData.issues.length === 0 && defaultData.status === "low" && (
          <div className="text-center py-4">
            <CheckCircle className="h-8 w-8 text-emerald-400 mx-auto mb-2" />
            <div className="text-sm text-muted-foreground">No issues detected</div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
