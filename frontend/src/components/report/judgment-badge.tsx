"use client";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

type Judgment = "excellent" | "good" | "warning" | "critical";

interface JudgmentBadgeProps {
  judgment: Judgment;
  showLabel?: boolean;
  size?: "sm" | "md" | "lg";
}

const judgmentConfig = {
  excellent: {
    label: "Ottimo",
    emoji: "🟢",
    bgColor: "bg-emerald-500/20",
    textColor: "text-emerald-400",
    borderColor: "border-emerald-500/30",
  },
  good: {
    label: "Bene",
    emoji: "🟢",
    bgColor: "bg-green-500/20",
    textColor: "text-green-400",
    borderColor: "border-green-500/30",
  },
  warning: {
    label: "Attenzione",
    emoji: "🟡",
    bgColor: "bg-yellow-500/20",
    textColor: "text-yellow-400",
    borderColor: "border-yellow-500/30",
  },
  critical: {
    label: "Critico",
    emoji: "🔴",
    bgColor: "bg-red-500/20",
    textColor: "text-red-400",
    borderColor: "border-red-500/30",
  },
};

const sizeClasses = {
  sm: "text-xs px-1.5 py-0.5",
  md: "text-sm px-2 py-1",
  lg: "text-base px-3 py-1.5",
};

export function JudgmentBadge({ judgment, showLabel = true, size = "sm" }: JudgmentBadgeProps) {
  const config = judgmentConfig[judgment];

  return (
    <Badge
      variant="outline"
      className={cn(
        config.bgColor,
        config.textColor,
        config.borderColor,
        sizeClasses[size],
        "font-medium"
      )}
    >
      <span className="mr-1">{config.emoji}</span>
      {showLabel && config.label}
    </Badge>
  );
}

export function JudgmentDot({ judgment }: { judgment: Judgment }) {
  const config = judgmentConfig[judgment];
  return <span title={config.label}>{config.emoji}</span>;
}
