import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { o as require_jsx_runtime } from "../_libs/@radix-ui/react-arrow+[...].mjs";
import { i as cn, n as Button, r as api } from "./api-CvgU3YZp.mjs";
import { i as CardTitle, n as CardContent, r as CardHeader, t as Card } from "./card-FWEPwnHu.mjs";
import { E as Download, c as SquareCheckBig, i as TriangleAlert, j as ChevronDown, p as ShieldAlert, s as Square, t as X, v as PackageX } from "../_libs/lucide-react.mjs";
import { t as Skeleton } from "./skeleton-CTfZ-LAW.mjs";
import { i as DropdownMenuTrigger, n as DropdownMenuContent, r as DropdownMenuItem, t as DropdownMenu } from "./dropdown-menu-BFkmOnnx.mjs";
import { i as useQueryClient, n as useQuery, t as useMutation } from "../_libs/tanstack__react-query.mjs";
import { t as Input } from "./input-UeNrrxUk.mjs";
import { t as Route } from "./recommendations-Dw8IuSG1.mjs";
import { a as TableHead, i as TableCell, n as Table, o as TableHeader, r as TableBody, s as TableRow, t as Badge } from "./badge-DmY8Zsjp.mjs";
import { n as toast } from "../_libs/sonner.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/recommendations-DiuP1BBy.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function PriorityText({ priority }) {
	const p = Number(priority);
	if (isNaN(p)) return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
		className: "text-xs font-semibold",
		children: priority
	});
	if (p === 1) return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
		className: "font-semibold text-red-500 bg-red-50 px-2 py-0.5 rounded text-xs",
		children: p
	});
	if (p >= .9) return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
		className: "font-semibold text-red-400 bg-red-50 px-2 py-0.5 rounded text-xs",
		children: p
	});
	if (p >= .8) return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
		className: "font-semibold text-orange-500 bg-orange-50 px-2 py-0.5 rounded text-xs",
		children: p
	});
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
		className: "font-semibold text-amber-500 bg-amber-50 px-2 py-0.5 rounded text-xs",
		children: p
	});
}
function StatusBadge({ status }) {
	if (status === "Recommended") return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
		variant: "outline",
		className: "text-gray-500",
		children: status
	});
	if (status === "Drafted") return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
		variant: "outline",
		className: "text-gray-500",
		children: status
	});
	if (status === "PendingApproval") return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
		variant: "outline",
		className: "text-amber-500 bg-amber-50",
		children: status
	});
	if (status === "Approved") return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
		variant: "outline",
		className: "text-blue-500 bg-blue-50",
		children: status
	});
	if (status === "Executed") return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
		variant: "outline",
		className: "text-emerald-500 bg-emerald-50",
		children: status
	});
	if (status === "Failed") return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
		variant: "outline",
		className: "text-red-500 bg-red-50",
		children: status
	});
	if (status === "Rejected") return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
		variant: "outline",
		className: "text-rose-500 bg-rose-50",
		children: status
	});
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
		variant: "outline",
		children: status
	});
}
function RecommendationsPage() {
	const queryClient = useQueryClient();
	const { materialId, plantId } = Route.useSearch();
	const q = useQuery({
		queryKey: ["recommendations"],
		queryFn: api.recommendations
	});
	const aq = useQuery({
		queryKey: ["actions"],
		queryFn: () => api.actions.list()
	});
	const [selected, setSelected] = (0, import_react.useState)(null);
	const [selectedPlant, setSelectedPlant] = (0, import_react.useState)("All Plants");
	const [currentPage, setCurrentPage] = (0, import_react.useState)(1);
	const [editQty, setEditQty] = (0, import_react.useState)("");
	const [dismissed, setDismissed] = (0, import_react.useState)(/* @__PURE__ */ new Set());
	const recommendations = q.data ?? [];
	const actions = aq.data ?? [];
	const actionMap = /* @__PURE__ */ new Map();
	actions.forEach((a) => actionMap.set(`${a.material_id}-${a.plant_id}`, a));
	const mergedRows = recommendations.filter((r) => !dismissed.has(`${r.material_id}-${r.plant_id}`)).map((r) => {
		const action = actionMap.get(`${r.material_id}-${r.plant_id}`);
		return {
			...r,
			suggested_qty: r.recommended_qty ?? 0,
			action_status: action ? action.status : "Recommended",
			action_id: action ? action.action_id : void 0,
			action
		};
	});
	actions.forEach((a) => {
		if (!recommendations.find((r) => r.material_id === a.material_id && r.plant_id === a.plant_id) && !dismissed.has(`${a.material_id}-${a.plant_id}`)) mergedRows.push({
			material_id: a.material_id,
			plant_id: a.plant_id,
			priority: "0",
			reason: "Existing action",
			recommended_action: "Replenish",
			suggested_qty: a.recommended_qty,
			action_status: a.status,
			action_id: a.action_id,
			action: a
		});
	});
	const uniquePlants = Array.from(new Set(mergedRows.map((r) => r.plant_id))).sort();
	const filteredRows = selectedPlant === "All Plants" ? mergedRows : mergedRows.filter((r) => r.plant_id === selectedPlant);
	const ITEMS_PER_PAGE = 8;
	const totalPages = Math.ceil(filteredRows.length / ITEMS_PER_PAGE);
	const paginatedRows = filteredRows.slice((currentPage - 1) * ITEMS_PER_PAGE, currentPage * ITEMS_PER_PAGE);
	const createMutation = useMutation({
		mutationFn: (qty) => api.actions.create(selected.material_id, selected.plant_id, qty),
		onSuccess: () => {
			toast.success("Draft approved and submitted to manager.");
			queryClient.invalidateQueries({ queryKey: ["actions"] });
		},
		onError: (err) => {
			toast.error(err instanceof Error ? err.message : "Failed to create action");
		}
	});
	(0, import_react.useEffect)(() => {
		if (materialId && plantId && mergedRows.length > 0 && !selected) {
			const match = mergedRows.find((r) => r.material_id === materialId && r.plant_id === plantId);
			if (match) {
				setSelected(match);
				setEditQty(String(match.suggested_qty ?? ""));
			}
		}
	}, [
		materialId,
		plantId,
		mergedRows,
		selected
	]);
	const handleExport = (format) => {
		if (!filteredRows.length) return;
		let content = "";
		let type = "";
		let ext = "";
		if (format === "json") {
			content = JSON.stringify(filteredRows, null, 2);
			type = "application/json";
			ext = "json";
		} else {
			const headers = Object.keys(filteredRows[0]).filter((k) => typeof filteredRows[0][k] !== "object");
			const csvRows = filteredRows.map((row) => headers.map((h) => {
				const val = row[h];
				return typeof val === "string" ? `"${val.replace(/"/g, "\"\"")}"` : val;
			}).join(","));
			content = [headers.join(","), ...csvRows].join("\n");
			type = "text/csv";
			ext = "csv";
		}
		const blob = new Blob([content], { type });
		const url = URL.createObjectURL(blob);
		const a = document.createElement("a");
		a.href = url;
		a.download = `recommendations_export.${ext}`;
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);
		URL.revokeObjectURL(url);
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "flex-1 space-y-4 p-4 md:p-8 pt-6",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "flex flex-col md:flex-row md:items-center md:justify-between gap-4",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "text-2xl font-bold tracking-tight text-foreground",
				children: "Recommendations"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "text-sm text-muted-foreground mt-1",
				children: "Draft replenishment actions generated by the planning agent."
			})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-center gap-3",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DropdownMenu, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DropdownMenuTrigger, {
					asChild: true,
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex items-center gap-2 rounded-lg border bg-white px-3 py-2 text-sm text-muted-foreground shadow-sm cursor-pointer hover:bg-muted/30",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: selectedPlant }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChevronDown, { className: "h-4 w-4" })]
					})
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DropdownMenuContent, {
					align: "end",
					className: "w-48 bg-white",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DropdownMenuItem, {
						className: "cursor-pointer",
						onClick: () => {
							setSelectedPlant("All Plants");
							setCurrentPage(1);
						},
						children: "All Plants"
					}), uniquePlants.map((p) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(DropdownMenuItem, {
						className: "cursor-pointer",
						onClick: () => {
							setSelectedPlant(p);
							setCurrentPage(1);
						},
						children: p
					}, p))]
				})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(DropdownMenu, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(DropdownMenuTrigger, {
					asChild: true,
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
						className: "gap-2 bg-primary text-primary-foreground shadow-sm rounded-lg hover:bg-primary/90",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Download, { className: "h-4 w-4" }), " Export"]
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
				})] })]
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: cn("grid gap-6", selected ? "lg:grid-cols-[1.5fr_1fr] xl:grid-cols-[2fr_1fr]" : "grid-cols-1"),
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
				className: "shadow-sm bg-white rounded-2xl border-border/50 flex flex-col",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardHeader, {
					className: "flex flex-row items-center justify-between pb-4 border-b border-border/50",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardTitle, {
						className: "text-base font-bold text-foreground",
						children: "Draft recommendations"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex flex-wrap items-center gap-2",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Badge, {
								variant: "outline",
								className: "bg-red-50 text-red-600 border-red-200 px-2 py-0.5 rounded-md text-xs",
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(PackageX, { className: "mr-1 h-3 w-3" }),
									" Shortage ",
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: "ml-1 font-bold",
										children: "23"
									})
								]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Badge, {
								variant: "outline",
								className: "bg-orange-50 text-orange-600 border-orange-200 px-2 py-0.5 rounded-md text-xs",
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ShieldAlert, { className: "mr-1 h-3 w-3" }),
									" Safety Stock ",
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: "ml-1 font-bold",
										children: "31"
									})
								]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Badge, {
								variant: "outline",
								className: "bg-amber-50 text-amber-600 border-amber-200 px-2 py-0.5 rounded-md text-xs",
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TriangleAlert, { className: "mr-1 h-3 w-3" }),
									" Near Reorder ",
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: "ml-1 font-bold",
										children: "59"
									})
								]
							})
						]
					})]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardContent, {
					className: "p-0",
					children: q.isLoading ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "space-y-2 p-4",
						children: Array.from({ length: 6 }).map((_, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-10 w-full" }, i))
					}) : q.error ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "p-8 text-center text-sm text-muted-foreground",
						children: "Could not load recommendations."
					}) : !filteredRows.length ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "p-8 text-center text-sm text-muted-foreground",
						children: "No recommendations matching this filter right now."
					}) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex flex-col flex-1",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Table, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHeader, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(TableRow, {
							className: "border-b-border/50 hover:bg-transparent",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
									className: "w-12 text-center",
									children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Square, { className: "h-4 w-4 text-muted-foreground/50 inline-block" })
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, { children: "Material" }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, { children: "Plant" }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, { children: "Status" }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, { children: "Priority" }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, { children: "Reason" }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
									className: "text-right",
									children: "Suggested Qty"
								})
							]
						}) }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableBody, { children: paginatedRows.map((r, i) => {
							const isSel = selected?.material_id === r.material_id && selected?.plant_id === r.plant_id;
							const displayQty = r.suggested_qty;
							return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(TableRow, {
								onClick: () => {
									setSelected(r);
									setEditQty(String(r.suggested_qty ?? ""));
								},
								className: cn("cursor-pointer border-b-border/30 transition-colors", isSel ? "bg-primary/5 border-primary/20" : "hover:bg-muted/30"),
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
										className: "text-center",
										children: isSel ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SquareCheckBig, { className: "h-4 w-4 text-primary inline-block" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Square, { className: "h-4 w-4 text-muted-foreground/30 inline-block" })
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
										className: "font-semibold text-foreground",
										children: r.material_id
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
										className: "text-muted-foreground",
										children: r.plant_id
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatusBadge, { status: r.action_status ?? "Recommended" }) }),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(PriorityText, { priority: String(r.priority) }) }),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
										className: "max-w-xs truncate text-muted-foreground",
										children: r.reason
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
										className: "text-right font-semibold text-foreground",
										children: displayQty
									})
								]
							}, `${r.material_id}-${r.plant_id}-${i}`);
						}) })] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "mt-auto flex items-center justify-between border-t border-border/50 p-4",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
								className: "text-xs text-muted-foreground font-medium",
								children: [
									"Showing ",
									filteredRows.length > 0 ? (currentPage - 1) * ITEMS_PER_PAGE + 1 : 0,
									"-",
									Math.min(currentPage * ITEMS_PER_PAGE, filteredRows.length),
									" of ",
									filteredRows.length,
									" recommendations"
								]
							}), totalPages > 1 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "flex items-center gap-1 text-xs text-muted-foreground",
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
										variant: "ghost",
										size: "icon",
										className: "h-7 w-7",
										onClick: () => setCurrentPage((p) => Math.max(1, p - 1)),
										disabled: currentPage === 1,
										children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChevronDown, { className: "h-3.5 w-3.5 rotate-90" })
									}),
									(() => {
										const pages = [];
										if (totalPages <= 6) for (let i = 1; i <= totalPages; i++) pages.push(i);
										else if (currentPage <= 3) pages.push(1, 2, 3, 4, 5, "...", totalPages);
										else if (currentPage >= totalPages - 2) pages.push(1, "...", totalPages - 4, totalPages - 3, totalPages - 2, totalPages - 1, totalPages);
										else pages.push(1, "...", currentPage - 1, currentPage, currentPage + 1, "...", totalPages);
										return pages.map((p, i) => p === "..." ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
											className: "px-1 tracking-widest",
											children: "..."
										}, `dots-${i}`) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
											variant: "ghost",
											size: "icon",
											className: cn("h-7 w-7 rounded-md font-medium", currentPage === p ? "bg-primary/10 text-primary font-bold hover:bg-primary/20" : "hover:bg-muted"),
											onClick: () => setCurrentPage(p),
											children: p
										}, `page-${p}`));
									})(),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
										variant: "ghost",
										size: "icon",
										className: "h-7 w-7",
										onClick: () => setCurrentPage((p) => Math.min(totalPages, p + 1)),
										disabled: currentPage === totalPages,
										children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChevronDown, { className: "h-3.5 w-3.5 -rotate-90" })
									})
								]
							})]
						})]
					})
				})]
			}), selected && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
				className: "shadow-sm bg-white rounded-2xl border-border/50 flex flex-col max-h-[800px] animate-in slide-in-from-right-4 fade-in duration-300",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardHeader, {
					className: "flex flex-row items-center justify-between border-b border-border/50 pb-4",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardTitle, {
						className: "text-base font-bold text-foreground",
						children: "Detail"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
						variant: "ghost",
						size: "icon",
						className: "h-8 w-8 text-muted-foreground hover:bg-muted",
						onClick: () => setSelected(null),
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(X, { className: "h-4 w-4" })
					})]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardContent, {
					className: "p-0 flex flex-col flex-1 min-h-0",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(import_jsx_runtime.Fragment, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "p-6 space-y-6 flex-1 overflow-y-auto",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: "text-xs text-muted-foreground mb-1",
								children: "Material"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: "text-xl font-bold text-foreground",
								children: selected.material_id
							})] }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
									className: "text-xs text-muted-foreground mb-1",
									children: "Plant"
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
									className: "text-base font-bold text-foreground",
									children: selected.plant_id
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
									className: "mt-2",
									children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
										className: "inline-flex items-center rounded-sm bg-red-50 px-2 py-0.5 text-xs font-semibold text-red-600 border border-red-200",
										children: [
											"Priority ",
											selected.priority,
											" - Critical"
										]
									})
								})
							] }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "space-y-4",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
									className: "text-xs text-muted-foreground mb-1",
									children: "Recommended action"
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
									className: "font-bold text-foreground",
									children: selected.recommended_action
								})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
									className: "text-xs text-muted-foreground mb-1",
									children: "Reason"
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
									className: "text-sm text-muted-foreground",
									children: selected.reason
								})] })]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "grid grid-cols-2 gap-4 pt-4 border-t border-border/50",
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
										className: "col-span-2",
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
											className: "text-[11px] text-muted-foreground uppercase tracking-wider font-semibold mb-1",
											children: "Suggested Qty"
										}), !selected.action_status || selected.action_status === "Recommended" || selected.action_status === "Drafted" ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
											className: "flex items-center gap-2",
											children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
												type: "number",
												value: editQty,
												onChange: (e) => setEditQty(e.target.value),
												className: "w-24 h-8 font-bold"
											}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
												className: "text-sm font-medium text-muted-foreground",
												children: "Units"
											})]
										}) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
											className: "font-bold text-foreground mt-1",
											children: [selected.suggested_qty, " Units"]
										})]
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
										className: "text-[11px] text-muted-foreground uppercase tracking-wider font-semibold",
										children: "Lead Time"
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
										className: "font-bold text-foreground mt-1",
										children: selected.lead_time_days !== void 0 && selected.lead_time_days !== null ? `${selected.lead_time_days} days` : "—"
									})] }),
									/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
										className: "text-[11px] text-muted-foreground uppercase tracking-wider font-semibold",
										children: "Preferred Supplier"
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
										className: "font-bold text-foreground mt-1",
										children: selected.suggested_supplier_id || "—"
									})] }),
									/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
										className: "text-[11px] text-muted-foreground uppercase tracking-wider font-semibold",
										children: "Est. Arrival"
									}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
										className: "font-bold text-foreground mt-1",
										children: selected.lead_time_days !== void 0 && selected.lead_time_days !== null ? (() => {
											const d = /* @__PURE__ */ new Date();
											d.setDate(d.getDate() + Number(selected.lead_time_days));
											return d.toLocaleDateString("en-GB", {
												day: "numeric",
												month: "short",
												year: "numeric"
											});
										})() : "—"
									})] })
								]
							})
						]
					}), !selected.action_status || selected.action_status === "Recommended" || selected.action_status === "Drafted" ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "p-4 border-t border-border/50 bg-muted/10 flex items-center gap-3",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
							className: "flex-1 bg-primary text-primary-foreground hover:bg-primary/90 rounded-lg shadow-sm font-semibold",
							onClick: () => createMutation.mutate(Number(editQty)),
							disabled: createMutation.isPending,
							children: createMutation.isPending ? "Submitting..." : "Submit for Approval"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
							variant: "outline",
							className: "flex-1 rounded-lg font-semibold bg-white",
							onClick: () => {
								setDismissed((prev) => new Set(prev).add(`${selected.material_id}-${selected.plant_id}`));
								setSelected(null);
								toast.info("Recommendation dismissed.");
							},
							children: "Reject"
						})]
					}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "p-4 border-t border-border/50 bg-muted/10 flex flex-col gap-2",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "text-sm text-center font-medium text-muted-foreground",
							children: [
								"This action is currently ",
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "font-bold text-foreground",
									children: selected.action_status
								}),
								"."
							]
						})
					})] })
				})]
			})]
		})]
	});
}
//#endregion
export { RecommendationsPage as component };
