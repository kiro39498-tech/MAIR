import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { api, ApiError } from "@/lib/api";

type Msg = { role: "user" | "assistant"; content: string; error?: boolean };

type ChatContextType = {
  messages: Msg[];
  input: string;
  loading: boolean;
  setInput: (val: string) => void;
  send: (text: string) => Promise<void>;
  clearChat: () => void;
};

const ChatContext = createContext<ChatContextType | null>(null);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [messages, setMessages] = useState<Msg[]>(() => {
    if (typeof window === "undefined") return [];
    try {
      const saved = sessionStorage.getItem("copilot_messages");
      if (saved) return JSON.parse(saved);
    } catch (e) {
      console.error("Failed to load chat history", e);
    }
    return [];
  });
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      sessionStorage.setItem("copilot_messages", JSON.stringify(messages));
    }
  }, [messages]);

  const clearChat = () => {
    setMessages([]);
    setInput("");
    if (typeof window !== "undefined") {
      sessionStorage.removeItem("copilot_messages");
    }
  };

  async function send(text: string) {
    const trimmed = text.trim();
    if (!trimmed || loading) return;
    setMessages((m) => [...m, { role: "user", content: trimmed }]);
    setInput("");
    setLoading(true);
    try {
      const res = await api.chat(trimmed);
      const reply =
        res.reply ??
        res.response ??
        res.message ??
        (typeof res === "string" ? (res as string) : JSON.stringify(res));
      setMessages((m) => [...m, { role: "assistant", content: String(reply) }]);
    } catch (e) {
      const msg = e instanceof ApiError ? e.message : "Request failed";
      setMessages((m) => [
        ...m,
        { role: "assistant", content: `Sorry, something went wrong: ${msg}`, error: true },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <ChatContext.Provider value={{ messages, input, loading, setInput, send, clearChat }}>
      {children}
    </ChatContext.Provider>
  );
}

export function useChat() {
  const context = useContext(ChatContext);
  if (!context) throw new Error("useChat must be used within a ChatProvider");
  return context;
}
