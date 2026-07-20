import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useRef, useState } from "react";
import { Loader2, Send, Sparkles, Bot, User, Trash2 } from "lucide-react";

import { api, ApiError } from "@/lib/api";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import { useChat } from "@/contexts/chat-context";

export const Route = createFileRoute("/copilot")({
  component: CopilotPage,
});

type Msg = { role: "user" | "assistant"; content: string; error?: boolean };

const EXAMPLES = [
  "What materials are currently in shortage?",
  "Which materials are at risk?",
  "Show me recommendations for replenishment",
];

function CopilotPage() {
  const { messages, input, setInput, loading, send, clearChat } = useChat();
  const scrollRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = (text: string) => {
    send(text).finally(() => {
      setTimeout(() => inputRef.current?.focus(), 0);
    });
  };

  return (
    <div className="mx-auto flex h-[calc(100dvh-7rem)] md:h-[calc(100dvh-9rem)] max-w-4xl flex-col gap-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-foreground">Copilot Chat</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Ask the planning agent about inventory, risks, and replenishment.
          </p>
        </div>
        {messages.length > 0 && (
          <Button 
            variant="outline" 
            size="sm" 
            onClick={clearChat} 
            className="gap-2 shrink-0 bg-white shadow-sm"
          >
            <Trash2 className="h-4 w-4" /> Clear Chat
          </Button>
        )}
      </div>

      <Card className="flex flex-1 flex-col overflow-hidden bg-white shadow-sm border border-border/50 rounded-2xl">
        <CardContent className="flex flex-1 flex-col gap-0 p-0 overflow-hidden">
          <div ref={scrollRef} className="flex-1 space-y-4 overflow-y-auto p-4">
            {messages.length === 0 && (
              <div className="flex h-full flex-col items-center justify-center gap-5 text-center animate-in fade-in zoom-in-95 duration-500">
                <div className="flex h-14 w-14 items-center justify-center rounded-full bg-primary/10 text-primary">
                  <Sparkles className="h-7 w-7" />
                </div>
                <div className="max-w-sm space-y-1">
                  <p className="text-lg font-bold tracking-tight text-foreground">How can I help?</p>
                  <p className="text-sm text-muted-foreground">
                    Try one of the example prompts below.
                  </p>
                </div>
                <div className="flex flex-wrap justify-center gap-3 mt-2">
                  {EXAMPLES.map((ex) => (
                    <button
                      key={ex}
                      onClick={() => handleSend(ex)}
                      className="rounded-full border border-border/60 bg-white px-5 py-2.5 text-sm font-medium text-muted-foreground shadow-sm transition-all hover:border-primary/40 hover:bg-primary/5 hover:text-primary active:scale-95"
                    >
                      {ex}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((m, i) => (
              <MessageBubble key={i} msg={m} />
            ))}

            {loading && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" /> Thinking...
              </div>
            )}
          </div>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend(input);
            }}
            className="p-4 bg-white"
          >
            <div className="flex items-end gap-2 rounded-xl border-2 border-primary/20 bg-white p-1 focus-within:border-primary/60 transition-all shadow-sm">
              <Textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSend(input);
                  }
                }}
                placeholder="Ask about materials, risks, or replenishment..."
                rows={1}
                className="min-h-[44px] max-h-40 flex-1 resize-none border-0 shadow-none focus-visible:ring-0 px-3 py-3"
              />
              <Button type="submit" disabled={loading || !input.trim()} size="icon" className="h-[44px] w-[44px] shrink-0 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90">
                {loading ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <Send className="h-5 w-5" />
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

function MessageBubble({ msg }: { msg: Msg }) {
  const isUser = msg.role === "user";
  return (
    <div className={cn("flex gap-3", isUser && "flex-row-reverse animate-in slide-in-from-right-2 fade-in duration-300", !isUser && "animate-in slide-in-from-left-2 fade-in duration-300")}>
      <div
        className={cn(
          "flex h-8 w-8 shrink-0 items-center justify-center rounded-full shadow-sm",
          isUser ? "bg-primary text-primary-foreground" : "bg-secondary text-secondary-foreground",
        )}
      >
        {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>
      <div
        className={cn(
          "max-w-[85%] whitespace-pre-wrap rounded-2xl px-5 py-3 text-sm leading-relaxed shadow-sm",
          isUser
            ? "bg-primary text-primary-foreground rounded-tr-sm"
            : msg.error
              ? "border border-destructive/20 bg-destructive/10 text-destructive rounded-tl-sm"
              : "bg-card border text-card-foreground rounded-tl-sm",
        )}
      >
        {msg.content}
      </div>
    </div>
  );
}