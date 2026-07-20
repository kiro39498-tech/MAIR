import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { useState, useEffect } from "react";

import { api, type Recommendation, type ReplenishmentAction } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { useQueryClient, useMutation } from "@tanstack/react-query";
import { 
  ChevronDown, 
  Download, 
  PackageX, 
  ShieldAlert, 
  AlertTriangle, 
  Square, 
  CheckSquare,
  X,
  ListChecks
} from "lucide-react";

export const Route = createFileRoute("/recommendations")({
  component: RecommendationsPage,
  validateSearch: (search: Record<string, unknown>) => {
    return {
      materialId: search.materialId as string | undefined,
      plantId: search.plantId as string | undefined,
    }
  }
});

function PriorityText({ priority }: { priority: string }) {
  const p = Number(priority);
  if (isNaN(p)) return <span className="text-xs font-semibold">{priority}</span>;
  
  if (p === 1) return <span className="font-semibold text-red-500 bg-red-50 px-2 py-0.5 rounded text-xs">{p}</span>;
  if (p >= 0.9) return <span className="font-semibold text-red-400 bg-red-50 px-2 py-0.5 rounded text-xs">{p}</span>;
  if (p >= 0.8) return <span className="font-semibold text-orange-500 bg-orange-50 px-2 py-0.5 rounded text-xs">{p}</span>;
  return <span className="font-semibold text-amber-500 bg-amber-50 px-2 py-0.5 rounded text-xs">{p}</span>;
}

function StatusBadge({ status }: { status: string }) {
  if (status === "Recommended") return <Badge variant="outline" className="text-gray-500">{status}</Badge>;
  if (status === "Drafted") return <Badge variant="outline" className="text-gray-500">{status}</Badge>;
  if (status === "PendingApproval") return <Badge variant="outline" className="text-amber-500 bg-amber-50">{status}</Badge>;
  if (status === "Approved") return <Badge variant="outline" className="text-blue-500 bg-blue-50">{status}</Badge>;
  if (status === "Executed") return <Badge variant="outline" className="text-emerald-500 bg-emerald-50">{status}</Badge>;
  if (status === "Failed") return <Badge variant="outline" className="text-red-500 bg-red-50">{status}</Badge>;
  if (status === "Rejected") return <Badge variant="outline" className="text-rose-500 bg-rose-50">{status}</Badge>;
  return <Badge variant="outline">{status}</Badge>;
}

type MergedRow = Recommendation & { action_status?: string; action_id?: string; suggested_qty?: number; action?: ReplenishmentAction };

