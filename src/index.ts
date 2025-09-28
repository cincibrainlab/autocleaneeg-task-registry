import { Router } from "itty-router";
import { handleLibraryIndex } from "./routes/library";
import { handlePublish } from "./routes/publish";
import { handleOptions } from "./utils/cors";
import { errorResponse } from "./utils/responses";
import type { Env } from "./types";

const router = Router();

router.options("*", (request: Request, env: Env) => handleOptions(request, env));
router.get("/library/index", (request: Request, env: Env, ctx: ExecutionContext) => handleLibraryIndex(request, env, ctx));
router.post("/publish", (request: Request, env: Env, ctx: ExecutionContext) => handlePublish(request, env, ctx));
router.all("*", (request: Request, env: Env) =>
  errorResponse(request, env, 404, "Not found"),
);

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    try {
      // Pass all parameters to router.fetch for itty-router v5
      const response = await router.fetch(request, env, ctx);
      if (!response) {
        return errorResponse(request, env, 404, "Not found");
      }
      return response;
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unexpected error";
      return errorResponse(request, env, 500, message);
    }
  },
};
