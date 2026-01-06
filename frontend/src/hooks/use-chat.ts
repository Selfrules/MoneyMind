"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, useCallback, useRef } from "react";
import { api } from "@/lib/api";
import type {
  ChatHistoryResponse,
  ChatMessage,
  ChatSSEEvent,
  SuggestedQuestionsResponse,
} from "@/lib/api-types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

/**
 * Hook to fetch chat history
 */
export function useChatHistory(sessionId?: string) {
  return useQuery<ChatHistoryResponse>({
    queryKey: ["chat-history", sessionId || "default"],
    queryFn: () =>
      api.get(
        `/api/chat/history${sessionId ? `?session_id=${sessionId}` : ""}`
      ),
    staleTime: 1000 * 60, // 1 minute
  });
}

/**
 * Hook to fetch suggested questions
 */
export function useSuggestedQuestions() {
  return useQuery<SuggestedQuestionsResponse>({
    queryKey: ["chat-suggestions"],
    queryFn: () => api.get("/api/chat/suggestions"),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Hook to clear chat session
 */
export function useClearChat() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (sessionId?: string) =>
      api.delete(
        `/api/chat/session${sessionId ? `?session_id=${sessionId}` : ""}`
      ),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["chat-history"] });
    },
  });
}

/**
 * Hook for streaming chat with SSE
 */
export function useStreamingChat() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const queryClient = useQueryClient();

  const sendMessage = useCallback(
    async (message: string, existingSessionId?: string) => {
      setIsStreaming(true);
      setStreamingContent("");
      setError(null);

      // Create abort controller
      abortControllerRef.current = new AbortController();

      try {
        const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message,
            session_id: existingSessionId || sessionId,
          }),
          signal: abortControllerRef.current.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body?.getReader();
        if (!reader) {
          throw new Error("No response body");
        }

        const decoder = new TextDecoder();
        let fullContent = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split("\n");

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const data: ChatSSEEvent = JSON.parse(line.slice(6));

                switch (data.type) {
                  case "session":
                    if (data.session_id) {
                      setSessionId(data.session_id);
                    }
                    break;
                  case "text":
                    if (data.content) {
                      fullContent += data.content;
                      setStreamingContent(fullContent);
                    }
                    break;
                  case "done":
                    // Invalidate chat history to refresh
                    queryClient.invalidateQueries({
                      queryKey: ["chat-history"],
                    });
                    break;
                  case "error":
                    setError(data.message || "Unknown error");
                    break;
                }
              } catch {
                // Ignore JSON parse errors
              }
            }
          }
        }

        return fullContent;
      } catch (err) {
        if (err instanceof Error && err.name !== "AbortError") {
          setError(err.message);
        }
        return null;
      } finally {
        setIsStreaming(false);
        abortControllerRef.current = null;
      }
    },
    [sessionId, queryClient]
  );

  const cancelStream = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsStreaming(false);
    }
  }, []);

  return {
    sendMessage,
    cancelStream,
    isStreaming,
    streamingContent,
    sessionId,
    error,
  };
}
