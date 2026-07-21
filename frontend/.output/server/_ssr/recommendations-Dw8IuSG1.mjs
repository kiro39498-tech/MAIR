import { m as createFileRoute, p as lazyRouteComponent } from "../_libs/@tanstack/react-router+[...].mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/recommendations-Dw8IuSG1.js
var $$splitComponentImporter = () => import("./recommendations-DiuP1BBy.mjs");
var Route = createFileRoute("/recommendations")({
	component: lazyRouteComponent($$splitComponentImporter, "component"),
	validateSearch: (search) => {
		return {
			materialId: search.materialId,
			plantId: search.plantId
		};
	}
});
//#endregion
export { Route as t };
