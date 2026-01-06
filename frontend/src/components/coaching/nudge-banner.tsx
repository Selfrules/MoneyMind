"use client";

import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  X,
  Bell,
  AlertTriangle,
  CheckCircle,
  Trophy,
  Sparkles,
  Lightbulb,
  ChevronRight,
  PartyPopper,
} from "lucide-react";

interface CoachingEvent {
  id: string;
  type: "nudge" | "celebration" | "alert" | "motivation" | "milestone" | "tip";
  priority: "low" | "medium" | "high" | "critical";
  title: string;
  message: string;
  icon: string;
  action_text?: string;
  action_url?: string;
  category?: string;
  is_dismissible: boolean;
}

interface NudgeBannerProps {
  events?: CoachingEvent[];
  onDismiss?: (eventId: string) => void;
  onAction?: (eventId: string) => void;
}

function getEventIcon(type: string, priority: string) {
  switch (type) {
    case "celebration":
    case "milestone":
      return <Trophy className="h-5 w-5" />;
    case "alert":
      return priority === "critical" ? (
        <AlertTriangle className="h-5 w-5" />
      ) : (
        <Bell className="h-5 w-5" />
      );
    case "motivation":
      return <Sparkles className="h-5 w-5" />;
    case "tip":
      return <Lightbulb className="h-5 w-5" />;
    default:
      return <Bell className="h-5 w-5" />;
  }
}

function getEventStyle(type: string, priority: string) {
  if (type === "celebration" || type === "milestone") {
    return {
      bg: "bg-emerald-500/10",
      border: "border-emerald-500/30",
      iconBg: "bg-emerald-500/20",
      iconText: "text-emerald-400",
      accent: "text-emerald-400",
    };
  }

  if (type === "motivation") {
    return {
      bg: "bg-purple-500/10",
      border: "border-purple-500/30",
      iconBg: "bg-purple-500/20",
      iconText: "text-purple-400",
      accent: "text-purple-400",
    };
  }

  if (type === "tip") {
    return {
      bg: "bg-blue-500/10",
      border: "border-blue-500/30",
      iconBg: "bg-blue-500/20",
      iconText: "text-blue-400",
      accent: "text-blue-400",
    };
  }

  // Nudges and alerts - color by priority
  switch (priority) {
    case "critical":
      return {
        bg: "bg-red-500/10",
        border: "border-red-500/30",
        iconBg: "bg-red-500/20",
        iconText: "text-red-400",
        accent: "text-red-400",
      };
    case "high":
      return {
        bg: "bg-orange-500/10",
        border: "border-orange-500/30",
        iconBg: "bg-orange-500/20",
        iconText: "text-orange-400",
        accent: "text-orange-400",
      };
    case "medium":
      return {
        bg: "bg-yellow-500/10",
        border: "border-yellow-500/30",
        iconBg: "bg-yellow-500/20",
        iconText: "text-yellow-400",
        accent: "text-yellow-400",
      };
    default:
      return {
        bg: "bg-muted/50",
        border: "border-border",
        iconBg: "bg-muted",
        iconText: "text-muted-foreground",
        accent: "text-muted-foreground",
      };
  }
}

interface SingleNudgeProps {
  event: CoachingEvent;
  onDismiss?: () => void;
  onAction?: () => void;
}

