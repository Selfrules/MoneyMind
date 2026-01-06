"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Calculator,
  PlusCircle,
  ArrowRight,
  Calendar,
  Clock,
  Sparkles,
  Loader2,
} from "lucide-react";
import type { FIREExtraSavingsResponse } from "@/lib/api";

interface ExtraSavingsSimulatorProps {
  onSimulate: (amount: number) => void;
  result?: FIREExtraSavingsResponse;
  isSimulating?: boolean;
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("it-IT", {
    style: "currency",
    currency: "EUR",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString("it-IT", { month: "short", year: "numeric" });
}

const QUICK_AMOUNTS = [50, 100, 200, 500];

export function ExtraSavingsSimulator({
  onSimulate,
  result,
  isSimulating,
}: ExtraSavingsSimulatorProps) {
  const [customAmount, setCustomAmount] = useState<string>("");

  const handleSimulate = (amount: number) => {
    if (amount > 0) {
      onSimulate(amount);
    }
  };

  const handleCustomSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const amount = parseFloat(customAmount);
    if (!isNaN(amount) && amount > 0) {
      handleSimulate(amount);
    }
  };

  return (
    <Card>
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Calculator className="h-5 w-5 text-primary" />
          Simula Extra Risparmio
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Quanto tempo risparmi aggiungendo extra ogni mese?
        </p>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Quick Amount Buttons */}
        <div className="grid grid-cols-4 gap-2">
          {QUICK_AMOUNTS.map((amount) => (
            <Button
              key={amount}
              variant="outline"
              size="sm"
              onClick={() => handleSimulate(amount)}
              disabled={isSimulating}
              className="text-sm"
            >
              +{formatCurrency(amount)}
            </Button>
          ))}
        </div>

        {/* Custom Amount Input */}
        <form onSubmit={handleCustomSubmit} className="flex gap-2">
          <div className="relative flex-1">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground text-sm">
              +
            </span>
            <Input
              type="number"
              placeholder="Importo personalizzato"
              value={customAmount}
              onChange={(e) => setCustomAmount(e.target.value)}
              className="pl-7"
              min="1"
              step="10"
            />
          </div>
          <Button type="submit" disabled={isSimulating || !customAmount}>
            {isSimulating ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              "Simula"
            )}
          </Button>
        </form>

        {/* Results */}
        {result && (
          <div className="mt-4 pt-4 border-t border-border space-y-4">
            {/* Before vs After */}
            <div className="grid grid-cols-[1fr,auto,1fr] gap-2 items-center">
              <div className="rounded-lg bg-muted/50 p-3 text-center">
                <div className="text-xs text-muted-foreground mb-1">Ora</div>
                <div className="text-lg font-bold">
                  {result.current.years_to_fire.toFixed(1)} anni
                </div>
                <div className="text-xs text-muted-foreground">
                  {formatCurrency(result.current.monthly_savings)}/mese
                </div>
              </div>

              <ArrowRight className="h-5 w-5 text-muted-foreground" />

              <div className="rounded-lg bg-emerald-500/10 border border-emerald-500/20 p-3 text-center">
                <div className="text-xs text-emerald-400 mb-1">Con Extra</div>
                <div className="text-lg font-bold text-emerald-400">
                  {result.with_extra.years_to_fire.toFixed(1)} anni
                </div>
                <div className="text-xs text-muted-foreground">
                  {formatCurrency(result.with_extra.monthly_savings)}/mese
                </div>
              </div>
            </div>

            {/* Impact Summary */}
            <div className="rounded-lg bg-gradient-to-r from-orange-500/10 to-red-500/10 border border-orange-500/20 p-4">
              <div className="flex items-center justify-between mb-3">
                <span className="font-medium text-foreground">
                  Impatto sul tuo percorso FI
                </span>
                <Badge className="bg-orange-500/20 text-orange-400 border-orange-500/30">
                  +{formatCurrency(result.with_extra.extra_amount)}/mese
                </Badge>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-full bg-emerald-500/20">
                    <Clock className="h-4 w-4 text-emerald-400" />
                  </div>
                  <div>
                    <div className="font-bold text-emerald-400">
                      -{result.impact.time_saved_description}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Tempo risparmiato
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-full bg-blue-500/20">
                    <Calendar className="h-4 w-4 text-blue-400" />
                  </div>
                  <div>
                    <div className="font-medium text-foreground">
                      {formatDate(result.with_extra.fire_date)}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Nuova data FI
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Motivational Message */}
            {result.impact.years_saved > 0 && (
              <div className="flex items-start gap-2 text-sm text-muted-foreground bg-muted/30 rounded-lg p-3">
                <Sparkles className="h-4 w-4 text-yellow-400 mt-0.5 flex-shrink-0" />
                <span>
                  Con solo{" "}
                  <strong className="text-foreground">
                    {formatCurrency(result.with_extra.extra_amount)}
                  </strong>{" "}
                  in più al mese, raggiungi la libertà finanziaria{" "}
                  <strong className="text-emerald-400">
                    {result.impact.years_saved.toFixed(1)} anni prima
                  </strong>
                  ! Pensa a cosa potresti tagliare o guadagnare.
                </span>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
