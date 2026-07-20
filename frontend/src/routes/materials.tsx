import { createFileRoute, Link, Outlet, useRouterState } from "@tanstack/react-router";

export const Route = createFileRoute("/materials")({
  component: MaterialsLayout,
});

function MaterialsLayout() {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  if (pathname === "/materials") {
    return (
      <div className="rounded-lg border bg-card p-6 text-sm">
        <p className="mb-2 font-medium">Materials list</p>
        <p className="text-muted-foreground">
          The full materials list lives on the{" "}
          <Link to="/" className="text-primary underline">
            Dashboard
          </Link>
          . Select any row to open its detail here.
        </p>
      </div>
    );
  }
  return <Outlet />;
}