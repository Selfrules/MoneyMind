"use client";

import { useEffect, useRef } from "react";
import type { ChatMessage } from "@/lib/api-types";
import { Bot, User } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatMessagesProps {
  messages: ChatMessage[];
  streamingContent?: string;
  isStreaming?: boolean;
}

function MessageBubble({
  message,
  isStreaming = false,
}: {
  message: ChatMessage;
  isStreaming?: boolean;
}) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex gap-3 mb-4",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0",
          isUser ? "bg-primary" : "bg-muted"
        )}
      >
        {isUser ? (
          <User className="w-4 h-4 text-primary-foreground" />
        ) : (
          <Bot className="w-4 h-4 text-muted-foreground" />
        )}
      </div>

      {/* Message */}
      <div
        className={cn(
          "max-w-[80%] rounded-2xl px-4 py-2",
          isUser
            ? "bg-primary text-primary-foreground rounded-tr-none"
            : "bg-muted rounded-tl-none"
        )}
      >
        <p className="text-sm whitespace-pre-wrap break-words">
          {message.content}
          {isStreaming && (
            <span className="inline-block w-2 h-4 ml-1 bg-current animate-pulse" />
          )}
        </p>
      </div>
    </div>
  );
}

export function ChatMessages({
  messages,
  streamingContent,
  isStreaming,
}: ChatMessagesProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-4">
      {messages.length === 0 && !streamingContent && (
        <div className="text-center py-12">
          <Bot className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
          <h3 className="font-medium mb-2">Ciao! Sono il tuo Coach Finanziario</h3>
          <p className="text-sm text-muted-foreground">
            Chiedimi qualsiasi cosa sulle tue finanze.
          </p>
        </div>
      )}

      {messages.map((msg, index) => (
        <MessageBubble key={msg.id || index} message={msg} />
      ))}

      {/* Streaming message */}
      {streamingContent && (
        <MessageBubble
          message={{
            id: null,
            role: "assistant",
            content: streamingContent,
            tokens_used: null,
            created_at: null,
          }}
          isStreaming={isStreaming}
        />
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}