function RecommendationsPage() {
  const queryClient = useQueryClient();
  const { materialId, plantId } = Route.useSearch();
  const q = useQuery({ queryKey: ["recommendations"], queryFn: api.recommendations });
  const aq = useQuery({ queryKey: ["actions"], queryFn: () => api.actions.list() });
  
  const [selected, setSelected] = useState<MergedRow | null>(null);
  const [selectedPlant, setSelectedPlant] = useState<string>("All Plants");
  const [currentPage, setCurrentPage] = useState(1);
  const [editQty, setEditQty] = useState<string>("");
  const [dismissed, setDismissed] = useState<Set<string>>(new Set());
  
  const recommendations = q.data ?? [];
  const actions = aq.data ?? [];
  
  const actionMap = new Map<string, ReplenishmentAction>();
  actions.forEach(a => actionMap.set(`${a.material_id}-${a.plant_id}`, a));
  
  const mergedRows: MergedRow[] = recommendations
    .filter(r => !dismissed.has(`${r.material_id}-${r.plant_id}`))
    .map(r => {
      const action = actionMap.get(`${r.material_id}-${r.plant_id}`);
      return {
        ...r,
        suggested_qty: r.recommended_qty ?? 0,
        action_status: action ? action.status : "Recommended",
        action_id: action ? action.action_id : undefined,
        action,
      };
    });
    
  actions.forEach(a => {
    if (!recommendations.find(r => r.material_id === a.material_id && r.plant_id === a.plant_id) && !dismissed.has(`${a.material_id}-${a.plant_id}`)) {
      mergedRows.push({
        material_id: a.material_id,
        plant_id: a.plant_id,
        priority: "0",
        reason: "Existing action",
        recommended_action: "Replenish",
        suggested_qty: a.recommended_qty,
        action_status: a.status,
        action_id: a.action_id,
        action: a,
      });
    }
  });

  const uniquePlants = Array.from(new Set(mergedRows.map(r => r.plant_id))).sort();
  const filteredRows = selectedPlant === "All Plants" ? mergedRows : mergedRows.filter(r => r.plant_id === selectedPlant);
  const ITEMS_PER_PAGE = 8;
  const totalPages = Math.ceil(filteredRows.length / ITEMS_PER_PAGE);
  const paginatedRows = filteredRows.slice((currentPage - 1) * ITEMS_PER_PAGE, currentPage * ITEMS_PER_PAGE);

  const createMutation = useMutation({
    mutationFn: (qty: number) => api.actions.create(selected!.material_id, selected!.plant_id, qty),
    onSuccess: () => {
      toast.success("Draft approved and submitted to manager.");
      queryClient.invalidateQueries({ queryKey: ["actions"] });
    },
    onError: (err) => {
      toast.error(err instanceof Error ? err.message : "Failed to create action");
    }
  });

  useEffect(() => {
    if (materialId && plantId && mergedRows.length > 0 && !selected) {
      const match = mergedRows.find(r => r.material_id === materialId && r.plant_id === plantId);
      if (match) {
        setSelected(match);
        setEditQty(String(match.suggested_qty ?? ""));
      }
    }
  }, [materialId, plantId, mergedRows, selected]);

  const handleExport = (format: "json" | "csv") => {
    if (!filteredRows.length) return;
    let content = "";
    let type = "";
    let ext = "";
    
    if (format === "json") {
      content = JSON.stringify(filteredRows, null, 2);
      type = "application/json";
      ext = "json";
    } else {
      const headers = Object.keys(filteredRows[0]).filter(k => typeof (filteredRows[0] as any)[k] !== 'object');
      const csvRows = filteredRows.map(row => 
        headers.map(h => {
          const val = (row as any)[h];
          return typeof val === 'string' ? `"${val.replace(/"/g, '""')}"` : val;
        }).join(",")
      );
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

  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-foreground">Recommendations</h2>
          <p className="text-sm text-muted-foreground mt-1">
            Draft replenishment actions generated by the planning agent.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <div className="flex items-center gap-2 rounded-lg border bg-white px-3 py-2 text-sm text-muted-foreground shadow-sm cursor-pointer hover:bg-muted/30">
                <span>{selectedPlant}</span>
                <ChevronDown className="h-4 w-4" />
              </div>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48 bg-white">
              <DropdownMenuItem className="cursor-pointer" onClick={() => { setSelectedPlant("All Plants"); setCurrentPage(1); }}>All Plants</DropdownMenuItem>
              {uniquePlants.map(p => (
                <DropdownMenuItem className="cursor-pointer" key={p} onClick={() => { setSelectedPlant(p); setCurrentPage(1); }}>{p}</DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button className="gap-2 bg-primary text-primary-foreground shadow-sm rounded-lg hover:bg-primary/90">
                <Download className="h-4 w-4" /> Export
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48 bg-white">
              <DropdownMenuItem className="cursor-pointer font-medium" onClick={() => handleExport("csv")}>Export as CSV / Excel</DropdownMenuItem>
              <DropdownMenuItem className="cursor-pointer font-medium" onClick={() => handleExport("json")}>Export as JSON</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      <div className={cn("grid gap-6", selected ? "lg:grid-cols-[1.5fr_1fr] xl:grid-cols-[2fr_1fr]" : "grid-cols-1")}>
        <Card className="shadow-sm bg-white rounded-2xl border-border/50 flex flex-col">
          <CardHeader className="flex flex-row items-center justify-between pb-4 border-b border-border/50">
            <CardTitle className="text-base font-bold text-foreground">Draft recommendations</CardTitle>
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="outline" className="bg-red-50 text-red-600 border-red-200 px-2 py-0.5 rounded-md text-xs">
                <PackageX className="mr-1 h-3 w-3" /> Shortage <span className="ml-1 font-bold">23</span>
              </Badge>
              <Badge variant="outline" className="bg-orange-50 text-orange-600 border-orange-200 px-2 py-0.5 rounded-md text-xs">
                <ShieldAlert className="mr-1 h-3 w-3" /> Safety Stock <span className="ml-1 font-bold">31</span>
              </Badge>
              <Badge variant="outline" className="bg-amber-50 text-amber-600 border-amber-200 px-2 py-0.5 rounded-md text-xs">
                <AlertTriangle className="mr-1 h-3 w-3" /> Near Reorder <span className="ml-1 font-bold">59</span>
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            {q.isLoading ? (
              <div className="space-y-2 p-4">
                {Array.from({ length: 6 }).map((_, i) => (
                  <Skeleton key={i} className="h-10 w-full" />
                ))}
              </div>
            ) : q.error ? (
              <div className="p-8 text-center text-sm text-muted-foreground">
                Could not load recommendations.
              </div>
            ) : !filteredRows.length ? (
              <div className="p-8 text-center text-sm text-muted-foreground">
                No recommendations matching this filter right now.
              </div>
            ) : (
              <div className="flex flex-col flex-1">
                <Table>
                  <TableHeader>
                    <TableRow className="border-b-border/50 hover:bg-transparent">
                      <TableHead className="w-12 text-center">
                        <Square className="h-4 w-4 text-muted-foreground/50 inline-block" />
                      </TableHead>
                      <TableHead>Material</TableHead>
                      <TableHead>Plant</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Priority</TableHead>
                      <TableHead>Reason</TableHead>
                      <TableHead className="text-right">Suggested Qty</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {paginatedRows.map((r, i) => {
                      const isSel =
                        selected?.material_id === r.material_id &&
                        selected?.plant_id === r.plant_id;
                      const displayQty = r.suggested_qty;
                      
                      return (
                        <TableRow
                          key={`${r.material_id}-${r.plant_id}-${i}`}
                          onClick={() => { setSelected(r); setEditQty(String(r.suggested_qty ?? "")); }}
                          className={cn("cursor-pointer border-b-border/30 transition-colors", isSel ? "bg-primary/5 border-primary/20" : "hover:bg-muted/30")}
                        >
                          <TableCell className="text-center">
                            {isSel ? <CheckSquare className="h-4 w-4 text-primary inline-block" /> : <Square className="h-4 w-4 text-muted-foreground/30 inline-block" />}
                          </TableCell>
                          <TableCell className="font-semibold text-foreground">{r.material_id}</TableCell>
                          <TableCell className="text-muted-foreground">{r.plant_id}</TableCell>
                          <TableCell><StatusBadge status={r.action_status ?? "Recommended"} /></TableCell>
                          <TableCell>
                            <PriorityText priority={String(r.priority)} />
                          </TableCell>
                          <TableCell className="max-w-xs truncate text-muted-foreground">
                            {r.reason}
                          </TableCell>
                          <TableCell className="text-right font-semibold text-foreground">
                            {displayQty}
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
                
                <div className="mt-auto flex items-center justify-between border-t border-border/50 p-4">
                  <span className="text-xs text-muted-foreground font-medium">
                    Showing {filteredRows.length > 0 ? (currentPage - 1) * ITEMS_PER_PAGE + 1 : 0}-{Math.min(currentPage * ITEMS_PER_PAGE, filteredRows.length)} of {filteredRows.length} recommendations
                  </span>
                  
                  {totalPages > 1 && (
                    <div className="flex items-center gap-1 text-xs text-muted-foreground">
                      <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setCurrentPage(p => Math.max(1, p - 1))} disabled={currentPage === 1}>
                        <ChevronDown className="h-3.5 w-3.5 rotate-90" />
                      </Button>
                      
                      {(() => {
                        const pages = [];
                        if (totalPages <= 6) {
                          for (let i = 1; i <= totalPages; i++) pages.push(i);
                        } else {
                          if (currentPage <= 3) {
                            pages.push(1, 2, 3, 4, 5, '...', totalPages);
                          } else if (currentPage >= totalPages - 2) {
                            pages.push(1, '...', totalPages - 4, totalPages - 3, totalPages - 2, totalPages - 1, totalPages);
                          } else {
                            pages.push(1, '...', currentPage - 1, currentPage, currentPage + 1, '...', totalPages);
                          }
                        }
                        
                        return pages.map((p, i) => 
                          p === '...' ? (
                            <span key={`dots-${i}`} className="px-1 tracking-widest">...</span>
                          ) : (
                            <Button 
                              key={`page-${p}`} 
                              variant="ghost" 
                              size="icon" 
                              className={cn("h-7 w-7 rounded-md font-medium", currentPage === p ? "bg-primary/10 text-primary font-bold hover:bg-primary/20" : "hover:bg-muted")}
                              onClick={() => setCurrentPage(p as number)}
                            >
                              {p}
                            </Button>
                          )
                        );
                      })()}

                      <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))} disabled={currentPage === totalPages}>
                        <ChevronDown className="h-3.5 w-3.5 -rotate-90" />
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {selected && (
          <Card className="shadow-sm bg-white rounded-2xl border-border/50 flex flex-col max-h-[800px] animate-in slide-in-from-right-4 fade-in duration-300">
            <CardHeader className="flex flex-row items-center justify-between border-b border-border/50 pb-4">
              <CardTitle className="text-base font-bold text-foreground">Detail</CardTitle>
              <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:bg-muted" onClick={() => setSelected(null)}>
                <X className="h-4 w-4" />
              </Button>
            </CardHeader>
            <CardContent className="p-0 flex flex-col flex-1 min-h-0">
              <>
                <div className="p-6 space-y-6 flex-1 overflow-y-auto">
                  <div>
                    <div className="text-xs text-muted-foreground mb-1">Material</div>
                    <div className="text-xl font-bold text-foreground">{selected.material_id}</div>
                  </div>
                  <div>
                    <div className="text-xs text-muted-foreground mb-1">Plant</div>
                    <div className="text-base font-bold text-foreground">{selected.plant_id}</div>
                    <div className="mt-2">
                      <span className="inline-flex items-center rounded-sm bg-red-50 px-2 py-0.5 text-xs font-semibold text-red-600 border border-red-200">
                        Priority {selected.priority} - Critical
                      </span>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <div className="text-xs text-muted-foreground mb-1">Recommended action</div>
                      <div className="font-bold text-foreground">{selected.recommended_action}</div>
                    </div>
                    <div>
                      <div className="text-xs text-muted-foreground mb-1">Reason</div>
                      <p className="text-sm text-muted-foreground">{selected.reason}</p>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4 pt-4 border-t border-border/50">
                    <div className="col-span-2">
                      <div className="text-[11px] text-muted-foreground uppercase tracking-wider font-semibold mb-1">Suggested Qty</div>
                      {(!selected.action_status || selected.action_status === "Recommended" || selected.action_status === "Drafted") ? (
                        <div className="flex items-center gap-2">
                           <Input type="number" value={editQty} onChange={(e) => setEditQty(e.target.value)} className="w-24 h-8 font-bold" />
                           <span className="text-sm font-medium text-muted-foreground">Units</span>
                        </div>
                      ) : (
                        <div className="font-bold text-foreground mt-1">{selected.suggested_qty} Units</div>
                      )}
                    </div>
                    <div>
                      <div className="text-[11px] text-muted-foreground uppercase tracking-wider font-semibold">Lead Time</div>
                      <div className="font-bold text-foreground mt-1">
                        {selected.lead_time_days !== undefined && selected.lead_time_days !== null
                          ? `${selected.lead_time_days} days`
                          : "—"}
                      </div>
                    </div>
                    <div>
                      <div className="text-[11px] text-muted-foreground uppercase tracking-wider font-semibold">Preferred Supplier</div>
                      <div className="font-bold text-foreground mt-1">
                        {selected.suggested_supplier_id || "—"}
                      </div>
                    </div>
                    <div>
                      <div className="text-[11px] text-muted-foreground uppercase tracking-wider font-semibold">Est. Arrival</div>
                      <div className="font-bold text-foreground mt-1">
                        {selected.lead_time_days !== undefined && selected.lead_time_days !== null
                          ? (() => {
                              const d = new Date();
                              d.setDate(d.getDate() + Number(selected.lead_time_days));
                              return d.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
                            })()
                          : "—"}
                      </div>
                    </div>
                  </div>
                </div>
                {(!selected.action_status || selected.action_status === "Recommended" || selected.action_status === "Drafted") ? (
                  <div className="p-4 border-t border-border/50 bg-muted/10 flex items-center gap-3">
                    <Button 
                      className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90 rounded-lg shadow-sm font-semibold"
                      onClick={() => createMutation.mutate(Number(editQty))}
                      disabled={createMutation.isPending}
                    >
                      {createMutation.isPending ? "Submitting..." : "Submit for Approval"}
                    </Button>
                    <Button 
                      variant="outline" 
                      className="flex-1 rounded-lg font-semibold bg-white"
                      onClick={() => {
                        setDismissed(prev => new Set(prev).add(`${selected.material_id}-${selected.plant_id}`));
                        setSelected(null);
                        toast.info("Recommendation dismissed.");
                      }}
                    >
                      Reject
                    </Button>
                  </div>
                ) : (
                  <div className="p-4 border-t border-border/50 bg-muted/10 flex flex-col gap-2">
                    <div className="text-sm text-center font-medium text-muted-foreground">
                      This action is currently <span className="font-bold text-foreground">{selected.action_status}</span>.
                    </div>
                  </div>
                )}
              </>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}