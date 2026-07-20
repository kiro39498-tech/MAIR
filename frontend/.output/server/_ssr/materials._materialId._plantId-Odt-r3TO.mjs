import { o as require_jsx_runtime } from "../_libs/@radix-ui/react-arrow+[...].mjs";
import { i as cn, n as Button, r as api } from "./api-BvsAdfBD.mjs";
import { i as CardTitle, n as CardContent, r as CardHeader, t as Card } from "./card-DNn1texp.mjs";
import { L as ArrowLeft, N as Calendar, R as Activity, _ as Package, a as TrendingDown, d as ShoppingCart, f as Shield, p as ShieldAlert, r as Upload, u as Sparkles, x as Lock } from "../_libs/lucide-react.mjs";
import { _ as useParams, g as Link } from "../_libs/@tanstack/react-router+[...].mjs";
import { t as Skeleton } from "./skeleton-coEUFSch.mjs";
import { i as DropdownMenuTrigger, n as DropdownMenuContent, r as DropdownMenuItem, t as DropdownMenu } from "./dropdown-menu-nNcayZpm.mjs";
import { n as useQuery } from "../_libs/tanstack__react-query.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/materials._materialId._plantId-Odt-r3TO.js
var import_jsx_runtime = require_jsx_runtime();
function MaterialDetailPage() {
	const { materialId, plantId } = useParams({ from: "/materials/$materialId/$plantId" });
	const q = useQuery({
		queryKey: [
			"material",
			materialId,
			plantId
		],
		queryFn: () => api.material(materialId, plantId)
	});
	const handleExport = (format) => {
		if (!q.data) return;
		let content = "";
		let type = "";
		let ext = "";
		if (format === "json") {
			content = JSON.stringify(q.data, null, 2);
			type = "application/json";
			ext = "json";
		} else {
			const headers = Object.keys(q.data);
			const csvRow = headers.map((h) => {
				const val = q.data[h];
				if (typeof val === "object" && val !== null) return `"${JSON.stringify(val).replace(/"/g, "\"\"")}"`;
				return typeof val === "string" ? `"${val.replace(/"/g, "\"\"")}"` : val;
			}).join(",");
			content = [headers.join(","), csvRow].join("\n");
			type = "text/csv";
			ext = "csv";
		}
		const blob = new Blob([content], { type });
		const url = URL.createObjectURL(blob);
		const a = document.createElement("a");
		a.href = url;
		a.download = `material_${materialId}_${plantId}_export.${ext}`;
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);
		URL.revokeObjectURL(url);
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "space-y-8 max-w-7xl mx-auto",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex flex-col md:flex-row md:items-center justify-between gap-4",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-start gap-4",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
					asChild: true,
					variant: "outline",
					size: "icon",
					className: "h-8 w-8 mt-1 rounded-lg shrink-0 shadow-sm border-border/50",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
						to: "/",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowLeft, { className: "h-4 w-4" })
					})
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex items-center gap-3",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("h2", {
						className: "text-2xl font-bold tracking-tight text-foreground",
						children: [
							materialId,
							" ",
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "text-muted-foreground font-normal mx-1",
								children: "·"
							}),
							" ",
							plantId
						]
					}), q.data?.status !== "Healthy" && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "bg-primary/10 text-primary text-[11px] font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider",
						children: "Critical Material"
					})]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "text-sm text-muted-foreground mt-1",
					children: "Material Details & Status"
				})] })]
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-center gap-3",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DropdownMenu, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DropdownMenuTrigger, {
					asChild: true,
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
						variant: "outline",
						className: "gap-2 bg-white shadow-sm border-border/50 rounded-lg",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Upload, { className: "h-4 w-4" }), " Export"]
					})
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DropdownMenuContent, {
					align: "end",
					className: "w-48 bg-white",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DropdownMenuItem, {
						className: "cursor-pointer font-medium",
						onClick: () => handleExport("csv"),
						children: "Export as CSV / Excel"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(DropdownMenuItem, {
						className: "cursor-pointer font-medium",
						onClick: () => handleExport("json"),
						children: "Export as JSON"
					})]
				})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
					asChild: true,
					className: "gap-2 bg-primary text-primary-foreground shadow-sm rounded-lg hover:bg-primary/90",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("a", {
						href: `/recommendations?materialId=${materialId}&plantId=${plantId}`,
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Sparkles, { className: "h-4 w-4" }), " View Recommendations"]
					})
				})]
			})]
		}), q.isLoading ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "grid gap-4 md:grid-cols-2 lg:grid-cols-3",
			children: Array.from({ length: 6 }).map((_, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-32 rounded-2xl" }, i))
		}) : q.error ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Card, {
			className: "rounded-2xl border-border/50",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardContent, {
				className: "p-8 text-center text-sm text-muted-foreground",
				children: ["Could not load material detail. ", q.error.message]
			})
		}) : q.data ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "space-y-6",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "grid gap-4 md:grid-cols-2 lg:grid-cols-3",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(KpiCard, {
						title: "Health Status",
						icon: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ShieldAlert, { className: "h-5 w-5" }),
						iconBg: "bg-orange-100 text-orange-600",
						value: q.data.status ?? "Unknown",
						valueClass: q.data.status === "Healthy" ? "text-emerald-600" : q.data.status?.includes("Shortage") ? "text-red-600" : "text-orange-600"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(KpiCard, {
						title: "Usable Inventory",
						icon: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Lock, { className: "h-5 w-5" }),
						iconBg: "bg-emerald-100 text-emerald-600",
						value: q.data.usable_inventory,
						unit: "Units"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(KpiCard, {
						title: "Safety Stock",
						icon: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Shield, { className: "h-5 w-5" }),
						iconBg: "bg-blue-100 text-blue-600",
						value: q.data.safety_stock,
						unit: "Units"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(KpiCard, {
						title: "Reorder Point",
						icon: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ShoppingCart, { className: "h-5 w-5" }),
						iconBg: "bg-purple-100 text-purple-600",
						value: q.data.reorder_point,
						unit: "Units"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(KpiCard, {
						title: "Projected Shortage Date",
						icon: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Calendar, { className: "h-5 w-5" }),
						iconBg: "bg-rose-100 text-rose-600",
						value: q.data.projected_shortage_date ?? "—"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(KpiCard, {
						title: "Projected Shortage Qty",
						icon: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TrendingDown, { className: "h-5 w-5" }),
						iconBg: "bg-red-100 text-red-600",
						value: q.data.projected_shortage_qty ?? "—",
						unit: q.data.projected_shortage_qty ? "Units" : void 0
					})
				]
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "grid gap-6 lg:grid-cols-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DataCard, {
					title: "Production Impact",
					icon: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Activity, { className: "h-5 w-5 text-muted-foreground" }),
					data: q.data.production_impact
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(DataCard, {
					title: "PO Coverage",
					icon: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Package, { className: "h-5 w-5 text-muted-foreground" }),
					data: q.data.po_coverage
				})]
			})]
		}) : null]
	});
}
function KpiCard({ title, icon, iconBg, value, valueClass, unit }) {
	const display = value === null || value === void 0 || value === "" ? "—" : typeof value === "number" ? value.toLocaleString() : String(value);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
		className: "rounded-2xl border-border/50 shadow-sm bg-white overflow-hidden flex flex-col justify-between p-6",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex items-center gap-3",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: cn("flex h-10 w-10 shrink-0 items-center justify-center rounded-full", iconBg),
				children: icon
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "text-[13px] font-semibold text-muted-foreground uppercase tracking-wider",
				children: title
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "mt-6 flex items-baseline gap-2",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: cn("text-3xl font-bold tracking-tight", valueClass || "text-foreground"),
				children: display
			}), unit && display !== "—" && /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "text-sm font-medium text-muted-foreground",
				children: unit
			})]
		})]
	});
}
function DataCard({ title, icon, data }) {
	if (!data) return null;
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
		className: "rounded-2xl border-border/50 shadow-sm bg-white overflow-hidden flex flex-col",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardHeader, {
			className: "bg-muted/10 border-b border-border/50 p-4 flex flex-row items-center gap-3",
			children: [icon, /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardTitle, {
				className: "text-base font-bold text-foreground m-0",
				children: title
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardContent, {
			className: "p-0",
			children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "divide-y divide-border/50",
				children: Object.entries(data).map(([key, val]) => {
					if (key === "material_id" || key === "plant_id") return null;
					const displayKey = key.split("_").map((word) => word.charAt(0).toUpperCase() + word.slice(1)).join(" ");
					let displayVal = "—";
					if (val !== null && val !== void 0) if (typeof val === "boolean") displayVal = val ? "Yes" : "No";
					else if (Array.isArray(val)) displayVal = val.length === 0 ? "None" : val.join(", ");
					else displayVal = String(val);
					return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex items-center justify-between p-4 hover:bg-muted/30 transition-colors",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "text-sm font-medium text-muted-foreground",
							children: displayKey
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "text-sm font-semibold text-foreground text-right",
							children: displayVal
						})]
					}, key);
				})
			})
		})]
	});
}
//#endregion
export { MaterialDetailPage as component };
