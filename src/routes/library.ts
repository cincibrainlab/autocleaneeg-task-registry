import type { Env } from "../types";
import { withCors } from "../utils/cors";
import { errorResponse } from "../utils/responses";

const GITHUB_RAW_BASE = "https://raw.githubusercontent.com";

function ttlSeconds(env: Env): number {
  const raw = env.CACHE_TTL_SECONDS;
  const parsed = raw ? Number.parseInt(raw, 10) : Number.NaN;
  return Number.isFinite(parsed) && parsed > 0 ? parsed : 300;
}

function buildCacheKey(request: Request, branch: string): Request {
  const url = new URL(request.url);
  url.pathname = "/__cache/library-index";
  url.search = `?branch=${encodeURIComponent(branch)}`;
  return new Request(url.toString(), { method: "GET" });
}

export async function handleLibraryIndex(
  request: Request,
  env: Env,
  ctx: ExecutionContext,
): Promise<Response> {
  if (!env.REGISTRY_OWNER || !env.REGISTRY_REPO) {
    return errorResponse(request, env, 500, "Registry owner/repo are not configured");
  }

  const branch = env.REGISTRY_DEFAULT_BRANCH || "main";
  const registryUrl = `${GITHUB_RAW_BASE}/${env.REGISTRY_OWNER}/${env.REGISTRY_REPO}/${branch}/registry.json`;
  const cacheKey = buildCacheKey(request, branch);
  const cache = await caches.open("registry-index");
  const cached = await cache.match(cacheKey);
  if (cached) {
    return withCors(cached, request, env);
  }

  const upstream = await fetch(registryUrl, {
    cf: {
      cacheEverything: true,
      cacheTtl: ttlSeconds(env),
    },
    headers: {
      Accept: "application/json",
      "User-Agent": "taskwizard-registry-backend/1.0",
    },
  });

  if (!upstream.ok) {
    return errorResponse(
      request,
      env,
      502,
      "Failed to fetch registry from GitHub",
      { status: upstream.status, statusText: upstream.statusText },
    );
  }

  const body = await upstream.text();
  const response = new Response(body, {
    status: 200,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": `public, max-age=${ttlSeconds(env)}`,
      "X-Registry-Source": registryUrl,
    },
  });

  ctx.waitUntil(cache.put(cacheKey, response.clone()));
  return withCors(response, request, env);
}
