import { m as createFileRoute, p as lazyRouteComponent } from "../_libs/@tanstack/react-router+[...].mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/recommendations-Dujm8yQC.js
var $$splitComponentImporter = () => import("./recommendations-BtCVXSDy.mjs");
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
