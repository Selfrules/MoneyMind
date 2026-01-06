"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Search,
  Wrench,
  Shield,
  TrendingUp,
  CheckCircle,
  Circle,
  ChevronRight,
} from "lucide-react";

interface Phase {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  status: "completed" | "current" | "upcoming";
  progress: number;
  milestones: string[];
}

interface JourneyMapProps {
  currentPhase: string;
  phaseProgress: number;
  overallProgress?: number;
  projectedDebtFreeDate?: string;
  completedMilestones?: string[];
  isLoading?: boolean;
}

const PHASES: Phase[] = [
  {
    id: "diagnosi",
    name: "Diagnosi",
    description: "Capire la situazione attuale",
    icon: <Search className="h-5 w-5" />,
    status: "upcoming",
    progress: 0,
    milestones: [
      "Importare transazioni",
      "Categorizzare spese",
      "Calcolare baseline",
      "Identificare pattern",
    ],
  },
  {
    id: "ottimizzazione",
    name: "Ottimizzazione",
    description: "Ridurre sprechi e ottimizzare",
    icon: <Wrench className="h-5 w-5" />,
    status: "upcoming",
    progress: 0,
    milestones: [
      "Analizzare abbonamenti",
      "Tagliare spese inutili",
      "Rinegoziare contratti",
      "Automatizzare risparmi",
    ],
  },
  {
    id: "sicurezza",
    name: "Sicurezza",
    description: "Costruire protezione finanziaria",
    icon: <Shield className="h-5 w-5" />,
    status: "upcoming",
    progress: 0,
    milestones: [
      "Fondo emergenza 1 mese",
      "Fondo emergenza 3 mesi",
      "Fondo emergenza 6 mesi",
      "Debiti azzerati",
    ],
  },
  {
    id: "crescita",
    name: "Crescita",
    description: "Investire per il futuro",
    icon: <TrendingUp className="h-5 w-5" />,
    status: "upcoming",
    progress: 0,
    milestones: [
      "Primo investimento",
      "Portfolio diversificato",
      "Coast FI raggiunto",
      "Libertà finanziaria",
    ],
  },
];

function getPhaseStatus(
  phaseId: string,
  currentPhase: string
): "completed" | "current" | "upcoming" {
  const phaseOrder = ["diagnosi", "ottimizzazione", "sicurezza", "crescita"];
  const currentIdx = phaseOrder.indexOf(currentPhase.toLowerCase());
  const phaseIdx = phaseOrder.indexOf(phaseId);

  if (phaseIdx < currentIdx) return "completed";
  if (phaseIdx === currentIdx) return "current";
  return "upcoming";
}

function getPhaseColor(status: "completed" | "current" | "upcoming"): string {
  switch (status) {
    case "completed":
      return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
    case "current":
      return "bg-primary/20 text-primary border-primary/30";
    case "upcoming":
      return "bg-muted text-muted-foreground border-border";
  }
}

function PhaseCard({
  phase,
  currentPhase,
  phaseProgress,
  isLast,
}: {
  phase: Phase;
  currentPhase: string;
  phaseProgress: number;
  isLast: boolean;
}) {
  const status = getPhaseStatus(phase.id, currentPhase);
  const isCurrent = status === "current";
  const isCompleted = status === "completed";
  const progress = isCurrent ? phaseProgress : isCompleted ? 100 : 0;

  return (
    <div className="relative flex items-start gap-4">
      {/* Phase Icon */}
      <div className="relative">
        <div
          className={`flex h-12 w-12 items-center justify-center rounded-full border-2 transition-colors ${getPhaseColor(status)}`}
        >
          {isCompleted ? (
            <CheckCircle className="h-6 w-6 text-emerald-400" />
          ) : (
            phase.icon
          )}
        </div>
        {/* Connector line */}
        {!isLast && (
          <div className="absolute left-1/2 top-12 h-16 w-0.5 -translate-x-1/2 bg-border">
            {(isCurrent || isCompleted) && (
              <div
                className="w-full bg-primary transition-all"
                style={{ height: isCompleted ? "100%" : `${progress}%` }}
              />
            )}
          </div>
        )}
      </div>

      {/* Phase Content */}
      <div className="flex-1 pb-12">
        <div className="flex items-center gap-2">
          <h3
            className={`font-semibold ${
              isCurrent
                ? "text-foreground"
                : isCompleted
                  ? "text-emerald-400"
                  : "text-muted-foreground"
            }`}
          >
            {phase.name}
          </h3>
          {isCurrent && (
            <Badge variant="outline" className="bg-primary/10 text-primary border-primary/30">
              Attuale
            </Badge>
          )}
          {isCompleted && (
            <Badge variant="outline" className="bg-emerald-500/10 text-emerald-400 border-emerald-500/30">
              Completata
            </Badge>
          )}
        </div>
        <p className="text-sm text-muted-foreground mt-1">{phase.description}</p>

        {/* Progress bar for current phase */}
        {isCurrent && (
          <div className="mt-3">
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="text-muted-foreground">Progresso fase</span>
              <span className="text-foreground font-medium">{progress.toFixed(0)}%</span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>
        )}

        {/* Milestones */}
        {(isCurrent || isCompleted) && (
          <div className="mt-3 space-y-1.5">
            {phase.milestones.map((milestone, idx) => {
              const milestoneComplete =
                isCompleted || (isCurrent && (idx + 1) / phase.milestones.length <= progress / 100);

              return (
                <div
                  key={idx}
                  className={`flex items-center gap-2 text-xs ${
                    milestoneComplete ? "text-emerald-400" : "text-muted-foreground"
                  }`}
                >
                  {milestoneComplete ? (
                    <CheckCircle className="h-3.5 w-3.5" />
                  ) : (
                    <Circle className="h-3.5 w-3.5" />
                  )}
                  <span>{milestone}</span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

export function JourneyMap({
  currentPhase,
  phaseProgress,
  isLoading,
}: JourneyMapProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Il Tuo Percorso</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-8">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="flex items-start gap-4">
                <div className="h-12 w-12 rounded-full bg-muted animate-pulse" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 w-24 bg-muted animate-pulse rounded" />
                  <div className="h-3 w-48 bg-muted animate-pulse rounded" />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <ChevronRight className="h-5 w-5 text-primary" />
            Il Tuo Percorso Finanziario
          </CardTitle>
          <Badge variant="outline" className="bg-primary/10 text-primary">
            Fase {PHASES.findIndex((p) => p.id === currentPhase.toLowerCase()) + 1}/4
          </Badge>
        </div>
        <p className="text-sm text-muted-foreground">
          4 fasi verso la libertà finanziaria
        </p>
      </CardHeader>
      <CardContent>
        <div className="space-y-0">
          {PHASES.map((phase, idx) => (
            <PhaseCard
              key={phase.id}
              phase={phase}
              currentPhase={currentPhase}
              phaseProgress={phaseProgress}
              isLast={idx === PHASES.length - 1}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
