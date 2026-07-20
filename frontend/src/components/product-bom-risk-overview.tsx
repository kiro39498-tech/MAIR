import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { Search, ArrowUpDown, X, ChevronDown, ChevronUp, AlertCircle } from "lucide-react";

import { api, type ProductBomRiskRow } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { StatusBadge, STATUS_COLORS } from "@/components/status-badge";
import { Skeleton } from "@/components/ui/skeleton";

export function ProductBomRiskOverview() {
  const { data: rows = [], isLoading, error } = useQuery({
    queryKey: ["product-bom-risk"],
    queryFn: api.productBomRisk,
  });

  // Client-side filtering & sorting state
  const [search, setSearch] = useState("");
  const [selectedPlant, setSelectedPlant] = useState<string>("all");
  const [selectedStatus, setSelectedStatus] = useState<string>("all");
  const [sortBy, setSortBy] = useState<keyof ProductBomRiskRow | "blocker_count">("priority_score");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [currentPage, setCurrentPage] = useState(1);
  const [expandedRows, setExpandedRows] = useState<Record<string, boolean>>({});
  const ITEMS_PER_PAGE = 10;

  // 1. Get unique plant list for filter dropdown
  const uniquePlants = useMemo(() => {
    const plants = new Set(rows.map((r) => r.plant_id));
    return Array.from(plants).sort();
  }, [rows]);

  // 2. Aggregate counts per health status (for the Recharts chart)
  const chartData = useMemo(() => {
    const counts: Record<string, number> = {
      "Shortage": 0,
      "Safety Stock Warning": 0,
      "Near Reorder": 0,
      "Healthy": 0,
      "Excess": 0,
    };

    rows.forEach((r) => {
      if (selectedPlant !== "all" && r.plant_id !== selectedPlant) return;
      if (counts[r.risk_status] !== undefined) {
        counts[r.risk_status]++;
      }
    });

    return Object.keys(counts).map((key) => ({
      name: key,
      value: counts[key],
      fill: STATUS_COLORS[key] ?? "#94a3b8",
    }));
  }, [rows, selectedPlant]);

  // 3. Filter rows based on search, plant selection, and status selection
  const filteredRows = useMemo(() => {
    return rows.filter((r) => {
      const matchesSearch =
        r.product_id.toLowerCase().includes(search.toLowerCase()) ||
        r.product_name.toLowerCase().includes(search.toLowerCase());

      const matchesPlant = selectedPlant === "all" || r.plant_id === selectedPlant;
      const matchesStatus = selectedStatus === "all" || r.risk_status === selectedStatus;

      return matchesSearch && matchesPlant && matchesStatus;
    });
  }, [rows, search, selectedPlant, selectedStatus]);

  // 4. Sort rows
  const sortedRows = useMemo(() => {
    const sorted = [...filteredRows];
    sorted.sort((a, b) => {
      let aVal: any;
      let bVal: any;

      if (sortBy === "blocker_count") {
        aVal = a.blocking_components.length;
        bVal = b.blocking_components.length;
      } else {
        aVal = a[sortBy];
        bVal = b[sortBy];
      }

      if (aVal === undefined || aVal === null) return 1;
      if (bVal === undefined || bVal === null) return -1;

      if (typeof aVal === "string" && typeof bVal === "string") {
        return sortOrder === "asc"
          ? aVal.localeCompare(bVal)
          : bVal.localeCompare(aVal);
      } else {
        return sortOrder === "asc"
          ? (aVal as number) - (bVal as number)
          : (bVal as number) - (aVal as number);
      }
    });
    return sorted;
  }, [filteredRows, sortBy, sortOrder]);

  // 5. Paginate rows
  const paginatedRows = useMemo(() => {
    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    return sortedRows.slice(start, start + ITEMS_PER_PAGE);
  }, [sortedRows, currentPage]);

  const totalPages = Math.ceil(sortedRows.length / ITEMS_PER_PAGE);

  const toggleSort = (field: keyof ProductBomRiskRow | "blocker_count") => {
    if (sortBy === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(field);
      setSortOrder("desc");
    }
    setCurrentPage(1);
  };

  const handleChartClick = (data: any) => {
    if (data && data.name) {
      setSelectedStatus(selectedStatus === data.name ? "all" : data.name);
      setCurrentPage(1);
    }
  };

  const toggleRow = (key: string) => {
    setExpandedRows((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const clearFilters = () => {
    setSearch("");
    setSelectedPlant("all");
    setSelectedStatus("all");
    setCurrentPage(1);
  };

  const isFiltered = search !== "" || selectedPlant !== "all" || selectedStatus !== "all";

  if (error) {
    return (
      <Card className="rounded-xl border border-destructive/20 bg-destructive/5 p-6">
        <div className="text-center text-sm font-semibold text-destructive">
          Error loading BOM risk metrics: {(error as Error).message}
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* 1. Bar Chart Card */}
      <Card className="shadow-sm bg-white rounded-xl border border-border">
        <CardHeader className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between pb-6">
          <div>
            <CardTitle className="text-lg font-bold text-foreground">
              Finished Product Risk (BOM-Based)
            </CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              Rolls up component health through the Bill of Materials. Click a status bar to filter the table.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-4">
            {chartData.map((d) => (
              <div
                key={d.name}
                onClick={() => {
                  setSelectedStatus(selectedStatus === d.name ? "all" : d.name);
                  setCurrentPage(1);
                }}
                className={`flex items-center gap-2 cursor-pointer transition-all hover:opacity-80 px-2 py-1 rounded-md ${
                  selectedStatus === d.name ? "bg-slate-100 ring-1 ring-slate-200" : ""
                }`}
              >
                <div
                  className="h-2.5 w-2.5 rounded-full"
                  style={{ backgroundColor: d.fill }}
                ></div>
                <span className="text-xs font-bold text-slate-700">
                  {d.name} ({d.value})
                </span>
              </div>
            ))}
          </div>
        </CardHeader>
        <CardContent className="h-64">
          {isLoading ? (
            <Skeleton className="h-full w-full rounded-lg" />
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={chartData}
                margin={{ top: 8, right: 8, bottom: 8, left: 8 }}
              >
                <CartesianGrid strokeDasharray="3 3" vertical={false} className="stroke-slate-200" />
                <XAxis dataKey="name" tick={{ fontSize: 11, fontWeight: 500 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                <Tooltip
                  cursor={{ fill: "rgba(148, 163, 184, 0.05)" }}
                  contentStyle={{
                    background: "white",
                    border: "1px solid rgb(226, 232, 240)",
                    borderRadius: 8,
                    fontSize: 12,
                    boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
                  }}
                />
                <Bar
                  dataKey="value"
                  radius={[6, 6, 0, 0]}
                  onClick={handleChartClick}
                  className="cursor-pointer"
                >
                  {chartData.map((entry, idx) => (
                    <Cell
                      key={`cell-${idx}`}
                      fill={entry.fill}
                      opacity={selectedStatus === "all" || selectedStatus === entry.name ? 1.0 : 0.4}
                      className="transition-all duration-300"
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>

      {/* 2. Detailed Table Card */}
      <Card className="shadow-sm bg-white rounded-xl border border-border">
        <CardHeader className="border-b border-border/50 pb-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <CardTitle className="text-base font-bold text-foreground">
              Finished Product Health Posture
            </CardTitle>
            <p className="text-xs text-muted-foreground mt-1">
              Refined finished good risk based on worst-case component availability. Click row to expand blockers.
            </p>
          </div>

          {/* Filtering controls */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search product..."
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setCurrentPage(1);
                }}
                className="pl-8 h-9 w-48 text-xs bg-white rounded-lg shadow-sm"
              />
            </div>

            <Select
              value={selectedPlant}
              onValueChange={(val) => {
                setSelectedPlant(val);
                setCurrentPage(1);
              }}
            >
              <SelectTrigger className="h-9 w-36 text-xs bg-white rounded-lg shadow-sm">
                <SelectValue placeholder="All Plants" />
              </SelectTrigger>
              <SelectContent className="bg-white">
                <SelectItem value="all">All Plants</SelectItem>
                {uniquePlants.map((p) => (
                  <SelectItem key={p} value={p}>
                    {p}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select
              value={selectedStatus}
              onValueChange={(val) => {
                setSelectedStatus(val);
                setCurrentPage(1);
              }}
            >
              <SelectTrigger className="h-9 w-44 text-xs bg-white rounded-lg shadow-sm">
                <SelectValue placeholder="All Statuses" />
              </SelectTrigger>
              <SelectContent className="bg-white">
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="Healthy">Healthy</SelectItem>
                <SelectItem value="Near Reorder">Near Reorder</SelectItem>
                <SelectItem value="Safety Stock Warning">Safety Stock Warning</SelectItem>
                <SelectItem value="Shortage">Shortage</SelectItem>
                <SelectItem value="Excess">Excess</SelectItem>
              </SelectContent>
            </Select>

            {isFiltered && (
              <Button
                variant="ghost"
                size="sm"
                onClick={clearFilters}
                className="h-9 text-xs gap-1 hover:bg-slate-100 shrink-0"
              >
                <X className="h-3 w-3" /> Reset
              </Button>
            )}
          </div>
        </CardHeader>

        <CardContent className="p-0">
          {isLoading ? (
            <div className="space-y-2 p-6">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full rounded-md" />
              ))}
            </div>
          ) : !sortedRows.length ? (
            <div className="p-8 text-center text-sm text-muted-foreground">
              No matching finished products found for the active filters.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="bg-slate-50/50 hover:bg-transparent">
                    <TableHead className="w-10"></TableHead>
                    <TableHead
                      className="cursor-pointer font-bold text-slate-700"
                      onClick={() => toggleSort("product_id")}
                    >
                      <div className="flex items-center gap-1">
                        Product <ArrowUpDown className="h-3 w-3" />
                      </div>
                    </TableHead>
                    <TableHead
                      className="cursor-pointer font-bold text-slate-700"
                      onClick={() => toggleSort("plant_id")}
                    >
                      <div className="flex items-center gap-1">
                        Plant <ArrowUpDown className="h-3 w-3" />
                      </div>
                    </TableHead>
                    <TableHead className="font-bold text-slate-700">BOM Status</TableHead>
                    <TableHead
                      className="text-right cursor-pointer font-bold text-slate-700"
                      onClick={() => toggleSort("blocker_count")}
                    >
                      <div className="flex items-center justify-end gap-1">
                        Blocking Components <ArrowUpDown className="h-3 w-3" />
                      </div>
                    </TableHead>
                    <TableHead
                      className="text-right cursor-pointer font-bold text-slate-700"
                      onClick={() => toggleSort("priority_score")}
                    >
                      <div className="flex items-center justify-end gap-1">
                        Max Priority Score <ArrowUpDown className="h-3 w-3" />
                      </div>
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {paginatedRows.map((row, i) => {
                    const rowKey = `${row.product_id}-${row.plant_id}`;
                    const isExpanded = !!expandedRows[rowKey];
                    const blockerCount = row.blocking_components.length;

                    return (
                      <Component key={rowKey}>
                        <TableRow
                          className="hover:bg-slate-50/50 cursor-pointer border-b border-slate-100"
                          onClick={() => toggleRow(rowKey)}
                        >
                          <TableCell className="text-center p-2">
                            {isExpanded ? (
                              <ChevronUp className="h-4 w-4 text-slate-500 inline" />
                            ) : (
                              <ChevronDown className="h-4 w-4 text-slate-500 inline" />
                            )}
                          </TableCell>
                          <TableCell className="font-semibold text-slate-900">
                            <div>{row.product_id}</div>
                            <div className="text-[10px] font-normal text-muted-foreground truncate max-w-[200px]">
                              {row.product_name}
                            </div>
                          </TableCell>
                          <TableCell className="text-slate-600">{row.plant_id}</TableCell>
                          <TableCell>
                            <StatusBadge status={row.risk_status} />
                          </TableCell>
                          <TableCell className="text-right font-medium text-slate-700 tabular-nums">
                            {blockerCount > 0 ? (
                              <span className="inline-flex items-center gap-1 text-red-600 font-bold bg-red-50 border border-red-100 rounded-full px-2.5 py-0.5 text-xs">
                                <AlertCircle className="h-3 w-3" /> {blockerCount} blocker{blockerCount > 1 ? "s" : ""}
                              </span>
                            ) : (
                              <span className="text-xs text-slate-400">No blockers</span>
                            )}
                          </TableCell>
                          <TableCell className="text-right tabular-nums">
                            <span
                              className={`inline-block font-bold text-xs px-2 py-0.5 rounded-full ${
                                row.priority_score >= 0.8
                                  ? "bg-red-50 text-red-700 border border-red-100"
                                  : row.priority_score >= 0.5
                                  ? "bg-amber-50 text-amber-700 border border-amber-100"
                                  : "bg-slate-50 text-slate-700 border border-slate-100"
                              }`}
                            >
                              {row.priority_score.toFixed(3)}
                            </span>
                          </TableCell>
                        </TableRow>

                        {/* Expanded Blocker Details */}
                        {isExpanded && (
                          <TableRow className="bg-slate-50/50 hover:bg-slate-50/50">
                            <TableCell colSpan={6} className="p-4 pl-12 border-t border-slate-100">
                              <div className="border border-slate-200/80 rounded-lg overflow-hidden bg-white shadow-xs">
                                <div className="bg-slate-50 border-b border-slate-100 p-2.5 text-xs font-bold text-slate-700 flex justify-between">
                                  <span>BOM COMPONENTS AFFECTING PRODUCTION FOR {row.product_id}</span>
                                </div>
                                {!row.blocking_components.length ? (
                                  <div className="p-4 text-xs text-slate-500 text-center">
                                    All component items are healthy at this plant. No production bottlenecks.
                                  </div>
                                ) : (
                                  <Table className="text-xs">
                                    <TableHeader>
                                      <TableRow className="bg-transparent hover:bg-transparent">
                                        <TableHead className="h-8 font-semibold text-slate-500">Component</TableHead>
                                        <TableHead className="h-8 font-semibold text-slate-500">Status</TableHead>
                                        <TableHead className="h-8 text-right font-semibold text-slate-500">Usable Stock</TableHead>
                                        <TableHead className="h-8 text-right font-semibold text-slate-500">Reorder Point</TableHead>
                                        <TableHead className="h-8 text-right font-semibold text-slate-500 text-red-600">Net Shortfall</TableHead>
                                      </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                      {row.blocking_components.map((comp, j) => (
                                        <TableRow
                                          key={`${comp.material_id}-${j}`}
                                          className="hover:bg-slate-50/30 cursor-pointer"
                                          onClick={() => {
                                            window.location.href = `/materials/${encodeURIComponent(comp.material_id)}/${encodeURIComponent(row.plant_id)}`;
                                          }}
                                        >
                                          <TableCell className="font-semibold text-slate-900 p-3">{comp.material_id}</TableCell>
                                          <TableCell className="p-3"><StatusBadge status={comp.health_status} className="scale-90 origin-left" /></TableCell>
                                          <TableCell className="text-right tabular-nums p-3">{comp.usable_qty.toLocaleString()}</TableCell>
                                          <TableCell className="text-right tabular-nums p-3">{comp.reorder_point.toLocaleString()}</TableCell>
                                          <TableCell className="text-right tabular-nums font-bold text-red-600 p-3">{comp.shortfall.toLocaleString()}</TableCell>
                                        </TableRow>
                                      ))}
                                    </TableBody>
                                  </Table>
                                )}
                              </div>
                            </TableCell>
                          </TableRow>
                        )}
                      </Component>
                    );
                  })}
                </TableBody>
              </Table>
            </div>
          )}

          {/* Pagination controls */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between border-t border-slate-100 p-4">
              <span className="text-xs text-muted-foreground font-medium">
                Showing {(currentPage - 1) * ITEMS_PER_PAGE + 1}-
                {Math.min(currentPage * ITEMS_PER_PAGE, sortedRows.length)} of {sortedRows.length}{" "}
                items
              </span>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="text-xs h-8 bg-white border-slate-200"
                >
                  Previous
                </Button>
                <div className="flex items-center gap-1.5 text-xs text-slate-600 font-bold px-1">
                  {currentPage} of {totalPages}
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="text-xs h-8 bg-white border-slate-200"
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// React fragment wrapper helper
const Component = ({ children }: { children: React.ReactNode }) => <>{children}</>;
