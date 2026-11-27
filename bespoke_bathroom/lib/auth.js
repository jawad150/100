// Sign-in for the studio. Research runs on the Claude plan signed in to Claude Code on
// this computer (`claude auth login`), through the Claude Agent SDK. No API key is used.
import os from "node:os";
import path from "node:path";
import fs from "node:fs";
import { execFile } from "node:child_process";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);

// On Windows, PowerShell often blocks claude.ps1, so point people at claude.cmd.
export const SIGN_IN_COMMAND = process.platform === "win32" ? "claude.cmd auth login" : "claude auth login";

// Claude Code runs here: an empty folder, so no project files, settings or CLAUDE.md apply.
export const WORK_DIR = path.join(os.tmpdir(), "bespoke-bathroom-studio");
fs.mkdirSync(WORK_DIR, { recursive: true });

// The environment for Claude Code: API keys, auth tokens and Anthropic Console profiles are
// removed, so the only credential it can find is the Claude plan login.
export function planEnv() {
  const env = { ...process.env, CLAUDE_AGENT_SDK_CLIENT_APP: "bespoke-bathroom-social-studio/1.0" };
  for (const k of ["ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_PROFILE", "ANTHROPIC_BASE_URL"]) delete env[k];
  env.ANTHROPIC_CONFIG_DIR = path.join(WORK_DIR, "no-console-profile");
  return env;
}

// The Claude Code binary that ships with the Agent SDK for this platform.
function bundledClaude() {
  try {
    const pkg = require.resolve(`@anthropic-ai/claude-agent-sdk-${process.platform}-${process.arch}/package.json`);
    const bin = path.join(path.dirname(pkg), process.platform === "win32" ? "claude.exe" : "claude");
    return fs.existsSync(bin) ? bin : null;
  } catch {
    return null;
  }
}

let cached = null;

// Asks Claude Code whether it is signed in to a Claude plan. Cached for 20 seconds.
export async function authStatus({ fresh = false } = {}) {
  if (!fresh && cached && Date.now() - cached.at < 20000) return cached.value;
  const bin = bundledClaude();
  const value = await new Promise((resolve) => {
    if (!bin) return resolve({ signedIn: false, source: null, plan: null });
    execFile(bin, ["auth", "status"], { env: planEnv(), cwd: WORK_DIR, timeout: 20000, windowsHide: true }, (err, stdout) => {
      try {
        const s = JSON.parse(stdout);
        const onPlan = s.loggedIn && s.authMethod && !/api.?key|console/i.test(s.authMethod);
        resolve({ signedIn: !!onPlan, source: onPlan ? "claude" : null, plan: s.subscriptionType ?? null });
      } catch {
        resolve({ signedIn: false, source: null, plan: null });
      }
    });
  });
  cached = { at: Date.now(), value };
  return value;
}
