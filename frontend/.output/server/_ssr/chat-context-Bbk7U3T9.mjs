import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { o as require_jsx_runtime } from "../_libs/@radix-ui/react-arrow+[...].mjs";
import { r as api, t as ApiError } from "./api-BvsAdfBD.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/chat-context-Bbk7U3T9.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var ChatContext = (0, import_react.createContext)(null);
function ChatProvider({ children }) {
	const [messages, setMessages] = (0, import_react.useState)(() => {
		if (typeof window === "undefined") return [];
		try {
			const saved = sessionStorage.getItem("copilot_messages");
			if (saved) return JSON.parse(saved);
		} catch (e) {
			console.error("Failed to load chat history", e);
		}
		return [];
	});
	const [input, setInput] = (0, import_react.useState)("");
	const [loading, setLoading] = (0, import_react.useState)(false);
	(0, import_react.useEffect)(() => {
		if (typeof window !== "undefined") sessionStorage.setItem("copilot_messages", JSON.stringify(messages));
	}, [messages]);
	const clearChat = () => {
		setMessages([]);
		setInput("");
		if (typeof window !== "undefined") sessionStorage.removeItem("copilot_messages");
	};
	async function send(text) {
		const trimmed = text.trim();
		if (!trimmed || loading) return;
		setMessages((m) => [...m, {
			role: "user",
			content: trimmed
		}]);
		setInput("");
		setLoading(true);
		try {
			const res = await api.chat(trimmed);
			const reply = res.reply ?? res.response ?? res.message ?? (typeof res === "string" ? res : JSON.stringify(res));
			setMessages((m) => [...m, {
				role: "assistant",
				content: String(reply)
			}]);
		} catch (e) {
			const msg = e instanceof ApiError ? e.message : "Request failed";
			setMessages((m) => [...m, {
				role: "assistant",
				content: `Sorry, something went wrong: ${msg}`,
				error: true
			}]);
		} finally {
			setLoading(false);
		}
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChatContext.Provider, {
		value: {
			messages,
			input,
			loading,
			setInput,
			send,
			clearChat
		},
		children
	});
}
function useChat() {
	const context = (0, import_react.useContext)(ChatContext);
	if (!context) throw new Error("useChat must be used within a ChatProvider");
	return context;
}
//#endregion
export { useChat as n, ChatProvider as t };
