export type Env = {
  REGISTRY_OWNER: string;
  REGISTRY_REPO: string;
  REGISTRY_DEFAULT_BRANCH: string;
  ALLOWED_ORIGINS?: string;
  CACHE_TTL_SECONDS?: string;
  GITHUB_APP_ID?: string;
  GITHUB_CLIENT_ID?: string;
  GITHUB_CLIENT_SECRET?: string;
  GITHUB_PRIVATE_KEY?: string;
  GITHUB_INSTALLATION_ID?: string;
  SESSION_SECRET?: string;
};

export type PublishRequest = {
  name: string;
  category: string;
  python: string;
  summary?: string;
  authorGithub?: string;
  dryRun?: boolean;
};
