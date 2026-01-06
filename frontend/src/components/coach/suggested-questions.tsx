"use client";

import { Badge } from "@/components/ui/badge";
import type { SuggestedQuestion } from "@/lib/api-types";
import {
  HelpCircle,
  PiggyBank,
  CreditCard,
  TrendingUp,
  Wallet,
} from "lucide-react";

interface SuggestedQuestionsProps {
  questions: SuggestedQuestion[];
  onSelect: (question: string) => void;
}

function getCategoryIcon(category: string) {
  switch (category) {
    case "debt":
      return <CreditCard className="w-3 h-3" />;
    case "savings":
      return <PiggyBank className="w-3 h-3" />;
    case "spending":
      return <TrendingUp className="w-3 h-3" />;
    case "budget":
      return <Wallet className="w-3 h-3" />;
    default:
      return <HelpCircle className="w-3 h-3" />;
  }
}

export function SuggestedQuestions({
  questions,
  onSelect,
}: SuggestedQuestionsProps) {
  if (questions.length === 0) return null;

  return (
    <div className="px-4 py-3 border-t">
      <p className="text-xs text-muted-foreground mb-2">Domande suggerite:</p>
      <div className="flex flex-wrap gap-2">
        {questions.map((q, index) => (
          <Badge
            key={index}
            variant="outline"
            className="cursor-pointer hover:bg-muted transition-colors py-1.5 px-3"
            onClick={() => onSelect(q.text)}
          >
            {getCategoryIcon(q.category)}
            <span className="ml-1.5 text-xs">{q.text}</span>
          </Badge>
        ))}
      </div>
    </div>
  );
}
