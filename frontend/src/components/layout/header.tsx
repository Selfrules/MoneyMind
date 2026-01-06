"use client";

import { Bell, ChevronDown, RefreshCw, Code2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

interface PhaseInfo {
  name: string;
  progress: number;
}

interface HeaderProps {
  title?: string;
  currentPhase?: PhaseInfo;
  notificationCount?: number;
  userName?: string;
}

const phaseColors: Record<string, string> = {
  diagnosi: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  ottimizzazione: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
  sicurezza: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
  crescita: "bg-purple-500/20 text-purple-400 border-purple-500/30",
};

export function Header({
  title = "Dashboard",
  currentPhase,
  notificationCount = 0,
  userName,
}: HeaderProps) {
  const queryClient = useQueryClient();
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefreshAll = async () => {
    setIsRefreshing(true);
    await queryClient.invalidateQueries();
    setTimeout(() => setIsRefreshing(false), 500);
  };

  return (
    <header className="fixed top-0 left-[250px] right-0 z-30 h-16 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-full items-center justify-between px-6">
        {/* Left: Page Title + Phase Indicator */}
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-semibold text-foreground">{title}</h1>

          {currentPhase && (
            <div
              className={cn(
                "flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-medium",
                phaseColors[currentPhase.name.toLowerCase()] || phaseColors.diagnosi
              )}
            >
              <span className="capitalize">{currentPhase.name}</span>
              <span className="opacity-60">|</span>
              <span>{currentPhase.progress}%</span>
            </div>
          )}
        </div>

        {/* Right: Dev Tools + Notifications + User */}
        <div className="flex items-center gap-2">
          {/* Dev Tools - Refresh All Queries */}
          {process.env.NODE_ENV === "development" && (
            <button
              onClick={handleRefreshAll}
              className="flex h-9 items-center gap-1.5 rounded-lg px-2.5 text-xs font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
              aria-label="Refresh all data"
              title="Refresh all data"
            >
              <RefreshCw className={cn("h-4 w-4", isRefreshing && "animate-spin")} />
              <span className="hidden sm:inline">Refresh</span>
            </button>
          )}

          {/* Dev Indicator */}
          {process.env.NODE_ENV === "development" && (
            <div className="flex h-7 items-center gap-1 rounded-md bg-yellow-500/10 px-2 text-[10px] font-medium text-yellow-500 border border-yellow-500/20">
              <Code2 className="h-3 w-3" />
              <span>DEV</span>
            </div>
          )}

          {/* Notification Bell */}
          <button
            className="relative flex h-9 w-9 items-center justify-center rounded-lg transition-colors hover:bg-accent"
            aria-label="Notifications"
          >
            <Bell className="h-5 w-5 text-muted-foreground" />
            {notificationCount > 0 && (
              <span className="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-destructive px-1 text-[10px] font-medium text-white">
                {notificationCount > 9 ? "9+" : notificationCount}
              </span>
            )}
          </button>

          {/* User Menu */}
          <button className="flex items-center gap-2 rounded-lg px-2 py-1.5 transition-colors hover:bg-accent">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-sm font-medium text-primary">
              {userName ? userName.charAt(0).toUpperCase() : "M"}
            </div>
            {userName && (
              <>
                <span className="text-sm font-medium text-foreground">{userName}</span>
                <ChevronDown className="h-4 w-4 text-muted-foreground" />
              </>
            )}
          </button>
        </div>
      </div>
    </header>
  );
}
