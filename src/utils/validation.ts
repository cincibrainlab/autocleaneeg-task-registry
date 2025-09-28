import { z } from "zod";
import type { PublishRequest } from "../types";

const NAME_PATTERN = /^[A-Z][A-Za-z0-9_]*$/;
const CATEGORY_PATTERN = /^[a-z0-9]+(?:[-_][a-z0-9]+)*$/;
const MAX_PYTHON_LENGTH = 40_000;
const FORBIDDEN_IMPORTS = ["os", "sys", "subprocess", "socket", "requests", "shutil"];

export const publishSchema = z.object({
  name: z
    .string()
    .trim()
    .min(3, "Name must be at least 3 characters")
    .max(64, "Name must be 64 characters or fewer")
    .regex(NAME_PATTERN, "Name must be PascalCase (letters, digits, underscores; start with capital letter)"),
  category: z
    .string()
    .trim()
    .min(3, "Category must be at least 3 characters")
    .max(48, "Category must be 48 characters or fewer")
    .regex(CATEGORY_PATTERN, "Category must be lowercase letters, digits, hyphen or underscore"),
  python: z
    .string()
    .min(50, "Python content appears blank")
    .max(MAX_PYTHON_LENGTH, `Python content exceeds ${MAX_PYTHON_LENGTH} characters`),
  summary: z
    .string()
    .trim()
    .max(500, "Summary must be 500 characters or fewer")
    .optional(),
  authorGithub: z
    .string()
    .trim()
    .regex(/^[A-Za-z0-9-]{1,39}$/u, "Invalid GitHub username")
    .optional(),
  dryRun: z.boolean().optional(),
});

export type ValidatedPublishRequest = z.infer<typeof publishSchema>;

export function validatePythonTask(
  payload: Pick<PublishRequest, "name" | "python">,
): string[] {
  const issues: string[] = [];
  const { name, python } = payload;

  const normalized = python.replace(/\r\n?/g, "\n");

  if (!new RegExp(`class\\s+${name}\\s*\\(.*Task`, "m").test(normalized)) {
    issues.push(`Python class definition "class ${name}(Task):" not found`);
  }

  if (!/from\s+autoclean?\.core\.task\s+import\s+Task/.test(normalized)) {
    issues.push("Expected import 'from autoclean.core.task import Task'");
  }

  if (!/config\s*=\s*{/.test(normalized)) {
    issues.push("Expected a 'config = {...}' block");
  }

  const docstringMatch = normalized.trimStart().startsWith('"""');
  if (!docstringMatch) {
    issues.push("Missing module docstring describing the task");
  }

  const forbiddenMatches = new Set<string>();
  const lines = normalized.split("\n");
  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line || line.startsWith("#")) continue;
    for (const mod of FORBIDDEN_IMPORTS) {
      if (
        line === `import ${mod}` ||
        line.startsWith(`import ${mod}.`) ||
        line.startsWith(`from ${mod} `)
      ) {
        forbiddenMatches.add(mod);
      }
    }
  }
  if (forbiddenMatches.size > 0) {
    issues.push(`Forbidden imports detected: ${Array.from(forbiddenMatches).join(", ")}`);
  }

  return issues;
}

export function makeFilePath(category: string, name: string): string {
  return `tasks/${category}/${name}.py`;
}

export function makeBranchName(name: string): string {
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
  const slug = name.replace(/[^A-Za-z0-9]+/g, "-").replace(/-+/g, "-").toLowerCase();
  return `wizard/${slug}-${timestamp}`;
}
