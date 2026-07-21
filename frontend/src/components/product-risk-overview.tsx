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
import { Search, ArrowUpDown, X } from "lucide-react";

import { api, type ProductRiskRow } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

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

export function ProductRiskOverview() {
  const { data: rows = [], isLoading, error } = useQuery({
    queryKey: ["product-risk"],
    queryFn: api.productRisk,
  });

  const [selectedMaterial, setSelectedMaterial] = useState<ProductRiskRow | null>(null);

  const { data: usage = [], isLoading: isUsageLoading, error: usageError } = useQuery({
    queryKey: ["material-usage", selectedMaterial?.material_id, selectedMaterial?.plant_id],
    queryFn: () => selectedMaterial ? api.materialUsage(selectedMaterial.material_id, selectedMaterial.plant_id) : Promise.resolve([]),
    enabled: !!selectedMaterial,
  });

  // Client-side state for sorting and filtering

  const [search, setSearch] = useState("");
  const [selectedPlant, setSelectedPlant] = useState<string>("all");
  const [selectedStatus, setSelectedStatus] = useState<string>("all");
  const [sortBy, setSortBy] = useState<keyof ProductRiskRow>("priority_score");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [currentPage, setCurrentPage] = useState(1);
  const ITEMS_PER_PAGE = 10;

  // 1. Get unique plant list for filter dropdown
  const uniquePlants = useMemo(() => {
    const plants = new Set(rows.map((r) => r.plant_id));
    return Array.from(plants).sort();
  }, [rows]);

  // 2. Aggregate counts per health status (for the Recharts chart) based on current filtered/unfiltered dataset
  const chartData = useMemo(() => {
    const counts: Record<string, number> = {
      "Shortage": 0,
      "Safety Stock Warning": 0,
      "Near Reorder": 0,
      "Healthy": 0,
      "Excess": 0,
    };
    
    // Aggregate over rows matching the active plant filter (so the chart updates when plant changes)
    rows.forEach((r) => {
      if (selectedPlant !== "all" && r.plant_id !== selectedPlant) return;
      if (counts[r.health_status] !== undefined) {
        counts[r.health_status]++;
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
        r.material_id.toLowerCase().includes(search.toLowerCase()) ||
        r.material_name.toLowerCase().includes(search.toLowerCase());
      
      const matchesPlant = selectedPlant === "all" || r.plant_id === selectedPlant;
      const matchesStatus = selectedStatus === "all" || r.health_status === selectedStatus;

      return matchesSearch && matchesPlant && matchesStatus;
    });
  }, [rows, search, selectedPlant, selectedStatus]);

  // 4. Sort rows
  const sortedRows = useMemo(() => {
    const sorted = [...filteredRows];
    sorted.sort((a, b) => {
      const aVal = a[sortBy];
      const bVal = b[sortBy];

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

  const toggleSort = (field: keyof ProductRiskRow) => {
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
          Error loading product risk metrics: {(error as Error).message}
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
              Product Risk Distribution
            </CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              Click a bar in the chart to filter the detailed table below by that health status.
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

      {/* 2. Detailed Table Card wrapped in grid */}
      <div className={cn("grid gap-6", selectedMaterial ? "lg:grid-cols-[1.5fr_1fr] xl:grid-cols-[2fr_1fr]" : "grid-cols-1")}>
        <Card className="shadow-sm bg-white rounded-xl border border-border flex flex-col">

        <CardHeader className="border-b border-border/50 pb-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <CardTitle className="text-base font-bold text-foreground">
              Material-Wise Health Posture
            </CardTitle>
            <p className="text-xs text-muted-foreground mt-1">
              Table sorted by priority score (descending) by default.
            </p>
          </div>

          {/* Filtering controls */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search material..."
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
              No matching materials found for the active filters.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="bg-slate-50/50 hover:bg-transparent">
                    <TableHead
                      className="cursor-pointer font-bold text-slate-700"
                      onClick={() => toggleSort("material_id")}
                    >
                      <div className="flex items-center gap-1">
                        Material <ArrowUpDown className="h-3 w-3" />
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
                    <TableHead className="font-bold text-slate-700">Status</TableHead>
                    <TableHead
                      className="text-right cursor-pointer font-bold text-slate-700"
                      onClick={() => toggleSort("on_hand_qty")}
                    >
                      <div className="flex items-center justify-end gap-1">
                        Usable Qty <ArrowUpDown className="h-3 w-3" />
                      </div>
                    </TableHead>
                    <TableHead
                      className="text-right cursor-pointer font-bold text-slate-700"
                      onClick={() => toggleSort("reorder_point")}
                    >
                      <div className="flex items-center justify-end gap-1">
                        Reorder Point <ArrowUpDown className="h-3 w-3" />
                      </div>
                    </TableHead>
                    <TableHead
                      className="text-right cursor-pointer font-bold text-slate-700"
                      onClick={() => toggleSort("safety_stock")}
                    >
                      <div className="flex items-center justify-end gap-1">
                        Safety Stock <ArrowUpDown className="h-3 w-3" />
                      </div>
                    </TableHead>
                    <TableHead
                      className="text-right cursor-pointer font-bold text-slate-700"
                      onClick={() => toggleSort("days_of_supply")}
                    >
                      <div className="flex items-center justify-end gap-1">
                        Days of Supply <ArrowUpDown className="h-3 w-3" />
                      </div>
                    </TableHead>
                    <TableHead
                      className="text-right cursor-pointer font-bold text-slate-700"
                      onClick={() => toggleSort("priority_score")}
                    >
                      <div className="flex items-center justify-end gap-1">
                        Priority Score <ArrowUpDown className="h-3 w-3" />
                      </div>
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {paginatedRows.map((row, i) => {
                    const isSel =
                      selectedMaterial?.material_id === row.material_id &&
                      selectedMaterial?.plant_id === row.plant_id;

                    return (
                      <TableRow
                        key={`${row.material_id}-${row.plant_id}-${i}`}
                        className={cn(
                          "cursor-pointer border-b border-slate-100 transition-colors",
                          isSel ? "bg-primary/5 border-primary/20" : "hover:bg-slate-50/50"
                        )}
                        onClick={() => {
                          setSelectedMaterial(row);
                        }}
                      >

                      <TableCell className="font-semibold text-slate-900">
                        <div>{row.material_id}</div>
                        <div className="text-[10px] font-normal text-muted-foreground truncate max-w-[150px]">
                          {row.material_name}
                        </div>
                      </TableCell>
                      <TableCell className="text-slate-600">{row.plant_id}</TableCell>
                      <TableCell>
                        <StatusBadge status={row.health_status} />
                      </TableCell>
                      <TableCell className="text-right font-medium text-slate-900 tabular-nums">
                        {row.on_hand_qty.toLocaleString()}
                      </TableCell>
                      <TableCell className="text-right text-slate-600 tabular-nums">
                        {row.reorder_point.toLocaleString()}
                      </TableCell>
                      <TableCell className="text-right text-slate-600 tabular-nums">
                        {row.safety_stock.toLocaleString()}
                      </TableCell>
                      <TableCell
                        className={`text-right font-semibold tabular-nums ${
                          row.days_of_supply < 10
                            ? "text-red-600"
                            : row.days_of_supply < 20
                            ? "text-amber-600"
                            : "text-slate-600"
                        }`}
                      >
                        {row.days_of_supply === 9999 ? "—" : row.days_of_supply.toFixed(1)}
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

      {selectedMaterial && (
        <Card className="shadow-sm bg-white rounded-xl border border-border flex flex-col max-h-[800px] animate-in slide-in-from-right-4 fade-in duration-300">
          <CardHeader className="flex flex-row items-center justify-between border-b border-border/50 pb-4">
            <CardTitle className="text-base font-bold text-foreground">Material Usage Detail</CardTitle>
            <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:bg-muted" onClick={() => setSelectedMaterial(null)}>
              <X className="h-4 w-4" />
            </Button>
          </CardHeader>
          <CardContent className="p-0 flex flex-col flex-1 min-h-0">
            <div className="p-6 space-y-6 flex-1 overflow-y-auto">
              <div className="flex justify-between items-start">
                <div>
                  <div className="text-xs text-muted-foreground mb-1">Selected Material</div>
                  <div className="text-xl font-bold text-foreground">{selectedMaterial.material_id}</div>
                  <div className="text-sm text-muted-foreground mt-0.5">{selectedMaterial.material_name}</div>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  className="text-xs bg-white"
                  onClick={() => {
                    window.location.href = `/materials/${encodeURIComponent(selectedMaterial.material_id)}/${encodeURIComponent(selectedMaterial.plant_id)}`;
                  }}
                >
                  View Details
                </Button>
              </div>
              <div>
                <div className="text-xs text-muted-foreground mb-1">Plant Location</div>
                <div className="text-base font-bold text-foreground">{selectedMaterial.plant_id}</div>
              </div>
              
              <div className="pt-4 border-t border-border/50 space-y-3">
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">Used in Finished Goods</h4>
                
                {isUsageLoading ? (
                  <div className="space-y-2">
                    <Skeleton className="h-8 w-full" />
                    <Skeleton className="h-8 w-full" />
                  </div>
                ) : usageError ? (
                  <div className="text-xs text-red-500 font-semibold">Error loading usage: {(usageError as Error).message}</div>
                ) : usage.length === 0 ? (
                  <div className="p-4 text-center border border-dashed rounded-lg text-xs text-slate-400 bg-slate-50/50">
                    Not used in any finished products' BOM.
                  </div>
                ) : (
                  <div className="border border-slate-200 rounded-lg overflow-hidden">
                    <Table className="text-xs">
                      <TableHeader className="bg-slate-50/50">
                        <TableRow>
                          <TableHead className="font-semibold text-slate-500 h-8">Product</TableHead>
                          <TableHead className="font-semibold text-slate-500 h-8">Plant</TableHead>
                          <TableHead className="font-semibold text-slate-500 h-8">Status</TableHead>
                          <TableHead className="font-semibold text-slate-500 h-8 text-right">Qty/Unit</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {usage.map((item, idx) => (
                          <TableRow key={`${item.product_id}-${idx}`} className={cn("hover:bg-slate-50/30", item.is_blocking ? "bg-red-50/30 hover:bg-red-50/50" : "")}>
                            <TableCell className="font-semibold text-slate-900 p-2.5">
                              <div>{item.product_id}</div>
                              <div className="text-[10px] font-normal text-muted-foreground truncate max-w-[120px]">{item.product_name}</div>
                            </TableCell>
                            <TableCell className="p-2.5 text-slate-600">{item.plant_id}</TableCell>
                            <TableCell className="p-2.5">
                              <div className="flex flex-col gap-1 items-start">
                                <StatusBadge status={item.risk_status} className="scale-90 origin-left" />
                                {item.is_blocking && (
                                  <span className="inline-block text-[9px] font-bold text-red-600 bg-red-50 border border-red-100 rounded px-1">
                                    BLOCKING COMPONENT
                                  </span>
                                )}
                              </div>
                            </TableCell>
                            <TableCell className="p-2.5 text-right font-medium tabular-nums">{item.qty_per_unit.toFixed(3)}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  </div>

  );
}