function SingleNudge({ event, onDismiss, onAction }: SingleNudgeProps) {
  const style = getEventStyle(event.type, event.priority);

  return (
    <div
      className={`rounded-lg ${style.bg} border ${style.border} p-4 transition-all hover:scale-[1.01]`}
    >
      <div className="flex items-start gap-3">
        {/* Icon */}
        <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${style.iconBg} ${style.iconText} shrink-0`}>
          {event.icon ? (
            <span className="text-xl">{event.icon}</span>
          ) : (
            getEventIcon(event.type, event.priority)
          )}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h4 className="text-sm font-medium text-foreground">{event.title}</h4>
            {event.priority === "critical" && (
              <Badge variant="outline" className="bg-red-500/20 text-red-400 border-red-500/30 text-xs">
                Urgente
              </Badge>
            )}
          </div>
          <p className="text-xs text-muted-foreground mt-1 whitespace-pre-wrap">
            {event.message}
          </p>

          {/* Action button */}
          {event.action_text && (
            <Button
              variant="ghost"
              size="sm"
              className={`mt-2 h-7 px-2 text-xs ${style.accent}`}
              onClick={onAction}
            >
              {event.action_text}
              <ChevronRight className="h-3.5 w-3.5 ml-0.5" />
            </Button>
          )}
        </div>

        {/* Dismiss button */}
        {event.is_dismissible && (
          <Button
            variant="ghost"
            size="icon"
            className="h-8 w-8 shrink-0 text-muted-foreground hover:text-foreground"
            onClick={onDismiss}
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>
    </div>
  );
}

interface CelebrationModalProps {
  event: CoachingEvent;
  onDismiss: () => void;
}

function CelebrationModal({ event, onDismiss }: CelebrationModalProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <Card className="w-full max-w-md mx-4 bg-card border-emerald-500/30">
        <CardContent className="pt-6 text-center">
          <div className="flex justify-center mb-4">
            <div className="relative">
              <div className="h-20 w-20 rounded-full bg-emerald-500/20 flex items-center justify-center">
                <PartyPopper className="h-10 w-10 text-emerald-400" />
              </div>
              {/* Confetti effect */}
              <span className="absolute -top-2 -left-2 text-2xl animate-bounce">🎉</span>
              <span className="absolute -top-2 -right-2 text-2xl animate-bounce delay-75">🎊</span>
              <span className="absolute -bottom-2 left-1/2 -translate-x-1/2 text-2xl animate-bounce delay-150">⭐</span>
            </div>
          </div>

          <h2 className="text-xl font-bold text-foreground mb-2">{event.title}</h2>
          <p className="text-muted-foreground mb-6 whitespace-pre-wrap">{event.message}</p>

          <Button className="w-full" onClick={onDismiss}>
            <CheckCircle className="h-4 w-4 mr-2" />
            Fantastico!
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

export function NudgeBanner({ events = [], onDismiss, onAction }: NudgeBannerProps) {
  const [dismissedIds, setDismissedIds] = useState<Set<string>>(new Set());
  const [celebrationEvent, setCelebrationEvent] = useState<CoachingEvent | null>(null);

  // Filter out dismissed events
  const activeEvents = events.filter((e) => !dismissedIds.has(e.id));

  // Check for celebrations to show as modal
  const celebrations = activeEvents.filter(
    (e) => e.type === "celebration" || e.type === "milestone"
  );
  const regularEvents = activeEvents.filter(
    (e) => e.type !== "celebration" && e.type !== "milestone"
  );

  // Show first celebration as modal if we haven't shown one yet
  if (celebrations.length > 0 && !celebrationEvent) {
    // Use setTimeout to avoid state update during render
    setTimeout(() => setCelebrationEvent(celebrations[0]), 0);
  }

  const handleDismiss = (eventId: string) => {
    setDismissedIds((prev) => new Set([...prev, eventId]));
    onDismiss?.(eventId);
  };

  const handleCelebrationDismiss = () => {
    if (celebrationEvent) {
      handleDismiss(celebrationEvent.id);
      setCelebrationEvent(null);
    }
  };

  if (activeEvents.length === 0) {
    return null;
  }

  return (
    <>
      {/* Celebration Modal */}
      {celebrationEvent && (
        <CelebrationModal event={celebrationEvent} onDismiss={handleCelebrationDismiss} />
      )}

      {/* Regular nudges */}
      {regularEvents.length > 0 && (
        <div className="space-y-3">
          {regularEvents.slice(0, 3).map((event) => (
            <SingleNudge
              key={event.id}
              event={event}
              onDismiss={() => handleDismiss(event.id)}
              onAction={() => onAction?.(event.id)}
            />
          ))}

          {regularEvents.length > 3 && (
            <p className="text-xs text-muted-foreground text-center">
              +{regularEvents.length - 3} altri avvisi
            </p>
          )}
        </div>
      )}
    </>
  );
}

// Export individual components for flexibility
export { SingleNudge, CelebrationModal };
