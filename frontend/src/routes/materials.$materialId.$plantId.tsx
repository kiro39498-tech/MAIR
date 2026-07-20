import { createFileRoute, Link, useParams } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { 
  ArrowLeft, ShieldAlert, Lock, Shield, ShoppingCart, 
  Calendar, TrendingDown, Upload, Sparkles, Activity, Package
} from "lucide-react";

import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/materials/$materialId/$plantId")({
  component: MaterialDetailPage,
});

function MaterialDetailPage() {
  const { materialId, plantId } = useParams({ from: "/materials/$materialId/$plantId" });
  const q = useQuery({
    queryKey: ["material", materialId, plantId],
    queryFn: () => api.material(materialId, plantId),
  });

  const handleExport = (format: "json" | "csv") => {
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
      const csvRow = headers.map(h => {
        const val = (q.data as any)[h];
        if (typeof val === 'object' && val !== null) {
           return `"${JSON.stringify(val).replace(/"/g, '""')}"`;
        }
        return typeof val === 'string' ? `"${val.replace(/"/g, '""')}"` : val;
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

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-start gap-4">
          <Button asChild variant="outline" size="icon" className="h-8 w-8 mt-1 rounded-lg shrink-0 shadow-sm border-border/50">
            <Link to="/">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-2xl font-bold tracking-tight text-foreground">
                {materialId} <span className="text-muted-foreground font-normal mx-1">·</span> {plantId}
              </h2>
              {q.data?.status !== "Healthy" && (
                <span className="bg-primary/10 text-primary text-[11px] font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider">
                  Critical Material
                </span>
              )}
            </div>
            <p className="text-sm text-muted-foreground mt-1">Material Details & Status</p>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" className="gap-2 bg-white shadow-sm border-border/50 rounded-lg">
                <Upload className="h-4 w-4" /> Export
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48 bg-white">
              <DropdownMenuItem className="cursor-pointer font-medium" onClick={() => handleExport("csv")}>Export as CSV / Excel</DropdownMenuItem>
              <DropdownMenuItem className="cursor-pointer font-medium" onClick={() => handleExport("json")}>Export as JSON</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          <Button asChild className="gap-2 bg-primary text-primary-foreground shadow-sm rounded-lg hover:bg-primary/90">
            <a href={`/recommendations?materialId=${materialId}&plantId=${plantId}`}>
              <Sparkles className="h-4 w-4" /> View Recommendations
            </a>
          </Button>
        </div>
      </div>

      {q.isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-32 rounded-2xl" />
          ))}
        </div>
      ) : q.error ? (
        <Card className="rounded-2xl border-border/50">
          <CardContent className="p-8 text-center text-sm text-muted-foreground">
            Could not load material detail. {(q.error as Error).message}
          </CardContent>
        </Card>
      ) : q.data ? (
        <div className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <KpiCard 
              title="Health Status" 
              icon={<ShieldAlert className="h-5 w-5" />}
              iconBg="bg-orange-100 text-orange-600"
              value={q.data.status ?? "Unknown"} 
              valueClass={
                q.data.status === "Healthy" 
                  ? "text-emerald-600" 
                  : q.data.status?.includes("Shortage") 
                    ? "text-red-600" 
                    : "text-orange-600"
              }
            />
            <KpiCard 
              title="Usable Inventory" 
              icon={<Lock className="h-5 w-5" />}
              iconBg="bg-emerald-100 text-emerald-600"
              value={q.data.usable_inventory} 
              unit="Units"
            />
            <KpiCard 
              title="Safety Stock" 
              icon={<Shield className="h-5 w-5" />}
              iconBg="bg-blue-100 text-blue-600"
              value={q.data.safety_stock} 
              unit="Units"
            />
            <KpiCard 
              title="Reorder Point" 
              icon={<ShoppingCart className="h-5 w-5" />}
              iconBg="bg-purple-100 text-purple-600"
              value={q.data.reorder_point} 
              unit="Units"
            />
            <KpiCard 
              title="Projected Shortage Date" 
              icon={<Calendar className="h-5 w-5" />}
              iconBg="bg-rose-100 text-rose-600"
              value={q.data.projected_shortage_date ?? "—"} 
            />
            <KpiCard 
              title="Projected Shortage Qty" 
              icon={<TrendingDown className="h-5 w-5" />}
              iconBg="bg-red-100 text-red-600"
              value={q.data.projected_shortage_qty ?? "—"} 
              unit={q.data.projected_shortage_qty ? "Units" : undefined}
            />
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <DataCard 
              title="Production Impact" 
              icon={<Activity className="h-5 w-5 text-muted-foreground" />}
              data={q.data.production_impact as Record<string, any>} 
            />
            <DataCard 
              title="PO Coverage" 
              icon={<Package className="h-5 w-5 text-muted-foreground" />}
              data={q.data.po_coverage as Record<string, any>} 
            />
          </div>
        </div>
      ) : null}
    </div>
  );
}

function KpiCard({ title, icon, iconBg, value, valueClass, unit }: { 
  title: string; 
  icon: React.ReactNode; 
  iconBg: string; 
  value: unknown; 
  valueClass?: string;
  unit?: string;
}) {
  const display =
    value === null || value === undefined || value === ""
      ? "—"
      : typeof value === "number"
        ? value.toLocaleString()
        : String(value);

  return (
    <Card className="rounded-2xl border-border/50 shadow-sm bg-white overflow-hidden flex flex-col justify-between p-6">
      <div className="flex items-center gap-3">
        <div className={cn("flex h-10 w-10 shrink-0 items-center justify-center rounded-full", iconBg)}>
          {icon}
        </div>
        <div className="text-[13px] font-semibold text-muted-foreground uppercase tracking-wider">{title}</div>
      </div>
      <div className="mt-6 flex items-baseline gap-2">
        <div className={cn("text-3xl font-bold tracking-tight", valueClass || "text-foreground")}>
          {display}
        </div>
        {unit && display !== "—" && (
          <div className="text-sm font-medium text-muted-foreground">{unit}</div>
        )}
      </div>
    </Card>
  );
}

function DataCard({ title, icon, data }: { title: string; icon: React.ReactNode; data?: Record<string, any> }) {
  if (!data) return null;

  return (
    <Card className="rounded-2xl border-border/50 shadow-sm bg-white overflow-hidden flex flex-col">
      <CardHeader className="bg-muted/10 border-b border-border/50 p-4 flex flex-row items-center gap-3">
        {icon}
        <CardTitle className="text-base font-bold text-foreground m-0">{title}</CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="divide-y divide-border/50">
          {Object.entries(data).map(([key, val]) => {
            // Skip redundant IDs
            if (key === "material_id" || key === "plant_id") return null;
            
            const displayKey = key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
            
            let displayVal = "—";
            if (val !== null && val !== undefined) {
              if (typeof val === 'boolean') {
                displayVal = val ? "Yes" : "No";
              } else if (Array.isArray(val)) {
                displayVal = val.length === 0 ? "None" : val.join(", ");
              } else {
                displayVal = String(val);
              }
            }

            return (
              <div key={key} className="flex items-center justify-between p-4 hover:bg-muted/30 transition-colors">
                <div className="text-sm font-medium text-muted-foreground">{displayKey}</div>
                <div className="text-sm font-semibold text-foreground text-right">{displayVal}</div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}