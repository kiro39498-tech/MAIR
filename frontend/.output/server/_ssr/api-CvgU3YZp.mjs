import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { o as require_jsx_runtime } from "../_libs/@radix-ui/react-arrow+[...].mjs";
import { n as Slot } from "../_libs/@radix-ui/react-primitive+[...].mjs";
import { n as clsx, t as cva } from "../_libs/class-variance-authority+clsx.mjs";
import { t as twMerge } from "../_libs/tailwind-merge.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/api-CvgU3YZp.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function cn(...inputs) {
	return twMerge(clsx(inputs));
}
var buttonVariants = cva("inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium cursor-pointer transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 disabled:cursor-not-allowed [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0", {
	variants: {
		variant: {
			default: "bg-primary text-primary-foreground shadow hover:bg-primary/90",
			destructive: "bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90",
			outline: "border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground",
			secondary: "bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80",
			ghost: "hover:bg-accent hover:text-accent-foreground",
			link: "text-primary underline-offset-4 hover:underline"
		},
		size: {
			default: "h-9 px-4 py-2",
			sm: "h-8 rounded-md px-3 text-xs",
			lg: "h-10 rounded-md px-8",
			icon: "h-9 w-9"
		}
	},
	defaultVariants: {
		variant: "default",
		size: "default"
	}
});
var Button = import_react.forwardRef(({ className, variant, size, asChild = false, ...props }, ref) => {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(asChild ? Slot : "button", {
		className: cn(buttonVariants({
			variant,
			size,
			className
		})),
		ref,
		...props
	});
});
Button.displayName = "Button";
var BASE_URL = "http://127.0.0.1:8002".replace(/\/$/, "") ?? "";
var ApiError = class extends Error {
	status;
	constructor(message, status) {
		super(message);
		this.status = status;
	}
};
async function request(path, init) {
	const url = `${BASE_URL}${path}`;
	let res;
	try {
		res = await fetch(url, {
			...init,
			headers: {
				"Content-Type": "application/json",
				...init?.headers ?? {}
			}
		});
	} catch (e) {
		throw new ApiError(`Network error contacting ${url}`);
	}
	if (!res.ok) throw new ApiError(`Request failed (${res.status})`, res.status);
	return await res.json();
}
var api = {
	summary: () => request("/api/dashboard/summary"),
	productRisk: () => request("/api/dashboard/product-risk"),
	productBomRisk: (params) => {
		const q = new URLSearchParams();
		if (params?.plantId) q.set("plant_id", params.plantId);
		if (params?.healthStatus) q.set("health_status", params.healthStatus);
		const qs = q.toString();
		return request(`/api/dashboard/product-bom-risk${qs ? `?${qs}` : ""}`);
	},
	materialUsage: (materialId, plantId) => request(`/api/dashboard/material-usage/${encodeURIComponent(materialId)}${plantId ? `?plant_id=${encodeURIComponent(plantId)}` : ""}`),
	materials: (params) => {
		const q = new URLSearchParams();
		if (params?.status) q.set("status", params.status);
		if (params?.risky_only) q.set("risky_only", "true");
		const qs = q.toString();
		return request(`/api/dashboard/materials${qs ? `?${qs}` : ""}`);
	},
	material: (materialId, plantId) => request(`/api/dashboard/materials/${encodeURIComponent(materialId)}/${encodeURIComponent(plantId)}`),
	recommendations: () => request("/api/dashboard/recommendations"),
	chat: (message) => request("/api/copilot/chat", {
		method: "POST",
		body: JSON.stringify({ message })
	}),
	actions: {
		list: async (status) => {
			let url = `${BASE_URL}/api/replenishment/actions`;
			if (status) url += `?status=${encodeURIComponent(status)}`;
			const res = await fetch(url);
			if (!res.ok) throw new ApiError(`Failed to fetch actions`, res.status);
			return res.json();
		},
		create: async (materialId, plantId, suggestedQty) => {
			const res = await fetch(`${BASE_URL}/api/replenishment/actions/create`, {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					material_id: materialId,
					plant_id: plantId,
					suggested_qty_override: suggestedQty
				})
			});
			if (!res.ok) throw new ApiError(`Failed to create action`, res.status);
			return res.json();
		},
		runPipeline: () => request("/api/replenishment/run", { method: "POST" }),
		approve: async (actionId, token) => {
			const url = `${BASE_URL}/api/replenishment/actions/${encodeURIComponent(actionId)}/approve?token=${encodeURIComponent(token)}`;
			const res = await fetch(url);
			if (!res.ok) throw new ApiError(`Failed to approve`, res.status);
			return res.text();
		},
		reject: async (actionId, token) => {
			const url = `${BASE_URL}/api/replenishment/actions/${encodeURIComponent(actionId)}/reject?token=${encodeURIComponent(token)}`;
			const res = await fetch(url);
			if (!res.ok) throw new ApiError(`Failed to reject`, res.status);
			return res.text();
		},
		execute: (actionId) => request(`/api/replenishment/actions/${encodeURIComponent(actionId)}/execute`, { method: "POST" })
	}
};
//#endregion
export { cn as i, Button as n, api as r, ApiError as t };
