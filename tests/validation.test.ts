import { describe, expect, it } from "vitest";
import { publishSchema, validatePythonTask, makeFilePath, makeBranchName } from "../src/utils/validation";

describe("publishSchema", () => {
  it("accepts a valid payload", () => {
    const python = [
      '"""Resting example"""',
      "from autoclean.core.task import Task",
      "",
      "config = {}",
      "",
      "class RestingEyesFocus(Task):",
      "    pass",
    ].join("\n");
    const payload = {
      name: "RestingEyesFocus",
      category: "resting",
      python,
      summary: "Test summary",
      authorGithub: "drpedapati",
    };
    const result = publishSchema.safeParse(payload);
    expect(result.success).toBe(true);
  });

  it("rejects invalid names", () => {
    const payload = {
      name: "invalid-name",
      category: "resting",
      python: "class X(Task): pass",
    };
    const result = publishSchema.safeParse(payload);
    expect(result.success).toBe(false);
  });
});

describe("validatePythonTask", () => {
  const basePython = [
    '"""Demo task"""',
    "from autoclean.core.task import Task",
    "",
    "config = {}",
    "",
    "class DemoTask(Task):",
    "    pass",
  ].join("\n");
  const base = {
    name: "DemoTask",
    python: basePython,
  };

  it("returns no issues for valid content", () => {
    expect(validatePythonTask(base)).toEqual([]);
  });

  it("detects missing class definition", () => {
    const issues = validatePythonTask({ ...base, python: base.python.replace("class DemoTask(Task):", "") });
    expect(issues.some((issue) => issue.includes("class DemoTask"))).toBe(true);
  });

  it("detects forbidden imports", () => {
    const python = `${base.python}\nimport os`;
    const issues = validatePythonTask({ ...base, python });
    expect(issues.some((issue) => issue.includes("Forbidden imports"))).toBe(true);
  });
});

describe("helpers", () => {
  it("builds python file paths", () => {
    expect(makeFilePath("resting", "DemoTask")).toBe("tasks/resting/DemoTask.py");
  });

  it("builds branch names", () => {
    const branch = makeBranchName("DemoTask");
    expect(branch.startsWith("wizard/demotask-")).toBe(true);
  });
});
