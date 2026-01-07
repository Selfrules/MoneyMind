"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  Wallet,
  Target,
  Flame,
  User,
  TrendingUp,
  TrendingDown,
  Percent,
} from "lucide-react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

interface XRayResponse {
  health_score: number;
  health_grade: string;
  risk_indicators: {
    dti_ratio: number;
    savings_rate: number;
  };
  debt_analysis: {
    total_debt: number;
  };
}

interface NavItem {
  href: string;
  label: string;
  icon: React.ReactNode;
}

const mainNavItems: NavItem[] = [
  {
    href: "/",
    label: "Dashboard",
    icon: <LayoutDashboard className="h-5 w-5" />,
  },
  {
    href: "/money",
    label: "Money",
    icon: <Wallet className="h-5 w-5" />,
  },
  {
    href: "/goals",
    label: "Goals",
    icon: <Target className="h-5 w-5" />,
  },
  {
    href: "/fire",
    label: "FIRE",
    icon: <Flame className="h-5 w-5" />,
  },
  {
    href: "/profile",
    label: "Profile",
    icon: <User className="h-5 w-5" />,
  },
];

interface QuickStat {
  label: string;
  value: string;
  icon: React.ReactNode;
  trend?: "up" | "down" | "neutral";
}

async function fetchXRay(): Promise<XRayResponse> {
  const currentMonth = new Date().toISOString().slice(0, 7);
  const response = await fetch(`${API_BASE_URL}/api/xray?month=${currentMonth}`);
  if (!response.ok) throw new Error("Failed to fetch XRay data");
  return response.json();
}

export function Sidebar() {
  const pathname = usePathname();

  const { data: xray } = useQuery({
    queryKey: ["sidebar-xray"],
    queryFn: fetchXRay,
    staleTime: 60000, // 1 minute
    refetchInterval: 60000,
  });

  const freedomScore = xray?.health_score ?? 0;
  const freedomGrade = xray?.health_grade ?? "?";

  const quickStats: QuickStat[] = xray ? [
    {
      label: "Savings Rate",
      value: `${xray.risk_indicators.savings_rate.toFixed(1)}%`,
      icon: <TrendingUp className="h-4 w-4 text-emerald-400" />,
      trend: xray.risk_indicators.savings_rate > 20 ? "up" : "down",
    },
    {
      label: "Debt",
      value: `€${(xray.debt_analysis.total_debt / 1000).toFixed(1)}k`,
      icon: <TrendingDown className="h-4 w-4 text-red-400" />,
      trend: "neutral",
    },
    {
      label: "DTI",
      value: `${xray.risk_indicators.dti_ratio.toFixed(1)}%`,
      icon: <Percent className="h-4 w-4 text-yellow-400" />,
      trend: xray.risk_indicators.dti_ratio < 36 ? "up" : "down",
    },
  ] : [];

  const getGradeColor = (grade: string) => {
    switch (grade) {
      case "A":
        return "text-emerald-400";
      case "B":
        return "text-green-400";
      case "C":
        return "text-yellow-400";
      case "D":
        return "text-orange-400";
      case "F":
        return "text-red-400";
      default:
        return "text-muted-foreground";
    }
  };

  const displayStats: QuickStat[] = quickStats.length > 0 ? quickStats : [
    {
      label: "Savings Rate",
      value: "--",
      icon: <TrendingUp className="h-4 w-4 text-emerald-400" />,
      trend: "neutral",
    },
    {
      label: "Debt",
      value: "--",
      icon: <TrendingDown className="h-4 w-4 text-red-400" />,
      trend: "neutral",
    },
    {
      label: "DTI",
      value: "--",
      icon: <Percent className="h-4 w-4 text-yellow-400" />,
      trend: "neutral",
    },
  ];

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-[250px] border-r border-border bg-sidebar flex flex-col">
      {/* Logo */}
      <div className="flex h-16 items-center gap-2 border-b border-border px-6">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
          <Wallet className="h-5 w-5 text-primary-foreground" />
        </div>
        <span className="text-lg font-semibold text-foreground">MoneyMind</span>
      </div>

      {/* Freedom Score Badge */}
      <div className="mx-4 mt-4 rounded-xl bg-card p-4">
        <div className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">
          Freedom Score
        </div>
        <div className="flex items-center gap-3">
          <div className={cn(
            "flex h-12 w-12 items-center justify-center rounded-xl text-xl font-bold",
            "bg-primary/10 border border-primary/20",
            getGradeColor(freedomGrade)
          )}>
            {freedomGrade}
          </div>
          <div>
            <div className="text-2xl font-bold text-foreground">{freedomScore}</div>
            <div className="text-xs text-muted-foreground">/ 100</div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4">
        <div className="text-xs font-medium text-muted-foreground uppercase tracking-wider px-3 mb-2">
          Navigation
        </div>
        <ul className="space-y-1">
          {mainNavItems.map((item) => {
            const isActive = pathname === item.href ||
              (item.href !== "/" && pathname.startsWith(item.href));

            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-primary/10 text-primary"
                      : "text-muted-foreground hover:bg-accent hover:text-foreground"
                  )}
                >
                  {item.icon}
                  {item.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Quick Stats */}
      <div className="border-t border-border p-4">
        <div className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3">
          Quick Stats
        </div>
        <div className="space-y-2">
          {displayStats.map((stat, index) => (
            <div key={index} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {stat.icon}
                <span className="text-sm text-muted-foreground">{stat.label}</span>
              </div>
              <span className="text-sm font-medium text-foreground">{stat.value}</span>
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
}
