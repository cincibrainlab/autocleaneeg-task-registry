import type { Env } from "../types";
import { withCors } from "../utils/cors";
import { errorResponse } from "../utils/responses";
import { generatePythonTask } from "../utils/pythonGenerator";

export async function handleExportConfig(
  request: Request,
  env: Env,
  ctx: ExecutionContext,
): Promise<Response> {
  try {
    // Parse the request body
    const body = await request.json() as any;

    if (!body.taskName || !body.config) {
      return errorResponse(request, env, 400, "Missing taskName or config in request body");
    }

    // Generate the Python file content
    const pythonContent = generatePythonTask(body.taskName, body.config);

    // Return the Python file as a download
    const response = new Response(pythonContent, {
      status: 200,
      headers: {
        "Content-Type": "text/x-python; charset=utf-8",
        "Content-Disposition": `attachment; filename="${body.taskName}.py"`,
        "Cache-Control": "no-cache",
      },
    });

    return withCors(response, request, env);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Failed to export configuration";
    return errorResponse(request, env, 500, message);
  }
}