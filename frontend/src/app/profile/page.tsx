"use client";

import { User } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { HealthKPIs, MonthlyReview } from "@/components/profile";
import { useDashboard } from "@/hooks/use-dashboard";
import { useKPIHistory, useMonthlyReport, useProfile } from "@/hooks/use-profile";
import { Skeleton } from "@/components/ui/skeleton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Settings, Wallet, Briefcase } from "lucide-react";

function LoadingState() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-40 w-full" />
      <Skeleton className="h-48 w-full" />
    </div>
  );
}

function formatAmount(amount: number): string {
  return new Intl.NumberFormat("it-IT", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(amount);
}

function HealthTab() {
  const { data: dashboard, isLoading: dashboardLoading } = useDashboard();
  const { data: kpiHistory, isLoading: kpiLoading } = useKPIHistory(12);

  if (dashboardLoading || kpiLoading) return <LoadingState />;
  if (!dashboard) return <p className="text-expense">Errore nel caricamento</p>;

  return (
    <HealthKPIs
      healthScore={dashboard.health_score}
      kpiHistory={kpiHistory}
    />
  );
}

function ReviewTab() {
  // Get previous month
  const prevMonth = new Date();
  prevMonth.setMonth(prevMonth.getMonth() - 1);
  const monthStr = prevMonth.toISOString().slice(0, 7);

  const { data, isLoading, error } = useMonthlyReport(monthStr);

  if (isLoading) return <LoadingState />;
  if (error || !data) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <p className="text-muted-foreground">
            Report mensile non disponibile
          </p>
        </CardContent>
      </Card>
    );
  }

  return <MonthlyReview report={data} />;
}

function SettingsTab() {
  const { data: profile, isLoading } = useProfile();

  if (isLoading) return <LoadingState />;

  return (
    <div className="space-y-4">
      {/* Profile Info */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base flex items-center gap-2">
            <User className="w-5 h-5 text-primary" />
            Profilo
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {profile && (
            <>
              <div className="flex items-center justify-between py-2 border-b border-border/50">
                <div className="flex items-center gap-2">
                  <Wallet className="w-4 h-4 text-muted-foreground" />
                  <span className="text-sm">Reddito mensile</span>
                </div>
                <span className="font-medium">
                  {formatAmount(profile.monthly_net_income)}
                </span>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-border/50">
                <div className="flex items-center gap-2">
                  <Briefcase className="w-4 h-4 text-muted-foreground" />
                  <span className="text-sm">Tipo di reddito</span>
                </div>
                <Badge variant="outline" className="capitalize">
                  {profile.income_type || "Non specificato"}
                </Badge>
              </div>
              <div className="flex items-center justify-between py-2 border-b border-border/50">
                <div className="flex items-center gap-2">
                  <Settings className="w-4 h-4 text-muted-foreground" />
                  <span className="text-sm">Stile coaching</span>
                </div>
                <Badge variant="outline" className="capitalize">
                  {profile.coaching_style || "Bilanciato"}
                </Badge>
              </div>
              <div className="flex items-center justify-between py-2">
                <div className="flex items-center gap-2">
                  <span className="text-sm">Fondo emergenza target</span>
                </div>
                <Badge variant="outline">
                  {profile.emergency_fund_target_months} mesi
                </Badge>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* App Info */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">MoneyMind</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Versione</span>
            <span>5.0 (Next.js)</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Backend</span>
            <span>FastAPI</span>
          </div>
          <p className="text-xs text-muted-foreground pt-2">
            AI-First Personal Finance Coach
          </p>
        </CardContent>
      </Card>
    </div>
  );
}

export default function ProfilePage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <User className="h-6 w-6 text-primary" />
            Profile
          </h1>
          <p className="text-muted-foreground text-sm">
            Salute finanziaria e impostazioni
          </p>
        </div>
      </div>

      <Tabs defaultValue="health" className="w-full">
        <TabsList className="mb-6">
          <TabsTrigger value="health">
            Salute
          </TabsTrigger>
          <TabsTrigger value="review">
            Review
          </TabsTrigger>
          <TabsTrigger value="settings">
            Impostazioni
          </TabsTrigger>
        </TabsList>

        <TabsContent value="health">
          <HealthTab />
        </TabsContent>

        <TabsContent value="review">
          <ReviewTab />
        </TabsContent>

        <TabsContent value="settings">
          <SettingsTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}
