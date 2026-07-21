import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { o as require_jsx_runtime } from "../_libs/@radix-ui/react-arrow+[...].mjs";
import { i as cn, n as Button } from "./api-CvgU3YZp.mjs";
import { n as useChat } from "./chat-context-DCdEs1cM.mjs";
import { n as CardContent, t as Card } from "./card-FWEPwnHu.mjs";
import { F as Bot, S as LoaderCircle, m as Send, n as User, o as Trash2, u as Sparkles } from "../_libs/lucide-react.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/copilot-CS7VDe26.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var Textarea = import_react.forwardRef(({ className, ...props }, ref) => {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("textarea", {
		className: cn("flex min-h-[60px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-base shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 md:text-sm", className),
		ref,
		...props
	});
});
Textarea.displayName = "Textarea";
var EXAMPLES = [
	"What materials are currently in shortage?",
	"Which materials are at risk?",
	"Show me recommendations for replenishment"
];
function CopilotPage() {
	const { messages, input, setInput, loading, send, clearChat } = useChat();
	const scrollRef = (0, import_react.useRef)(null);
	const inputRef = (0, import_react.useRef)(null);
	(0, import_react.useEffect)(() => {
		inputRef.current?.focus();
	}, []);
	(0, import_react.useEffect)(() => {
		scrollRef.current?.scrollTo({
			top: scrollRef.current.scrollHeight,
			behavior: "smooth"
		});
	}, [messages, loading]);
	const handleSend = (text) => {
		send(text).finally(() => {
			setTimeout(() => inputRef.current?.focus(), 0);
		});
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "mx-auto flex h-[calc(100dvh-7rem)] md:h-[calc(100dvh-9rem)] max-w-4xl flex-col gap-5",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex items-start justify-between gap-4",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "text-2xl font-bold tracking-tight text-foreground",
				children: "Copilot Chat"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "text-sm text-muted-foreground mt-1",
				children: "Ask the planning agent about inventory, risks, and replenishment."
			})] }), messages.length > 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
				variant: "outline",
				size: "sm",
				onClick: clearChat,
				className: "gap-2 shrink-0 bg-white shadow-sm",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Trash2, { className: "h-4 w-4" }), " Clear Chat"]
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Card, {
			className: "flex flex-1 flex-col overflow-hidden bg-white shadow-sm border border-border/50 rounded-2xl",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardContent, {
				className: "flex flex-1 flex-col gap-0 p-0 overflow-hidden",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					ref: scrollRef,
					className: "flex-1 space-y-4 overflow-y-auto p-4",
					children: [
						messages.length === 0 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex h-full flex-col items-center justify-center gap-5 text-center animate-in fade-in zoom-in-95 duration-500",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
									className: "flex h-14 w-14 items-center justify-center rounded-full bg-primary/10 text-primary",
									children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Sparkles, { className: "h-7 w-7" })
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "max-w-sm space-y-1",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
										className: "text-lg font-bold tracking-tight text-foreground",
										children: "How can I help?"
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
										className: "text-sm text-muted-foreground",
										children: "Try one of the example prompts below."
									})]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
									className: "flex flex-wrap justify-center gap-3 mt-2",
									children: EXAMPLES.map((ex) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
										onClick: () => handleSend(ex),
										className: "rounded-full border border-border/60 bg-white px-5 py-2.5 text-sm font-medium text-muted-foreground shadow-sm transition-all hover:border-primary/40 hover:bg-primary/5 hover:text-primary active:scale-95",
										children: ex
									}, ex))
								})
							]
						}),
						messages.map((m, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(MessageBubble, { msg: m }, i)),
						loading && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex items-center gap-2 text-sm text-muted-foreground",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, { className: "h-4 w-4 animate-spin" }), " Thinking..."]
						})
					]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("form", {
					onSubmit: (e) => {
						e.preventDefault();
						handleSend(input);
					},
					className: "p-4 bg-white",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex items-end gap-2 rounded-xl border-2 border-primary/20 bg-white p-1 focus-within:border-primary/60 transition-all shadow-sm",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Textarea, {
							ref: inputRef,
							value: input,
							onChange: (e) => setInput(e.target.value),
							onKeyDown: (e) => {
								if (e.key === "Enter" && !e.shiftKey) {
									e.preventDefault();
									handleSend(input);
								}
							},
							placeholder: "Ask about materials, risks, or replenishment...",
							rows: 1,
							className: "min-h-[44px] max-h-40 flex-1 resize-none border-0 shadow-none focus-visible:ring-0 px-3 py-3"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
							type: "submit",
							disabled: loading || !input.trim(),
							size: "icon",
							className: "h-[44px] w-[44px] shrink-0 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90",
							children: loading ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(LoaderCircle, { className: "h-5 w-5 animate-spin" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Send, { className: "h-5 w-5" })
						})]
					})
				})]
			})
		})]
	});
}
function MessageBubble({ msg }) {
	const isUser = msg.role === "user";
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: cn("flex gap-3", isUser && "flex-row-reverse animate-in slide-in-from-right-2 fade-in duration-300", !isUser && "animate-in slide-in-from-left-2 fade-in duration-300"),
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: cn("flex h-8 w-8 shrink-0 items-center justify-center rounded-full shadow-sm", isUser ? "bg-primary text-primary-foreground" : "bg-secondary text-secondary-foreground"),
			children: isUser ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(User, { className: "h-4 w-4" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Bot, { className: "h-4 w-4" })
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: cn("max-w-[85%] whitespace-pre-wrap rounded-2xl px-5 py-3 text-sm leading-relaxed shadow-sm", isUser ? "bg-primary text-primary-foreground rounded-tr-sm" : msg.error ? "border border-destructive/20 bg-destructive/10 text-destructive rounded-tl-sm" : "bg-card border text-card-foreground rounded-tl-sm"),
			children: msg.content
		})]
	});
}
//#endregion
export { CopilotPage as component };
