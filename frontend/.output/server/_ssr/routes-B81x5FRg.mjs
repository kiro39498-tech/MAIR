import { i as __toESM } from "../_runtime.mjs";
import { u as require_react } from "../_libs/@floating-ui/react-dom+[...].mjs";
import { o as require_jsx_runtime } from "../_libs/@radix-ui/react-arrow+[...].mjs";
import { i as cn, n as Button, r as api } from "./api-BvsAdfBD.mjs";
import { i as CardTitle, n as CardContent, r as CardHeader, t as Card } from "./card-DNn1texp.mjs";
import { I as ArrowUpDown, M as Check, O as CircleAlert, P as Boxes, h as Search, i as TriangleAlert, j as ChevronDown, k as ChevronUp, l as SquareActivity, p as ShieldAlert, t as X, v as PackageX, y as PackagePlus } from "../_libs/lucide-react.mjs";
import { t as Skeleton } from "./skeleton-coEUFSch.mjs";
import { n as useQuery } from "../_libs/tanstack__react-query.mjs";
import { t as Input } from "./input-BZC_VnU5.mjs";
import { a as TableHead, i as TableCell, n as Table, o as TableHeader, r as TableBody, s as TableRow, t as Badge } from "./badge-D-WmSVGe.mjs";
import { a as ItemText, c as Root2, d as Separator, f as Trigger, i as ItemIndicator, l as ScrollDownButton, m as Viewport, n as Icon, o as Label, p as Value, r as Item, s as Portal, t as Content2, u as ScrollUpButton } from "../_libs/@radix-ui/react-select+[...].mjs";
import { a as Bar, c as Tooltip, i as CartesianGrid, n as YAxis, o as Cell, r as XAxis, s as ResponsiveContainer, t as BarChart } from "../_libs/recharts+[...].mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/routes-B81x5FRg.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var Select = Root2;
var SelectValue = Value;
var SelectTrigger = import_react.forwardRef(({ className, children, ...props }, ref) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Trigger, {
	ref,
	className: cn("flex h-9 w-full items-center justify-between whitespace-nowrap rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm ring-offset-background cursor-pointer data-[placeholder]:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring disabled:cursor-not-allowed disabled:opacity-50 [&>span]:line-clamp-1", className),
	...props,
	children: [children, /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Icon, {
		asChild: true,
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChevronDown, { className: "h-4 w-4 opacity-50" })
	})]
}));
SelectTrigger.displayName = Trigger.displayName;
var SelectScrollUpButton = import_react.forwardRef(({ className, ...props }, ref) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ScrollUpButton, {
	ref,
	className: cn("flex cursor-default items-center justify-center py-1", className),
	...props,
	children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChevronUp, { className: "h-4 w-4" })
}));
SelectScrollUpButton.displayName = ScrollUpButton.displayName;
var SelectScrollDownButton = import_react.forwardRef(({ className, ...props }, ref) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ScrollDownButton, {
	ref,
	className: cn("flex cursor-default items-center justify-center py-1", className),
	...props,
	children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChevronDown, { className: "h-4 w-4" })
}));
SelectScrollDownButton.displayName = ScrollDownButton.displayName;
var SelectContent = import_react.forwardRef(({ className, children, position = "popper", ...props }, ref) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Portal, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Content2, {
	ref,
	className: cn("relative z-50 max-h-(--radix-select-content-available-height) min-w-[8rem] overflow-y-auto overflow-x-hidden rounded-md border bg-popover text-popover-foreground shadow-md data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2 origin-(--radix-select-content-transform-origin)", position === "popper" && "data-[side=bottom]:translate-y-1 data-[side=left]:-translate-x-1 data-[side=right]:translate-x-1 data-[side=top]:-translate-y-1", className),
	position,
	...props,
	children: [
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectScrollUpButton, {}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Viewport, {
			className: cn("p-1", position === "popper" && "h-[var(--radix-select-trigger-height)] w-full min-w-[var(--radix-select-trigger-width)]"),
			children
		}),
		/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectScrollDownButton, {})
	]
}) }));
SelectContent.displayName = Content2.displayName;
var SelectLabel = import_react.forwardRef(({ className, ...props }, ref) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Label, {
	ref,
	className: cn("px-2 py-1.5 text-sm font-semibold", className),
	...props
}));
SelectLabel.displayName = Label.displayName;
var SelectItem = import_react.forwardRef(({ className, children, ...props }, ref) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Item, {
	ref,
	className: cn("relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-2 pr-8 text-sm outline-none focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50", className),
	...props,
	children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
		className: "absolute right-2 flex h-3.5 w-3.5 items-center justify-center",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ItemIndicator, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Check, { className: "h-4 w-4" }) })
	}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ItemText, { children })]
}));
SelectItem.displayName = Item.displayName;
var SelectSeparator = import_react.forwardRef(({ className, ...props }, ref) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Separator, {
	ref,
	className: cn("-mx-1 my-1 h-px bg-muted", className),
	...props
}));
SelectSeparator.displayName = Separator.displayName;
var STYLES = {
	Healthy: "bg-emerald-100 text-emerald-800 border-emerald-200",
	"Near Reorder": "bg-amber-100 text-amber-800 border-amber-200",
	"Safety Stock Warning": "bg-orange-100 text-orange-800 border-orange-200",
	Shortage: "bg-red-100 text-red-800 border-red-200",
	Excess: "bg-sky-100 text-sky-800 border-sky-200"
};
function StatusBadge({ status, className }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
		variant: "outline",
		className: cn("font-medium", STYLES[status] ?? "bg-muted text-muted-foreground border-border", className),
		children: status
	});
}
var STATUS_COLORS = {
	Healthy: "#10b981",
	"Near Reorder": "#f59e0b",
	"Safety Stock Warning": "#f97316",
	Shortage: "#ef4444",
	Excess: "#0ea5e9"
};
function ProductRiskOverview() {
	const { data: rows = [], isLoading, error } = useQuery({
		queryKey: ["product-risk"],
		queryFn: api.productRisk
	});
	const [search, setSearch] = (0, import_react.useState)("");
	const [selectedPlant, setSelectedPlant] = (0, import_react.useState)("all");
	const [selectedStatus, setSelectedStatus] = (0, import_react.useState)("all");
	const [sortBy, setSortBy] = (0, import_react.useState)("priority_score");
	const [sortOrder, setSortOrder] = (0, import_react.useState)("desc");
	const [currentPage, setCurrentPage] = (0, import_react.useState)(1);
	const ITEMS_PER_PAGE = 10;
	const uniquePlants = (0, import_react.useMemo)(() => {
		const plants = new Set(rows.map((r) => r.plant_id));
		return Array.from(plants).sort();
	}, [rows]);
	const chartData = (0, import_react.useMemo)(() => {
		const counts = {
			"Shortage": 0,
			"Safety Stock Warning": 0,
			"Near Reorder": 0,
			"Healthy": 0,
			"Excess": 0
		};
		rows.forEach((r) => {
			if (selectedPlant !== "all" && r.plant_id !== selectedPlant) return;
			if (counts[r.health_status] !== void 0) counts[r.health_status]++;
		});
		return Object.keys(counts).map((key) => ({
			name: key,
			value: counts[key],
			fill: STATUS_COLORS[key] ?? "#94a3b8"
		}));
	}, [rows, selectedPlant]);
	const filteredRows = (0, import_react.useMemo)(() => {
		return rows.filter((r) => {
			const matchesSearch = r.material_id.toLowerCase().includes(search.toLowerCase()) || r.material_name.toLowerCase().includes(search.toLowerCase());
			const matchesPlant = selectedPlant === "all" || r.plant_id === selectedPlant;
			const matchesStatus = selectedStatus === "all" || r.health_status === selectedStatus;
			return matchesSearch && matchesPlant && matchesStatus;
		});
	}, [
		rows,
		search,
		selectedPlant,
		selectedStatus
	]);
	const sortedRows = (0, import_react.useMemo)(() => {
		const sorted = [...filteredRows];
		sorted.sort((a, b) => {
			const aVal = a[sortBy];
			const bVal = b[sortBy];
			if (aVal === void 0 || aVal === null) return 1;
			if (bVal === void 0 || bVal === null) return -1;
			if (typeof aVal === "string" && typeof bVal === "string") return sortOrder === "asc" ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
			else return sortOrder === "asc" ? aVal - bVal : bVal - aVal;
		});
		return sorted;
	}, [
		filteredRows,
		sortBy,
		sortOrder
	]);
	const paginatedRows = (0, import_react.useMemo)(() => {
		const start = (currentPage - 1) * ITEMS_PER_PAGE;
		return sortedRows.slice(start, start + ITEMS_PER_PAGE);
	}, [sortedRows, currentPage]);
	const totalPages = Math.ceil(sortedRows.length / ITEMS_PER_PAGE);
	const toggleSort = (field) => {
		if (sortBy === field) setSortOrder(sortOrder === "asc" ? "desc" : "asc");
		else {
			setSortBy(field);
			setSortOrder("desc");
		}
		setCurrentPage(1);
	};
	const handleChartClick = (data) => {
		if (data && data.name) {
			setSelectedStatus(selectedStatus === data.name ? "all" : data.name);
			setCurrentPage(1);
		}
	};
	const clearFilters = () => {
		setSearch("");
		setSelectedPlant("all");
		setSelectedStatus("all");
		setCurrentPage(1);
	};
	const isFiltered = search !== "" || selectedPlant !== "all" || selectedStatus !== "all";
	if (error) return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Card, {
		className: "rounded-xl border border-destructive/20 bg-destructive/5 p-6",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "text-center text-sm font-semibold text-destructive",
			children: ["Error loading product risk metrics: ", error.message]
		})
	});
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "space-y-6",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
			className: "shadow-sm bg-white rounded-xl border border-border",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardHeader, {
				className: "flex flex-col gap-4 md:flex-row md:items-start md:justify-between pb-6",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardTitle, {
					className: "text-lg font-bold text-foreground",
					children: "Product Risk Distribution"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "text-sm text-muted-foreground mt-1",
					children: "Click a bar in the chart to filter the detailed table below by that health status."
				})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "flex flex-wrap items-center gap-4",
					children: chartData.map((d) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						onClick: () => {
							setSelectedStatus(selectedStatus === d.name ? "all" : d.name);
							setCurrentPage(1);
						},
						className: `flex items-center gap-2 cursor-pointer transition-all hover:opacity-80 px-2 py-1 rounded-md ${selectedStatus === d.name ? "bg-slate-100 ring-1 ring-slate-200" : ""}`,
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "h-2.5 w-2.5 rounded-full",
							style: { backgroundColor: d.fill }
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
							className: "text-xs font-bold text-slate-700",
							children: [
								d.name,
								" (",
								d.value,
								")"
							]
						})]
					}, d.name))
				})]
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardContent, {
				className: "h-64",
				children: isLoading ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-full w-full rounded-lg" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ResponsiveContainer, {
					width: "100%",
					height: "100%",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(BarChart, {
						data: chartData,
						margin: {
							top: 8,
							right: 8,
							bottom: 8,
							left: 8
						},
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CartesianGrid, {
								strokeDasharray: "3 3",
								vertical: false,
								className: "stroke-slate-200"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(XAxis, {
								dataKey: "name",
								tick: {
									fontSize: 11,
									fontWeight: 500
								}
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(YAxis, {
								allowDecimals: false,
								tick: { fontSize: 11 }
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tooltip, {
								cursor: { fill: "rgba(148, 163, 184, 0.05)" },
								contentStyle: {
									background: "white",
									border: "1px solid rgb(226, 232, 240)",
									borderRadius: 8,
									fontSize: 12,
									boxShadow: "0 1px 3px rgba(0,0,0,0.05)"
								}
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Bar, {
								dataKey: "value",
								radius: [
									6,
									6,
									0,
									0
								],
								onClick: handleChartClick,
								className: "cursor-pointer",
								children: chartData.map((entry, idx) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Cell, {
									fill: entry.fill,
									opacity: selectedStatus === "all" || selectedStatus === entry.name ? 1 : .4,
									className: "transition-all duration-300"
								}, `cell-${idx}`))
							})
						]
					})
				})
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
			className: "shadow-sm bg-white rounded-xl border border-border",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardHeader, {
				className: "border-b border-border/50 pb-4 flex flex-col md:flex-row md:items-center justify-between gap-4",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardTitle, {
					className: "text-base font-bold text-foreground",
					children: "Material-Wise Health Posture"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "text-xs text-muted-foreground mt-1",
					children: "Table sorted by priority score (descending) by default."
				})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex flex-wrap items-center gap-3",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "relative",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Search, { className: "absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
								placeholder: "Search material...",
								value: search,
								onChange: (e) => {
									setSearch(e.target.value);
									setCurrentPage(1);
								},
								className: "pl-8 h-9 w-48 text-xs bg-white rounded-lg shadow-sm"
							})]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Select, {
							value: selectedPlant,
							onValueChange: (val) => {
								setSelectedPlant(val);
								setCurrentPage(1);
							},
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectTrigger, {
								className: "h-9 w-36 text-xs bg-white rounded-lg shadow-sm",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectValue, { placeholder: "All Plants" })
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(SelectContent, {
								className: "bg-white",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
									value: "all",
									children: "All Plants"
								}), uniquePlants.map((p) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
									value: p,
									children: p
								}, p))]
							})]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Select, {
							value: selectedStatus,
							onValueChange: (val) => {
								setSelectedStatus(val);
								setCurrentPage(1);
							},
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectTrigger, {
								className: "h-9 w-44 text-xs bg-white rounded-lg shadow-sm",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectValue, { placeholder: "All Statuses" })
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(SelectContent, {
								className: "bg-white",
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
										value: "all",
										children: "All Statuses"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
										value: "Healthy",
										children: "Healthy"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
										value: "Near Reorder",
										children: "Near Reorder"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
										value: "Safety Stock Warning",
										children: "Safety Stock Warning"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
										value: "Shortage",
										children: "Shortage"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
										value: "Excess",
										children: "Excess"
									})
								]
							})]
						}),
						isFiltered && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
							variant: "ghost",
							size: "sm",
							onClick: clearFilters,
							className: "h-9 text-xs gap-1 hover:bg-slate-100 shrink-0",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(X, { className: "h-3 w-3" }), " Reset"]
						})
					]
				})]
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardContent, {
				className: "p-0",
				children: [isLoading ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "space-y-2 p-6",
					children: Array.from({ length: 5 }).map((_, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-10 w-full rounded-md" }, i))
				}) : !sortedRows.length ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "p-8 text-center text-sm text-muted-foreground",
					children: "No matching materials found for the active filters."
				}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "overflow-x-auto",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Table, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHeader, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(TableRow, {
						className: "bg-slate-50/50 hover:bg-transparent",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
								className: "cursor-pointer font-bold text-slate-700",
								onClick: () => toggleSort("material_id"),
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex items-center gap-1",
									children: ["Material ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowUpDown, { className: "h-3 w-3" })]
								})
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
								className: "cursor-pointer font-bold text-slate-700",
								onClick: () => toggleSort("plant_id"),
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex items-center gap-1",
									children: ["Plant ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowUpDown, { className: "h-3 w-3" })]
								})
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
								className: "font-bold text-slate-700",
								children: "Status"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
								className: "text-right cursor-pointer font-bold text-slate-700",
								onClick: () => toggleSort("on_hand_qty"),
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex items-center justify-end gap-1",
									children: ["Usable Qty ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowUpDown, { className: "h-3 w-3" })]
								})
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
								className: "text-right cursor-pointer font-bold text-slate-700",
								onClick: () => toggleSort("reorder_point"),
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex items-center justify-end gap-1",
									children: ["Reorder Point ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowUpDown, { className: "h-3 w-3" })]
								})
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
								className: "text-right cursor-pointer font-bold text-slate-700",
								onClick: () => toggleSort("safety_stock"),
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex items-center justify-end gap-1",
									children: ["Safety Stock ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowUpDown, { className: "h-3 w-3" })]
								})
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
								className: "text-right cursor-pointer font-bold text-slate-700",
								onClick: () => toggleSort("days_of_supply"),
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex items-center justify-end gap-1",
									children: ["Days of Supply ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowUpDown, { className: "h-3 w-3" })]
								})
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
								className: "text-right cursor-pointer font-bold text-slate-700",
								onClick: () => toggleSort("priority_score"),
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex items-center justify-end gap-1",
									children: ["Priority Score ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowUpDown, { className: "h-3 w-3" })]
								})
							})
						]
					}) }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableBody, { children: paginatedRows.map((row, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(TableRow, {
						className: "hover:bg-slate-50/50 cursor-pointer border-b border-slate-100",
						onClick: () => {
							window.location.href = `/materials/${encodeURIComponent(row.material_id)}/${encodeURIComponent(row.plant_id)}`;
						},
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(TableCell, {
								className: "font-semibold text-slate-900",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { children: row.material_id }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
									className: "text-[10px] font-normal text-muted-foreground truncate max-w-[150px]",
									children: row.material_name
								})]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
								className: "text-slate-600",
								children: row.plant_id
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatusBadge, { status: row.health_status }) }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
								className: "text-right font-medium text-slate-900 tabular-nums",
								children: row.on_hand_qty.toLocaleString()
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
								className: "text-right text-slate-600 tabular-nums",
								children: row.reorder_point.toLocaleString()
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
								className: "text-right text-slate-600 tabular-nums",
								children: row.safety_stock.toLocaleString()
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
								className: `text-right font-semibold tabular-nums ${row.days_of_supply < 10 ? "text-red-600" : row.days_of_supply < 20 ? "text-amber-600" : "text-slate-600"}`,
								children: row.days_of_supply === 9999 ? "—" : row.days_of_supply.toFixed(1)
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
								className: "text-right tabular-nums",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: `inline-block font-bold text-xs px-2 py-0.5 rounded-full ${row.priority_score >= .8 ? "bg-red-50 text-red-700 border border-red-100" : row.priority_score >= .5 ? "bg-amber-50 text-amber-700 border border-amber-100" : "bg-slate-50 text-slate-700 border border-slate-100"}`,
									children: row.priority_score.toFixed(3)
								})
							})
						]
					}, `${row.material_id}-${row.plant_id}-${i}`)) })] })
				}), totalPages > 1 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex items-center justify-between border-t border-slate-100 p-4",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
						className: "text-xs text-muted-foreground font-medium",
						children: [
							"Showing ",
							(currentPage - 1) * ITEMS_PER_PAGE + 1,
							"-",
							Math.min(currentPage * ITEMS_PER_PAGE, sortedRows.length),
							" of ",
							sortedRows.length,
							" ",
							"items"
						]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex gap-2",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								variant: "outline",
								size: "sm",
								onClick: () => setCurrentPage((p) => Math.max(1, p - 1)),
								disabled: currentPage === 1,
								className: "text-xs h-8 bg-white border-slate-200",
								children: "Previous"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "flex items-center gap-1.5 text-xs text-slate-600 font-bold px-1",
								children: [
									currentPage,
									" of ",
									totalPages
								]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								variant: "outline",
								size: "sm",
								onClick: () => setCurrentPage((p) => Math.min(totalPages, p + 1)),
								disabled: currentPage === totalPages,
								className: "text-xs h-8 bg-white border-slate-200",
								children: "Next"
							})
						]
					})]
				})]
			})]
		})]
	});
}
function ProductBomRiskOverview() {
	const { data: rows = [], isLoading, error } = useQuery({
		queryKey: ["product-bom-risk"],
		queryFn: api.productBomRisk
	});
	const [search, setSearch] = (0, import_react.useState)("");
	const [selectedPlant, setSelectedPlant] = (0, import_react.useState)("all");
	const [selectedStatus, setSelectedStatus] = (0, import_react.useState)("all");
	const [sortBy, setSortBy] = (0, import_react.useState)("priority_score");
	const [sortOrder, setSortOrder] = (0, import_react.useState)("desc");
	const [currentPage, setCurrentPage] = (0, import_react.useState)(1);
	const [expandedRows, setExpandedRows] = (0, import_react.useState)({});
	const ITEMS_PER_PAGE = 10;
	const uniquePlants = (0, import_react.useMemo)(() => {
		const plants = new Set(rows.map((r) => r.plant_id));
		return Array.from(plants).sort();
	}, [rows]);
	const chartData = (0, import_react.useMemo)(() => {
		const counts = {
			"Shortage": 0,
			"Safety Stock Warning": 0,
			"Near Reorder": 0,
			"Healthy": 0,
			"Excess": 0
		};
		rows.forEach((r) => {
			if (selectedPlant !== "all" && r.plant_id !== selectedPlant) return;
			if (counts[r.risk_status] !== void 0) counts[r.risk_status]++;
		});
		return Object.keys(counts).map((key) => ({
			name: key,
			value: counts[key],
			fill: STATUS_COLORS[key] ?? "#94a3b8"
		}));
	}, [rows, selectedPlant]);
	const filteredRows = (0, import_react.useMemo)(() => {
		return rows.filter((r) => {
			const matchesSearch = r.product_id.toLowerCase().includes(search.toLowerCase()) || r.product_name.toLowerCase().includes(search.toLowerCase());
			const matchesPlant = selectedPlant === "all" || r.plant_id === selectedPlant;
			const matchesStatus = selectedStatus === "all" || r.risk_status === selectedStatus;
			return matchesSearch && matchesPlant && matchesStatus;
		});
	}, [
		rows,
		search,
		selectedPlant,
		selectedStatus
	]);
	const sortedRows = (0, import_react.useMemo)(() => {
		const sorted = [...filteredRows];
		sorted.sort((a, b) => {
			let aVal;
			let bVal;
			if (sortBy === "blocker_count") {
				aVal = a.blocking_components.length;
				bVal = b.blocking_components.length;
			} else {
				aVal = a[sortBy];
				bVal = b[sortBy];
			}
			if (aVal === void 0 || aVal === null) return 1;
			if (bVal === void 0 || bVal === null) return -1;
			if (typeof aVal === "string" && typeof bVal === "string") return sortOrder === "asc" ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
			else return sortOrder === "asc" ? aVal - bVal : bVal - aVal;
		});
		return sorted;
	}, [
		filteredRows,
		sortBy,
		sortOrder
	]);
	const paginatedRows = (0, import_react.useMemo)(() => {
		const start = (currentPage - 1) * ITEMS_PER_PAGE;
		return sortedRows.slice(start, start + ITEMS_PER_PAGE);
	}, [sortedRows, currentPage]);
	const totalPages = Math.ceil(sortedRows.length / ITEMS_PER_PAGE);
	const toggleSort = (field) => {
		if (sortBy === field) setSortOrder(sortOrder === "asc" ? "desc" : "asc");
		else {
			setSortBy(field);
			setSortOrder("desc");
		}
		setCurrentPage(1);
	};
	const handleChartClick = (data) => {
		if (data && data.name) {
			setSelectedStatus(selectedStatus === data.name ? "all" : data.name);
			setCurrentPage(1);
		}
	};
	const toggleRow = (key) => {
		setExpandedRows((prev) => ({
			...prev,
			[key]: !prev[key]
		}));
	};
	const clearFilters = () => {
		setSearch("");
		setSelectedPlant("all");
		setSelectedStatus("all");
		setCurrentPage(1);
	};
	const isFiltered = search !== "" || selectedPlant !== "all" || selectedStatus !== "all";
	if (error) return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Card, {
		className: "rounded-xl border border-destructive/20 bg-destructive/5 p-6",
		children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
			className: "text-center text-sm font-semibold text-destructive",
			children: ["Error loading BOM risk metrics: ", error.message]
		})
	});
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "space-y-6",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
			className: "shadow-sm bg-white rounded-xl border border-border",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardHeader, {
				className: "flex flex-col gap-4 md:flex-row md:items-start md:justify-between pb-6",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardTitle, {
					className: "text-lg font-bold text-foreground",
					children: "Finished Product Risk (BOM-Based)"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "text-sm text-muted-foreground mt-1",
					children: "Rolls up component health through the Bill of Materials. Click a status bar to filter the table."
				})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "flex flex-wrap items-center gap-4",
					children: chartData.map((d) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						onClick: () => {
							setSelectedStatus(selectedStatus === d.name ? "all" : d.name);
							setCurrentPage(1);
						},
						className: `flex items-center gap-2 cursor-pointer transition-all hover:opacity-80 px-2 py-1 rounded-md ${selectedStatus === d.name ? "bg-slate-100 ring-1 ring-slate-200" : ""}`,
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "h-2.5 w-2.5 rounded-full",
							style: { backgroundColor: d.fill }
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
							className: "text-xs font-bold text-slate-700",
							children: [
								d.name,
								" (",
								d.value,
								")"
							]
						})]
					}, d.name))
				})]
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardContent, {
				className: "h-64",
				children: isLoading ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-full w-full rounded-lg" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ResponsiveContainer, {
					width: "100%",
					height: "100%",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(BarChart, {
						data: chartData,
						margin: {
							top: 8,
							right: 8,
							bottom: 8,
							left: 8
						},
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CartesianGrid, {
								strokeDasharray: "3 3",
								vertical: false,
								className: "stroke-slate-200"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(XAxis, {
								dataKey: "name",
								tick: {
									fontSize: 11,
									fontWeight: 500
								}
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(YAxis, {
								allowDecimals: false,
								tick: { fontSize: 11 }
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Tooltip, {
								cursor: { fill: "rgba(148, 163, 184, 0.05)" },
								contentStyle: {
									background: "white",
									border: "1px solid rgb(226, 232, 240)",
									borderRadius: 8,
									fontSize: 12,
									boxShadow: "0 1px 3px rgba(0,0,0,0.05)"
								}
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Bar, {
								dataKey: "value",
								radius: [
									6,
									6,
									0,
									0
								],
								onClick: handleChartClick,
								className: "cursor-pointer",
								children: chartData.map((entry, idx) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Cell, {
									fill: entry.fill,
									opacity: selectedStatus === "all" || selectedStatus === entry.name ? 1 : .4,
									className: "transition-all duration-300"
								}, `cell-${idx}`))
							})
						]
					})
				})
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
			className: "shadow-sm bg-white rounded-xl border border-border",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardHeader, {
				className: "border-b border-border/50 pb-4 flex flex-col md:flex-row md:items-center justify-between gap-4",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardTitle, {
					className: "text-base font-bold text-foreground",
					children: "Finished Product Health Posture"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "text-xs text-muted-foreground mt-1",
					children: "Refined finished good risk based on worst-case component availability. Click row to expand blockers."
				})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex flex-wrap items-center gap-3",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "relative",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Search, { className: "absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Input, {
								placeholder: "Search product...",
								value: search,
								onChange: (e) => {
									setSearch(e.target.value);
									setCurrentPage(1);
								},
								className: "pl-8 h-9 w-48 text-xs bg-white rounded-lg shadow-sm"
							})]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Select, {
							value: selectedPlant,
							onValueChange: (val) => {
								setSelectedPlant(val);
								setCurrentPage(1);
							},
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectTrigger, {
								className: "h-9 w-36 text-xs bg-white rounded-lg shadow-sm",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectValue, { placeholder: "All Plants" })
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(SelectContent, {
								className: "bg-white",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
									value: "all",
									children: "All Plants"
								}), uniquePlants.map((p) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
									value: p,
									children: p
								}, p))]
							})]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Select, {
							value: selectedStatus,
							onValueChange: (val) => {
								setSelectedStatus(val);
								setCurrentPage(1);
							},
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectTrigger, {
								className: "h-9 w-44 text-xs bg-white rounded-lg shadow-sm",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectValue, { placeholder: "All Statuses" })
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(SelectContent, {
								className: "bg-white",
								children: [
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
										value: "all",
										children: "All Statuses"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
										value: "Healthy",
										children: "Healthy"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
										value: "Near Reorder",
										children: "Near Reorder"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
										value: "Safety Stock Warning",
										children: "Safety Stock Warning"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
										value: "Shortage",
										children: "Shortage"
									}),
									/* @__PURE__ */ (0, import_jsx_runtime.jsx)(SelectItem, {
										value: "Excess",
										children: "Excess"
									})
								]
							})]
						}),
						isFiltered && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Button, {
							variant: "ghost",
							size: "sm",
							onClick: clearFilters,
							className: "h-9 text-xs gap-1 hover:bg-slate-100 shrink-0",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(X, { className: "h-3 w-3" }), " Reset"]
						})
					]
				})]
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardContent, {
				className: "p-0",
				children: [isLoading ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "space-y-2 p-6",
					children: Array.from({ length: 5 }).map((_, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-10 w-full rounded-md" }, i))
				}) : !sortedRows.length ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "p-8 text-center text-sm text-muted-foreground",
					children: "No matching finished products found for the active filters."
				}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "overflow-x-auto",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Table, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHeader, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(TableRow, {
						className: "bg-slate-50/50 hover:bg-transparent",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, { className: "w-10" }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
								className: "cursor-pointer font-bold text-slate-700",
								onClick: () => toggleSort("product_id"),
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex items-center gap-1",
									children: ["Product ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowUpDown, { className: "h-3 w-3" })]
								})
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
								className: "cursor-pointer font-bold text-slate-700",
								onClick: () => toggleSort("plant_id"),
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex items-center gap-1",
									children: ["Plant ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowUpDown, { className: "h-3 w-3" })]
								})
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
								className: "font-bold text-slate-700",
								children: "BOM Status"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
								className: "text-right cursor-pointer font-bold text-slate-700",
								onClick: () => toggleSort("blocker_count"),
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex items-center justify-end gap-1",
									children: ["Blocking Components ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowUpDown, { className: "h-3 w-3" })]
								})
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
								className: "text-right cursor-pointer font-bold text-slate-700",
								onClick: () => toggleSort("priority_score"),
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "flex items-center justify-end gap-1",
									children: ["Max Priority Score ", /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ArrowUpDown, { className: "h-3 w-3" })]
								})
							})
						]
					}) }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableBody, { children: paginatedRows.map((row, i) => {
						const rowKey = `${row.product_id}-${row.plant_id}`;
						const isExpanded = !!expandedRows[rowKey];
						const blockerCount = row.blocking_components.length;
						return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Component, { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(TableRow, {
							className: "hover:bg-slate-50/50 cursor-pointer border-b border-slate-100",
							onClick: () => toggleRow(rowKey),
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
									className: "text-center p-2",
									children: isExpanded ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChevronUp, { className: "h-4 w-4 text-slate-500 inline" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)(ChevronDown, { className: "h-4 w-4 text-slate-500 inline" })
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(TableCell, {
									className: "font-semibold text-slate-900",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { children: row.product_id }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
										className: "text-[10px] font-normal text-muted-foreground truncate max-w-[200px]",
										children: row.product_name
									})]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
									className: "text-slate-600",
									children: row.plant_id
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatusBadge, { status: row.risk_status }) }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
									className: "text-right font-medium text-slate-700 tabular-nums",
									children: blockerCount > 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
										className: "inline-flex items-center gap-1 text-red-600 font-bold bg-red-50 border border-red-100 rounded-full px-2.5 py-0.5 text-xs",
										children: [
											/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CircleAlert, { className: "h-3 w-3" }),
											" ",
											blockerCount,
											" blocker",
											blockerCount > 1 ? "s" : ""
										]
									}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: "text-xs text-slate-400",
										children: "No blockers"
									})
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
									className: "text-right tabular-nums",
									children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
										className: `inline-block font-bold text-xs px-2 py-0.5 rounded-full ${row.priority_score >= .8 ? "bg-red-50 text-red-700 border border-red-100" : row.priority_score >= .5 ? "bg-amber-50 text-amber-700 border border-amber-100" : "bg-slate-50 text-slate-700 border border-slate-100"}`,
										children: row.priority_score.toFixed(3)
									})
								})
							]
						}), isExpanded && /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableRow, {
							className: "bg-slate-50/50 hover:bg-slate-50/50",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
								colSpan: 6,
								className: "p-4 pl-12 border-t border-slate-100",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
									className: "border border-slate-200/80 rounded-lg overflow-hidden bg-white shadow-xs",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
										className: "bg-slate-50 border-b border-slate-100 p-2.5 text-xs font-bold text-slate-700 flex justify-between",
										children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", { children: ["BOM COMPONENTS AFFECTING PRODUCTION FOR ", row.product_id] })
									}), !row.blocking_components.length ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
										className: "p-4 text-xs text-slate-500 text-center",
										children: "All component items are healthy at this plant. No production bottlenecks."
									}) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Table, {
										className: "text-xs",
										children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHeader, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(TableRow, {
											className: "bg-transparent hover:bg-transparent",
											children: [
												/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
													className: "h-8 font-semibold text-slate-500",
													children: "Component"
												}),
												/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
													className: "h-8 font-semibold text-slate-500",
													children: "Status"
												}),
												/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
													className: "h-8 text-right font-semibold text-slate-500",
													children: "Usable Stock"
												}),
												/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
													className: "h-8 text-right font-semibold text-slate-500",
													children: "Reorder Point"
												}),
												/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableHead, {
													className: "h-8 text-right font-semibold text-slate-500 text-red-600",
													children: "Net Shortfall"
												})
											]
										}) }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableBody, { children: row.blocking_components.map((comp, j) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(TableRow, {
											className: "hover:bg-slate-50/30 cursor-pointer",
											onClick: () => {
												window.location.href = `/materials/${encodeURIComponent(comp.material_id)}/${encodeURIComponent(row.plant_id)}`;
											},
											children: [
												/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
													className: "font-semibold text-slate-900 p-3",
													children: comp.material_id
												}),
												/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
													className: "p-3",
													children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(StatusBadge, {
														status: comp.health_status,
														className: "scale-90 origin-left"
													})
												}),
												/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
													className: "text-right tabular-nums p-3",
													children: comp.usable_qty.toLocaleString()
												}),
												/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
													className: "text-right tabular-nums p-3",
													children: comp.reorder_point.toLocaleString()
												}),
												/* @__PURE__ */ (0, import_jsx_runtime.jsx)(TableCell, {
													className: "text-right tabular-nums font-bold text-red-600 p-3",
													children: comp.shortfall.toLocaleString()
												})
											]
										}, `${comp.material_id}-${j}`)) })]
									})]
								})
							})
						})] }, rowKey);
					}) })] })
				}), totalPages > 1 && /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex items-center justify-between border-t border-slate-100 p-4",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
						className: "text-xs text-muted-foreground font-medium",
						children: [
							"Showing ",
							(currentPage - 1) * ITEMS_PER_PAGE + 1,
							"-",
							Math.min(currentPage * ITEMS_PER_PAGE, sortedRows.length),
							" of ",
							sortedRows.length,
							" ",
							"items"
						]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex gap-2",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								variant: "outline",
								size: "sm",
								onClick: () => setCurrentPage((p) => Math.max(1, p - 1)),
								disabled: currentPage === 1,
								className: "text-xs h-8 bg-white border-slate-200",
								children: "Previous"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "flex items-center gap-1.5 text-xs text-slate-600 font-bold px-1",
								children: [
									currentPage,
									" of ",
									totalPages
								]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								variant: "outline",
								size: "sm",
								onClick: () => setCurrentPage((p) => Math.min(totalPages, p + 1)),
								disabled: currentPage === totalPages,
								className: "text-xs h-8 bg-white border-slate-200",
								children: "Next"
							})
						]
					})]
				})]
			})]
		})]
	});
}
var Component = ({ children }) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(import_jsx_runtime.Fragment, { children });
var STATUS_META = [
	{
		key: "Healthy",
		label: "HEALTHY",
		icon: SquareActivity,
		accent: "text-emerald-500",
		borderColor: "border-emerald-200",
		bgColor: "bg-emerald-50"
	},
	{
		key: "Near Reorder",
		label: "NEAR REORDER",
		icon: TriangleAlert,
		accent: "text-amber-500",
		borderColor: "border-amber-200",
		bgColor: "bg-amber-50"
	},
	{
		key: "Safety Stock Warning",
		label: "SAFETY STOCK",
		icon: ShieldAlert,
		accent: "text-orange-500",
		borderColor: "border-orange-200",
		bgColor: "bg-orange-50"
	},
	{
		key: "Shortage",
		label: "SHORTAGE",
		icon: PackageX,
		accent: "text-red-500",
		borderColor: "border-red-200",
		bgColor: "bg-red-50"
	},
	{
		key: "Excess",
		label: "EXCESS",
		icon: PackagePlus,
		accent: "text-indigo-500",
		borderColor: "border-indigo-200",
		bgColor: "bg-indigo-50"
	}
];
function DashboardPage() {
	const summaryQ = useQuery({
		queryKey: ["summary"],
		queryFn: api.summary
	});
	const statusCounts = summaryQ.data?.status_counts ?? {};
	const totalRisky = Number(statusCounts["Shortage"] ?? 0) + Number(statusCounts["Safety Stock Warning"] ?? 0) + Number(statusCounts["Near Reorder"] ?? 0);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "space-y-6",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "text-2xl font-semibold tracking-tight",
				children: "Dashboard"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "text-sm text-muted-foreground mt-1",
				children: "Inventory health status and risk metrics across all plants."
			})] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
					className: "border border-border shadow-sm bg-white rounded-xl",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardHeader, {
						className: "flex flex-row items-center justify-between space-y-0 pb-3",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardTitle, {
							className: "text-xs font-bold tracking-widest text-muted-foreground uppercase",
							children: "Total Rows"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "p-1.5 rounded-md bg-slate-50",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Boxes, { className: "h-4 w-4 text-slate-500" })
						})]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardContent, { children: summaryQ.isLoading ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-8 w-16" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "space-y-1",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "text-[24px] leading-none font-bold text-slate-900",
							children: totalRisky
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: "w-4 border-b-[3px] border-border pt-2" })]
					}) })]
				}), STATUS_META.map((s) => {
					const Icon = s.icon;
					return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Card, {
						className: `border shadow-sm bg-white rounded-xl ${s.borderColor}`,
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(CardHeader, {
							className: "flex flex-row items-center justify-between space-y-0 pb-3",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardTitle, {
								className: `text-xs font-bold tracking-widest ${s.accent}`,
								children: s.label
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: `p-1.5 rounded-md ${s.bgColor}`,
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Icon, { className: `h-4 w-4 ${s.accent}` })
							})]
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(CardContent, { children: summaryQ.isLoading ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Skeleton, { className: "h-8 w-16" }) : /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "space-y-1",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: `text-[24px] leading-none font-bold ${s.accent}`,
								children: Number(statusCounts[s.key] ?? 0)
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { className: `w-4 border-b-[3px] pt-2 ${s.borderColor}` })]
						}) })]
					}, s.key);
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ProductRiskOverview, {}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(ProductBomRiskOverview, {})
		]
	});
}
//#endregion
export { DashboardPage as component };
