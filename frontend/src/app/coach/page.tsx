"use client";

import { useEffect, useState } from "react";
import { MessageCircle, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ChatMessages, ChatInput, SuggestedQuestions } from "@/components/coach";
import {
  useChatHistory,
  useSuggestedQuestions,
  useStreamingChat,
  useClearChat,
} from "@/hooks/use-chat";
import { Skeleton } from "@/components/ui/skeleton";
import type { ChatMessage } from "@/lib/api-types";

function LoadingState() {
  return (
    <div className="flex-1 p-4 space-y-4">
      <Skeleton className="h-16 w-3/4" />
      <Skeleton className="h-16 w-2/3 ml-auto" />
      <Skeleton className="h-16 w-3/4" />
    </div>
  );
}

export default function CoachPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(true);

  const { data: history, isLoading: historyLoading } = useChatHistory();
  const { data: suggestions } = useSuggestedQuestions();
  const { mutate: clearChat } = useClearChat();
  const {
    sendMessage,
    cancelStream,
    isStreaming,
    streamingContent,
    sessionId,
    error,
  } = useStreamingChat();

  // Load history
  useEffect(() => {
    if (history?.messages) {
      setMessages(history.messages);
      if (history.messages.length > 0) {
        setShowSuggestions(false);
      }
    }
  }, [history]);

  const handleSend = async (message: string) => {
    // Add user message optimistically
    const userMessage: ChatMessage = {
      id: null,
      role: "user",
      content: message,
      tokens_used: null,
      created_at: null,
    };
    setMessages((prev) => [...prev, userMessage]);
    setShowSuggestions(false);

    // Send and wait for response
    const response = await sendMessage(message, sessionId || undefined);

    // Add assistant response
    if (response) {
      setMessages((prev) => [
        ...prev,
        {
          id: null,
          role: "assistant",
          content: response,
          tokens_used: null,
          created_at: null,
        },
      ]);
    }
  };

  const handleClear = () => {
    clearChat(sessionId || undefined);
    setMessages([]);
    setShowSuggestions(true);
  };

  const handleSelectSuggestion = (question: string) => {
    handleSend(question);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-var(--header-height)-48px)]">
      {/* Page Header */}
      <div className="flex items-center justify-between pb-4 border-b">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <MessageCircle className="h-6 w-6 text-primary" />
            Coach
          </h1>
          <p className="text-muted-foreground text-sm">
            Il tuo consulente finanziario AI
          </p>
        </div>
        {messages.length > 0 && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleClear}
            className="text-muted-foreground"
          >
            <RotateCcw className="w-4 h-4 mr-1" />
            Nuova chat
          </Button>
        )}
      </div>

      {/* Messages */}
      {historyLoading ? (
        <LoadingState />
      ) : (
        <ChatMessages
          messages={messages}
          streamingContent={streamingContent}
          isStreaming={isStreaming}
        />
      )}

      {/* Error display */}
      {error && (
        <div className="px-4 py-2 bg-expense/10 text-expense text-sm">
          Errore: {error}
        </div>
      )}

      {/* Suggested Questions */}
      {showSuggestions && suggestions?.questions && !isStreaming && (
        <SuggestedQuestions
          questions={suggestions.questions}
          onSelect={handleSelectSuggestion}
        />
      )}

      {/* Input */}
      <ChatInput
        onSend={handleSend}
        onCancel={cancelStream}
        isStreaming={isStreaming}
        disabled={historyLoading}
      />
    </div>
  );
}
