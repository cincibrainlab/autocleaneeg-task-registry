import { Octokit } from "@octokit/core";
import { createAppAuth } from "@octokit/auth-app";
import type { Env } from "../types";

const REGISTRY_PATH = "registry.json";

const encoder = new TextEncoder();
const decoder = new TextDecoder();

function encodeBase64(input: string): string {
  const bytes = encoder.encode(input);
  let binary = "";
  for (let i = 0; i < bytes.length; i += 1) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

function decodeBase64(input: string): string {
  const sanitized = input.replace(/\s+/g, "");
  const binary = atob(sanitized);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  return decoder.decode(bytes);
}

export interface RegistryFile {
  sha: string;
  content: string;
  data: {
    version: number;
    commit: string;
    tasks: Array<{ name: string; path: string; summary?: string }>;
    [key: string]: unknown;
  };
}

export interface RepoContext {
  owner: string;
  repo: string;
}

export function getRepoContext(env: Env): RepoContext {
  if (!env.REGISTRY_OWNER || !env.REGISTRY_REPO) {
    throw new Error("Registry owner/repo environment variables are not set");
  }
  return { owner: env.REGISTRY_OWNER, repo: env.REGISTRY_REPO };
}

function decodePrivateKey(input?: string): string {
  if (!input) {
    throw new Error("GITHUB_PRIVATE_KEY is not configured");
  }
  const trimmed = input.trim();
  if (trimmed.startsWith("-----BEGIN")) {
    return trimmed;
  }
  return decodeBase64(trimmed);
}

export function createOctokit(env: Env): Octokit {
  const appId = env.GITHUB_APP_ID;
  const installationId = env.GITHUB_INSTALLATION_ID;
  if (!appId || !installationId) {
    throw new Error("GitHub App credentials are missing (app ID or installation ID)");
  }
  const privateKey = decodePrivateKey(env.GITHUB_PRIVATE_KEY);
  return new Octokit({
    authStrategy: createAppAuth,
    auth: {
      appId,
      privateKey,
      installationId: Number.parseInt(installationId, 10),
    },
    userAgent: "taskwizard-registry-backend/1.0",
  });
}

export async function fetchRegistryFile(
  octokit: Octokit,
  env: Env,
): Promise<RegistryFile> {
  const { owner, repo } = getRepoContext(env);
  const response = await octokit.request("GET /repos/{owner}/{repo}/contents/{path}", {
    owner,
    repo,
    path: REGISTRY_PATH,
  });

  if (!('content' in response.data) || typeof response.data.content !== "string") {
    throw new Error("Unexpected registry.json response payload");
  }

  const fileData = response.data as {
    content: string;
    encoding: string;
    sha: string;
  };

  const content = decodeBase64(fileData.content);
  const data = JSON.parse(content) as RegistryFile["data"];

  return {
    sha: fileData.sha,
    content,
    data,
  };
}

export async function getBranchSha(
  octokit: Octokit,
  env: Env,
  branch: string,
): Promise<string> {
  const { owner, repo } = getRepoContext(env);
  const response = await octokit.request("GET /repos/{owner}/{repo}/git/ref/{ref}", {
    owner,
    repo,
    ref: `heads/${branch}`,
  });
  return response.data.object.sha;
}

export async function createBranch(
  octokit: Octokit,
  env: Env,
  newBranch: string,
  baseBranch: string,
): Promise<void> {
  const baseSha = await getBranchSha(octokit, env, baseBranch);
  const { owner, repo } = getRepoContext(env);
  await octokit.request("POST /repos/{owner}/{repo}/git/refs", {
    owner,
    repo,
    ref: `refs/heads/${newBranch}`,
    sha: baseSha,
  });
}

export async function createOrUpdateFile(
  octokit: Octokit,
  env: Env,
  params: {
    path: string;
    content: string;
    message: string;
    branch: string;
    sha?: string;
  },
): Promise<void> {
  const { owner, repo } = getRepoContext(env);
  await octokit.request("PUT /repos/{owner}/{repo}/contents/{path}", {
    owner,
    repo,
    path: params.path,
    message: params.message,
    branch: params.branch,
    content: encodeBase64(params.content),
    sha: params.sha,
  });
}

export async function createPullRequest(
  octokit: Octokit,
  env: Env,
  params: {
    title: string;
    head: string;
    base: string;
    body: string;
    draft?: boolean;
  },
): Promise<{ url: string; number: number }> {
  const { owner, repo } = getRepoContext(env);
  const response = await octokit.request("POST /repos/{owner}/{repo}/pulls", {
    owner,
    repo,
    title: params.title,
    head: params.head,
    base: params.base,
    body: params.body,
    draft: params.draft ?? false,
  });
  return { url: response.data.html_url, number: response.data.number };
}

export function formatRegistryJson(data: RegistryFile["data"]): string {
  return `${JSON.stringify(data, null, 2)}\n`;
}
