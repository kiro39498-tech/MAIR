import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

const STYLES: Record<string, string> = {
  Healthy: "bg-emerald-100 text-emerald-800 border-emerald-200",
  "Near Reorder": "bg-amber-100 text-amber-800 border-amber-200",
  "Safety Stock Warning": "bg-orange-100 text-orange-800 border-orange-200",
  Shortage: "bg-red-100 text-red-800 border-red-200",
  Excess: "bg-sky-100 text-sky-800 border-sky-200",
};

export function StatusBadge({ status, className }: { status: string; className?: string }) {
  const style = STYLES[status] ?? "bg-muted text-muted-foreground border-border";
  return (
    <Badge variant="outline" className={cn("font-medium", style, className)}>
      {status}
    </Badge>
  );
}

export const STATUS_COLORS: Record<string, string> = {
  Healthy: "#10b981",
  "Near Reorder": "#f59e0b",
  "Safety Stock Warning": "#f97316",
  Shortage: "#ef4444",
  Excess: "#0ea5e9",
};