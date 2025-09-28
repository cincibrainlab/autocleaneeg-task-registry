import { withCors } from "./cors";
import type { Env } from "../types";

export function jsonResponse(
  data: unknown,
  request: Request,
  env: Env,
  init: ResponseInit = {},
): Response {
  const body = JSON.stringify(data, null, 2);
  const headers = new Headers(init.headers);
  if (!headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json; charset=utf-8");
  }
  return withCors(new Response(body, { ...init, headers }), request, env);
}

export function errorResponse(
  request: Request,
  env: Env,
  status: number,
  message: string,
  details?: unknown,
): Response {
  return jsonResponse({ error: message, details }, request, env, { status });
}
