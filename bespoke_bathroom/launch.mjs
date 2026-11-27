// One-click launcher for the Social Studio.
//   node launch.mjs             open the studio, starting the server in the background if needed
//   node launch.mjs --stop      stop a server this launcher started
//   node launch.mjs --shortcut  put a "Social Studio" shortcut on the desktop (Windows)
// Optional: STUDIO_CHROME_PROFILE="Profile 4" in .env opens a specific Chrome profile.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawn, execFile } from "node:child_process";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
try {
  process.loadEnvFile(path.join(here, ".env"));
} catch {
  /* no .env file: fine */
}
const PORT = Number(process.env.PORT) || 4321;
const URL_ = `http://localhost:${PORT}`;
const pidFile = path.join(here, "data", "server.pid");
const logFile = path.join(here, "data", "server.log");
const isWin = process.platform === "win32";

async function isUp() {
  try {
    const res = await fetch(`${URL_}/api/status`, { signal: AbortSignal.timeout(1500) });
    return res.ok;
  } catch {
    return false;
  }
}

async function waitUntilUp(seconds) {
  for (let i = 0; i < seconds * 2; i++) {
    if (await isUp()) return true;
    await new Promise((r) => setTimeout(r, 500));
  }
  return false;
}

function startServer() {
  if (!fs.existsSync(path.join(here, "node_modules"))) {
    // First run on a new computer: install the packages once, visibly logged.
    const npm = isWin ? "npm.cmd" : "npm";
    const r = spawn(npm, ["install", "--no-fund", "--no-audit"], { cwd: here, stdio: "ignore", shell: isWin });
    return new Promise((resolve) => r.on("exit", () => resolve(startServer())));
  }
  fs.mkdirSync(path.dirname(logFile), { recursive: true });
  const out = fs.openSync(logFile, "a");
  const child = spawn(process.execPath, ["server.js"], {
    cwd: here,
    detached: true,
    windowsHide: true,
    stdio: ["ignore", out, out],
  });
  fs.writeFileSync(pidFile, String(child.pid));
  child.unref();
}

function chromePath() {
  const candidates = isWin
    ? [
        path.join(process.env["PROGRAMFILES"] || "C:\\Program Files", "Google\\Chrome\\Application\\chrome.exe"),
        path.join(process.env["PROGRAMFILES(X86)"] || "C:\\Program Files (x86)", "Google\\Chrome\\Application\\chrome.exe"),
        path.join(process.env.LOCALAPPDATA || "", "Google\\Chrome\\Application\\chrome.exe"),
      ]
    : process.platform === "darwin"
      ? ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"]
      : ["/usr/bin/google-chrome", "/usr/bin/google-chrome-stable"];
  return candidates.find((p) => p && fs.existsSync(p)) ?? null;
}

function openBrowser() {
  const chrome = chromePath();
  if (chrome) {
    const args = process.env.STUDIO_CHROME_PROFILE ? [`--profile-directory=${process.env.STUDIO_CHROME_PROFILE}`, URL_] : [URL_];
    spawn(chrome, args, { detached: true, stdio: "ignore" }).unref();
  } else if (isWin) {
    spawn("cmd", ["/c", "start", "", URL_], { detached: true, stdio: "ignore", windowsHide: true }).unref();
  } else {
    spawn(process.platform === "darwin" ? "open" : "xdg-open", [URL_], { detached: true, stdio: "ignore" }).unref();
  }
}

function stopServer() {
  try {
    const pid = Number(fs.readFileSync(pidFile, "utf8"));
    process.kill(pid);
    fs.rmSync(pidFile, { force: true });
    console.log("Social Studio stopped.");
  } catch {
    console.log("No Social Studio server started by the launcher is running.");
  }
}

function makeShortcut() {
  if (!isWin) return console.log("The desktop shortcut is for Windows. On a Mac, double-click start.command.");
  const desktop = path.join(os.homedir(), "Desktop");
  const lnk = path.join(desktop, "Social Studio.lnk");
  const vbs = path.join(here, "Social Studio.vbs");
  const icon = path.join(here, "public", "assets", "studio.ico");
  const ps = [
    "$s = (New-Object -ComObject WScript.Shell).CreateShortcut($env:LNK)",
    "$s.TargetPath = \"$env:WINDIR\\System32\\wscript.exe\"",
    "$s.Arguments = '\"' + $env:VBS + '\"'",
    "$s.WorkingDirectory = $env:HERE",
    "$s.IconLocation = $env:ICON",
    "$s.Description = 'Open the Bespoke Bathroom UK Social Studio'",
    "$s.Save()",
  ].join("; ");
  execFile(
    "powershell.exe",
    ["-NoProfile", "-NonInteractive", "-Command", ps],
    { env: { ...process.env, LNK: lnk, VBS: vbs, HERE: here, ICON: icon }, windowsHide: true },
    (err) => console.log(err ? `Could not create the shortcut: ${err.message}` : `Shortcut created: ${lnk}`)
  );
}

const arg = process.argv[2];
if (arg === "--stop") stopServer();
else if (arg === "--shortcut") makeShortcut();
else {
  if (!(await isUp())) {
    await startServer();
    if (!(await waitUntilUp(isWin ? 60 : 45))) {
      console.log(`The studio did not start. See ${logFile}`);
      process.exit(1);
    }
  }
  openBrowser();
}
