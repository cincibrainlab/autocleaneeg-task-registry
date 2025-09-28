import type { Env } from "../types";

const DEFAULT_ALLOWED = ["*"];

function parseAllowedOrigins(env: Env): string[] {
  const raw = env.ALLOWED_ORIGINS?.trim();
  if (!raw) return DEFAULT_ALLOWED;
  return raw.split(",").map((entry) => entry.trim()).filter(Boolean);
}

export function withCors(response: Response, request: Request, env: Env): Response {
  const clone = response.clone();
  const allowed = parseAllowedOrigins(env);
  const origin = request.headers.get("Origin") || "";
  const headers = new Headers(clone.headers);
  const allowOrigin = allowed.includes("*")
    ? "*"
    : allowed.includes(origin)
      ? origin
      : allowed.length === 0
        ? "*"
        : allowed[0];
  headers.set("Access-Control-Allow-Origin", allowOrigin);
  headers.set("Access-Control-Allow-Headers", "Content-Type, Authorization");
  headers.set("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
  headers.set("Access-Control-Allow-Credentials", "true");
  headers.append("Vary", "Origin");
  return new Response(clone.body, {
    status: clone.status,
    statusText: clone.statusText,
    headers,
  });
}

export function handleOptions(request: Request, env: Env): Response {
  const allowed = parseAllowedOrigins(env);
  const origin = request.headers.get("Origin") || "";
  const headers = new Headers();
  const allowOrigin = allowed.includes("*")
    ? "*"
    : allowed.includes(origin)
      ? origin
      : allowed.length === 0
        ? "*"
        : allowed[0];
  headers.set("Access-Control-Allow-Origin", allowOrigin);
  headers.set("Access-Control-Allow-Headers", "Content-Type, Authorization");
  headers.set("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
  headers.set("Access-Control-Max-Age", "86400");
  headers.append("Vary", "Origin");
  return new Response(null, { status: 204, headers });
}
