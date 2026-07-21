import { createFileRoute } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import {
  Boxes,
  ActivitySquare,
  AlertTriangle,
  ShieldAlert,
  PackageX,
  PackagePlus,
} from "lucide-react";

import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ProductRiskOverview } from "@/components/product-risk-overview";
import { ProductBomRiskOverview } from "@/components/product-bom-risk-overview";

export const Route = createFileRoute("/")({
  component: DashboardPage,
});

const STATUS_META: {
  key: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  accent: string;
  borderColor: string;
  bgColor: string;
}[] = [
    { key: "Healthy", label: "HEALTHY", icon: ActivitySquare, accent: "text-emerald-500", borderColor: "border-emerald-200", bgColor: "bg-emerald-50" },
    { key: "Near Reorder", label: "NEAR REORDER", icon: AlertTriangle, accent: "text-amber-500", borderColor: "border-amber-200", bgColor: "bg-amber-50" },
    { key: "Safety Stock Warning", label: "SAFETY STOCK", icon: ShieldAlert, accent: "text-orange-500", borderColor: "border-orange-200", bgColor: "bg-orange-50" },
    { key: "Shortage", label: "SHORTAGE", icon: PackageX, accent: "text-red-500", borderColor: "border-red-200", bgColor: "bg-red-50" },
    { key: "Excess", label: "EXCESS", icon: PackagePlus, accent: "text-indigo-500", borderColor: "border-indigo-200", bgColor: "bg-indigo-50" },
  ];

function DashboardPage() {
  const summaryQ = useQuery({ queryKey: ["summary"], queryFn: api.summary });

  const statusCounts = summaryQ.data?.status_counts ?? {};
  const totalRisky =
    Number(statusCounts["Shortage"] ?? 0) +
    Number(statusCounts["Safety Stock Warning"] ?? 0) +
    Number(statusCounts["Near Reorder"] ?? 0);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Dashboard</h2>
        <p className="text-sm text-muted-foreground mt-1">
          Inventory health status and risk metrics across all plants.
        </p>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6">
        <Card className="border border-border shadow-sm bg-white rounded-xl">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
            <CardTitle className="text-xs font-bold tracking-widest text-muted-foreground uppercase">
              Total Materials
            </CardTitle>
            <div className="p-1.5 rounded-md bg-slate-50">
              <Boxes className="h-4 w-4 text-slate-500" />
            </div>
          </CardHeader>
          <CardContent>
            {summaryQ.isLoading ? (
              <Skeleton className="h-8 w-16" />
            ) : (
              <div className="space-y-1">
                <div className="text-[24px] leading-none font-bold text-slate-900">{summaryQ.data?.total_rows ?? 0}</div>
                <div className="w-4 border-b-[3px] border-border pt-2" />
              </div>
            )}
          </CardContent>
        </Card>
        {STATUS_META.map((s) => {
          const Icon = s.icon;
          return (
            <Card key={s.key} className={`border shadow-sm bg-white rounded-xl ${s.borderColor}`}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                <CardTitle className={`text-xs font-bold tracking-widest ${s.accent}`}>
                  {s.label}
                </CardTitle>
                <div className={`p-1.5 rounded-md ${s.bgColor}`}>
                  <Icon className={`h-4 w-4 ${s.accent}`} />
                </div>
              </CardHeader>
              <CardContent>
                {summaryQ.isLoading ? (
                  <Skeleton className="h-8 w-16" />
                ) : (
                  <div className="space-y-1">
                    <div className={`text-[24px] leading-none font-bold ${s.accent}`}>{Number(statusCounts[s.key] ?? 0)}</div>
                    <div className={`w-4 border-b-[3px] pt-2 ${s.borderColor}`} />
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Product-Wise Risk Overview component */}
      <ProductRiskOverview />

      {/* Finished Product Risk (BOM-Based) component */}
      <ProductBomRiskOverview />
    </div>
  );
}

