globalThis.__nitro_main__ = import.meta.url;
import { a as FastResponse, n as HTTPError, r as defineLazyEventHandler, t as H3Core } from "./_libs/h3+rou3+srvx.mjs";
import { t as HookableCore } from "./_libs/hookable.mjs";
//#region #nitro-vite-setup
function lazyService(loader) {
	let promise, mod;
	return { fetch(req) {
		if (mod) return mod.fetch(req);
		if (!promise) promise = loader().then((_mod) => mod = _mod.default || _mod);
		return promise.then((mod) => mod.fetch(req));
	} };
}
var services = { ["ssr"]: lazyService(() => import("./_ssr/ssr.mjs")) };
globalThis.__nitro_vite_envs__ = services;
//#endregion
//#region #nitro/virtual/public-assets-data
var public_assets_data_default = {
	"/favicon.ico": {
		"type": "image/vnd.microsoft.icon",
		"etag": "\"4f95-3RXc3p2mhEAs1WBwaIvE0Y0uu0Y\"",
		"mtime": "2026-07-18T01:37:58.904Z",
		"size": 20373,
		"path": "../public/favicon.ico"
	},
	"/assets/badge-BaINqAjR.js": {
		"type": "text/javascript; charset=utf-8",
		"etag": "\"b8e-7e5QTiFj1rS5VrxCo4sMF0k70mo\"",
		"mtime": "2026-07-19T02:11:38.944Z",
		"size": 2958,
		"path": "../public/assets/badge-BaINqAjR.js"
	},
	"/assets/card-Bedc-CYZ.js": {
		"type": "text/javascript; charset=utf-8",
		"etag": "\"41c-BGk9tWjclsJS78HcTrjqqTX2HoM\"",
		"mtime": "2026-07-19T02:11:38.948Z",
		"size": 1052,
		"path": "../public/assets/card-Bedc-CYZ.js"
	},
	"/assets/copilot-Byv6DNKR.js": {
		"type": "text/javascript; charset=utf-8",
		"etag": "\"16db-keQUpiLWlu0Gd3jAhDPqOrTzhBM\"",
		"mtime": "2026-07-19T02:11:38.948Z",
		"size": 5851,
		"path": "../public/assets/copilot-Byv6DNKR.js"
	},
	"/assets/dist-cWPVLn7b.js": {
		"type": "text/javascript; charset=utf-8",
		"etag": "\"2db6-fe2b+12gdjbpiy5BUf7qxjBsHEw\"",
		"mtime": "2026-07-19T02:11:38.948Z",
		"size": 11702,
		"path": "../public/assets/dist-cWPVLn7b.js"
	},
	"/assets/dropdown-menu-COqY-lxZ.js": {
		"type": "text/javascript; charset=utf-8",
		"etag": "\"6551-2Aa9DhwnPDwwzCajvjlCWqaKrK4\"",
		"mtime": "2026-07-19T02:11:38.948Z",
		"size": 25937,
		"path": "../public/assets/dropdown-menu-COqY-lxZ.js"
	},
	"/assets/react-dom-BGozS2fx.js": {
		"type": "text/javascript; charset=utf-8",
		"etag": "\"dda-0MZBIJvXSnBp/LkUj2JpcVxRM3E\"",
		"mtime": "2026-07-19T02:11:38.952Z",
		"size": 3546,
		"path": "../public/assets/react-dom-BGozS2fx.js"
	},
	"/assets/materials-CBkvMoz0.js": {
		"type": "text/javascript; charset=utf-8",
		"etag": "\"25b-yyZMJtkobrF51PoP3gtOimRzZvQ\"",
		"mtime": "2026-07-19T02:11:38.952Z",
		"size": 603,
		"path": "../public/assets/materials-CBkvMoz0.js"
	},
	"/assets/index-oVx5f8RJ.js": {
		"type": "text/javascript; charset=utf-8",
		"etag": "\"77e87-Z3ukbCymVtu19Us0Y9ihJMp5Gmo\"",
		"mtime": "2026-07-19T02:11:38.944Z",
		"size": 491143,
		"path": "../public/assets/index-oVx5f8RJ.js"
	},
	"/assets/jsx-runtime-C27Mmbu5.js": {
		"type": "text/javascript; charset=utf-8",
		"etag": "\"2157-K7z7JulAsA1EGRDTmPYOvz5HqGU\"",
		"mtime": "2026-07-19T02:11:38.952Z",
		"size": 8535,
		"path": "../public/assets/jsx-runtime-C27Mmbu5.js"
	},
	"/assets/materials._materialId._plantId-C1qZHjsS.js": {
		"type": "text/javascript; charset=utf-8",
		"etag": "\"210f-4nG4KQbhTzewzZVFMTb1yGZrH6U\"",
		"mtime": "2026-07-19T02:11:38.952Z",
		"size": 8463,
		"path": "../public/assets/materials._materialId._plantId-C1qZHjsS.js"
	},
	"/assets/sparkles-DxgKaJxh.js": {
		"type": "text/javascript; charset=utf-8",
		"etag": "\"1e3-pxr//cyfty4K0KMq+qTmWVQCqoc\"",
		"mtime": "2026-07-19T02:11:38.957Z",
		"size": 483,
		"path": "../public/assets/sparkles-DxgKaJxh.js"
	},
	"/assets/routes-BePkEVEY.js": {
		"type": "text/javascript; charset=utf-8",
		"etag": "\"665f8-EIDEH2kTKzjGit56sMpYbacowsU\"",
		"mtime": "2026-07-19T02:11:38.957Z",
		"size": 419320,
		"path": "../public/assets/routes-BePkEVEY.js"
	},
	"/assets/recommendations-Zq6m9cBq.js": {
		"type": "text/javascript; charset=utf-8",
		"etag": "\"4276-oPuS31j7JLAkKENs8UTk6gyksNE\"",
		"mtime": "2026-07-19T02:11:38.952Z",
		"size": 17014,
		"path": "../public/assets/recommendations-Zq6m9cBq.js"
	},
	"/assets/styles-DA_UkWLZ.css": {
		"type": "text/css; charset=utf-8",
		"etag": "\"1590b-1xU8IS5ER3Gmz1+ADfk217nsWuY\"",
		"mtime": "2026-07-19T02:11:38.959Z",
		"size": 88331,
		"path": "../public/assets/styles-DA_UkWLZ.css"
	},
	"/logo.png": {
		"type": "image/png",
		"etag": "\"116a7d-iZ1AcQ8unVZvtMPE8dQOkdo0820\"",
		"mtime": "2026-07-18T01:37:58.992Z",
		"size": 1141373,
		"path": "../public/logo.png"
	}
};
//#endregion
//#region #nitro/virtual/public-assets
var publicAssetBases = {};
function isPublicAssetURL(id = "") {
	if (public_assets_data_default[id]) return true;
	for (const base in publicAssetBases) if (id.startsWith(base)) return true;
	return false;
}
//#endregion
//#region node_modules/nitro/dist/runtime/internal/route-rules.mjs
var headers = ((m) => function headersRouteRule(event) {
	for (const [key, value] of Object.entries(m.options || {})) event.res.headers.set(key, value);
});
//#endregion
//#region #nitro/virtual/routing
var findRouteRules = /* @__PURE__ */ (() => {
	const $0 = [{
		name: "headers",
		route: "/assets/**",
		handler: headers,
		options: { "cache-control": "public, max-age=31536000, immutable" }
	}];
	return (m, p) => {
		let r = [];
		if (p.charCodeAt(p.length - 1) === 47) p = p.slice(0, -1) || "/";
		let s = p.split("/");
		if (s.length > 1) {
			if (s[1] === "assets") r.unshift({
				data: $0,
				params: { "_": s.slice(2).join("/") }
			});
		}
		return r;
	};
})();
var _lazy_fWzbUP = defineLazyEventHandler(() => import("./_chunks/ssr-renderer.mjs"));
var findRoute = /* @__PURE__ */ (() => {
	const data = {
		route: "/**",
		handler: _lazy_fWzbUP
	};
	return ((_m, p) => {
		return {
			data,
			params: { "_": p.slice(1) }
		};
	});
})();
[].filter(Boolean);
//#endregion
//#region node_modules/nitro/dist/runtime/internal/error/prod.mjs
var errorHandler = (error, event) => {
	const res = defaultHandler(error, event);
	return new FastResponse(typeof res.body === "string" ? res.body : JSON.stringify(res.body, null, 2), res);
};
function defaultHandler(error, event) {
	const unhandled = error.unhandled ?? !HTTPError.isError(error);
	const { status = 500, statusText = "" } = unhandled ? {} : error;
	if (status === 404) {
		const url = event.url || new URL(event.req.url);
		const baseURL = "/";
		if (/^\/[^/]/.test(baseURL) && !url.pathname.startsWith(baseURL)) return {
			status: 302,
			headers: new Headers({ location: `${baseURL}${url.pathname.slice(1)}${url.search}` })
		};
	}
	const headers = new Headers(unhandled ? {} : error.headers);
	headers.set("content-type", "application/json; charset=utf-8");
	return {
		status,
		statusText,
		headers,
		body: {
			error: true,
			...unhandled ? {
				status,
				unhandled: true
			} : typeof error.toJSON === "function" ? error.toJSON() : {
				status,
				statusText,
				message: error.message
			}
		}
	};
}
//#endregion
//#region #nitro/virtual/error-handler
var errorHandlers = [errorHandler];
async function error_handler_default(error, event) {
	for (const handler of errorHandlers) try {
		const response = await handler(error, event, { defaultHandler });
		if (response) return response;
	} catch (error) {
		console.error(error);
	}
}
//#endregion
//#region #nitro/virtual/app
function createNitroApp() {
	const captureError = (error, errorCtx) => {
		if (errorCtx?.event) {
			const errors = errorCtx.event.req.context?.nitro?.errors;
			if (errors) errors.push({
				error,
				context: errorCtx
			});
		}
	};
	const h3App = createH3App({ onError(error, event) {
		return error_handler_default(error, event);
	} });
	let appHandler = (req) => {
		req.context ||= {};
		req.context.nitro = req.context.nitro || { errors: [] };
		return h3App.fetch(req);
	};
	return {
		fetch: appHandler,
		h3: h3App,
		hooks: void 0,
		captureError
	};
}
function createH3App(config) {
	const h3App = new H3Core(config);
	h3App["~findRoute"] = (event) => findRoute(event.req.method, event.url.pathname);
	h3App["~getMiddleware"] = (event, route) => {
		const pathname = event.url.pathname;
		const method = event.req.method;
		const middleware = [];
		const routeRules = getRouteRules(method, pathname);
		event.context.routeRules = routeRules?.routeRules;
		if (routeRules?.routeRuleMiddleware.length) middleware.push(...routeRules.routeRuleMiddleware);
		if (route?.data?.middleware?.length) middleware.push(...route.data.middleware);
		return middleware;
	};
	return h3App;
}
//#endregion
//#region node_modules/nitro/dist/runtime/internal/app.mjs
var APP_ID = "default";
function useNitroApp() {
	let instance = useNitroApp._instance;
	if (instance) return instance;
	instance = useNitroApp._instance = createNitroApp();
	globalThis.__nitro__ = globalThis.__nitro__ || {};
	globalThis.__nitro__[APP_ID] = instance;
	return instance;
}
function useNitroHooks() {
	const nitroApp = useNitroApp();
	const hooks = nitroApp.hooks;
	if (hooks) return hooks;
	return nitroApp.hooks = new HookableCore();
}
function getRouteRules(method, pathname) {
	const m = findRouteRules(method, pathname);
	if (!m?.length) return { routeRuleMiddleware: [] };
	const routeRules = {};
	for (const layer of m) for (const rule of layer.data) {
		const currentRule = routeRules[rule.name];
		if (currentRule) {
			if (rule.options === false) {
				delete routeRules[rule.name];
				continue;
			}
			if (typeof currentRule.options === "object" && typeof rule.options === "object") currentRule.options = {
				...currentRule.options,
				...rule.options
			};
			else currentRule.options = rule.options;
			currentRule.route = rule.route;
			currentRule.params = {
				...currentRule.params,
				...layer.params
			};
		} else if (rule.options !== false) routeRules[rule.name] = {
			...rule,
			params: layer.params
		};
	}
	const middleware = [];
	const orderedRules = Object.values(routeRules).sort((a, b) => (a.handler?.order || 0) - (b.handler?.order || 0));
	for (const rule of orderedRules) {
		if (rule.options === false || !rule.handler) continue;
		middleware.push(rule.handler(rule));
	}
	return {
		routeRules,
		routeRuleMiddleware: middleware
	};
}
//#endregion
//#region node_modules/nitro/dist/presets/cloudflare/runtime/_module-handler.mjs
function createHandler(hooks) {
	const nitroApp = useNitroApp();
	const nitroHooks = useNitroHooks();
	return {
		async fetch(request, env, context) {
			globalThis.__env__ = env;
			augmentReq(request, {
				env,
				context
			});
			const ctxExt = {};
			const url = new URL(request.url);
			if (hooks.fetch) {
				const res = await hooks.fetch(request, env, context, url, ctxExt);
				if (res) return res;
			}
			return await nitroApp.fetch(request);
		},
		scheduled(controller, env, context) {
			globalThis.__env__ = env;
			context.waitUntil(nitroHooks.callHook("cloudflare:scheduled", {
				controller,
				env,
				context
			}) || Promise.resolve());
		},
		email(message, env, context) {
			globalThis.__env__ = env;
			context.waitUntil(nitroHooks.callHook("cloudflare:email", {
				message,
				event: message,
				env,
				context
			}) || Promise.resolve());
		},
		queue(batch, env, context) {
			globalThis.__env__ = env;
			context.waitUntil(nitroHooks.callHook("cloudflare:queue", {
				batch,
				event: batch,
				env,
				context
			}) || Promise.resolve());
		},
		tail(traces, env, context) {
			globalThis.__env__ = env;
			context.waitUntil(nitroHooks.callHook("cloudflare:tail", {
				traces,
				env,
				context
			}) || Promise.resolve());
		},
		trace(traces, env, context) {
			globalThis.__env__ = env;
			context.waitUntil(nitroHooks.callHook("cloudflare:trace", {
				traces,
				env,
				context
			}) || Promise.resolve());
		}
	};
}
function augmentReq(cfReq, ctx) {
	const req = cfReq;
	req.ip = cfReq.headers.get("cf-connecting-ip") || void 0;
	req.runtime ??= { name: "cloudflare" };
	req.runtime.cloudflare = {
		...req.runtime.cloudflare,
		...ctx
	};
	req.waitUntil = ctx.context?.waitUntil.bind(ctx.context);
}
//#endregion
//#region node_modules/nitro/dist/presets/cloudflare/runtime/cloudflare-module.mjs
var cloudflare_module_default = createHandler({ fetch(cfRequest, env, context, url) {
	if (env.ASSETS && isPublicAssetURL(url.pathname)) return env.ASSETS.fetch(cfRequest);
} });
//#endregion
export { cloudflare_module_default as default };
