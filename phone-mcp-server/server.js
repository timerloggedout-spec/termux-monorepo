#!/usr/bin/env node

/**
 * phone-mcp-server — Turn your Android phone into an MCP server
 *
 * Exposes 18 phone tools (SMS, contacts, camera, location, clipboard, etc.)
 * over HTTP using the Model Context Protocol (MCP). AI assistants like
 * GitHub Copilot CLI, Claude Desktop, and others can connect and control
 * your phone remotely.
 *
 * Requires: Android + Termux + Termux:API app + `pkg install termux-api nodejs-lts`
 *
 * Usage:
 *   node server.js                    # starts on port 3000
 *   node server.js --port 8080        # custom port
 *   node server.js --verbose          # debug logging
 *   PORT=8080 node server.js          # env var port
 *
 * @license MIT
 * @author Hector Rocha <hector@htek.dev>
 * @see https://github.com/htekdev/phone-mcp-server
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import express from "express";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { randomUUID } from "node:crypto";
import os from "node:os";
import { z } from "zod";

const exec = promisify(execFile);

// ---------------------------------------------------------------------------
// Config — CLI args and environment variables
// ---------------------------------------------------------------------------

const args = process.argv.slice(2);
const VERBOSE = args.includes("--verbose") || args.includes("-v");
const PORT =
  parseInt(args.find((_, i, a) => a[i - 1] === "--port") ?? "") ||
  parseInt(process.env.PORT ?? "") ||
  3000;

function log(...msg) {
  console.log(`[phone-mcp]`, ...msg);
}

function debug(...msg) {
  if (VERBOSE) console.log(`[phone-mcp:debug]`, ...msg);
}

// ---------------------------------------------------------------------------
// Termux:API helper
// Runs termux-* commands and returns stdout. All phone interactions go
// through these two functions.
// ---------------------------------------------------------------------------

const TERMUX_TIMEOUT = 30_000; // 30 seconds per command

/**
 * Execute a Termux command and return raw stdout.
 * @param {string} cmd - The termux command (e.g. "termux-sms-send")
 * @param {string[]} args - Command arguments
 * @param {object} opts - Options (timeout override)
 */
async function termux(cmd, args = [], opts = {}) {
  const timeout = opts.timeout ?? TERMUX_TIMEOUT;
  debug(`exec: ${cmd} ${args.join(" ")}`);
  try {
    const { stdout, stderr } = await exec(cmd, args, {
      timeout,
      maxBuffer: 10 * 1024 * 1024, // 10 MB — call logs can be large
    });
    if (stderr && VERBOSE) debug(`stderr: ${stderr}`);
    return stdout.trim();
  } catch (err) {
    const msg = err.stderr?.trim() || err.message;
    throw new Error(`termux command failed: ${cmd} — ${msg}`);
  }
}

/**
 * Execute a Termux command and parse JSON output.
 * Falls back to raw string if output isn't valid JSON.
 */
async function termuxJson(cmd, args = [], opts = {}) {
  const raw = await termux(cmd, args, opts);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return raw;
  }
}

/** MCP text result helper */
function text(content) {
  return {
    content: [
      {
        type: "text",
        text: typeof content === "string" ? content : JSON.stringify(content, null, 2),
      },
    ],
  };
}

/** MCP error result helper */
function err(message) {
  return {
    content: [{ type: "text", text: `Error: ${message}` }],
    isError: true,
  };
}

// ---------------------------------------------------------------------------
// MCP Server — Tool Registration
// Each tool maps to one or more Termux:API commands.
// ---------------------------------------------------------------------------

const server = new McpServer({
  name: "phone-mcp",
  version: "1.0.0",
});

// ---- 1. Send SMS ----

server.tool(
  "send_sms",
  "Send an SMS text message from the phone",
  {
    to: z.string().describe("Phone number to send to (e.g. +15551234567)"),
    message: z.string().describe("Message text to send"),
  },
  async ({ to, message }) => {
    await termux("termux-sms-send", ["-n", to, message]);
    return text(`SMS sent to ${to}`);
  }
);

// ---- 2. Read SMS ----

server.tool(
  "read_sms",
  "Read recent SMS messages from the phone inbox. Note: RCS messages are NOT accessible — only SMS/MMS.",
  {
    limit: z.number().optional().describe("Number of messages to return (default 10)"),
    type: z
      .string()
      .optional()
      .describe("Message type: inbox, sent, draft, all (default: inbox)"),
  },
  async ({ limit, type }) => {
    const cmdArgs = ["-l", String(limit || 10)];
    if (type) cmdArgs.push("-t", type);
    const messages = await termuxJson("termux-sms-list", cmdArgs);
    return text(messages);
  }
);

// ---- 3. Get Contacts ----

server.tool(
  "get_contacts",
  "Get all contacts from the phone. Returns name, number, and email.",
  {},
  async () => {
    const contacts = await termuxJson("termux-contact-list");
    return text(contacts);
  }
);

// ---- 4. Get Location ----

server.tool(
  "get_location",
  "Get current GPS location of the phone",
  {
    provider: z
      .string()
      .optional()
      .describe("Location provider: gps, network, or passive (default: gps)"),
  },
  async ({ provider }) => {
    const cmdArgs = [];
    if (provider) cmdArgs.push("-p", provider);
    const location = await termuxJson("termux-location", cmdArgs, { timeout: 60_000 });
    return text(location);
  }
);

// ---- 5. Get Battery ----

server.tool(
  "get_battery",
  "Get phone battery level, status, and temperature",
  {},
  async () => {
    const battery = await termuxJson("termux-battery-status");
    return text(battery);
  }
);

// ---- 6. Get Clipboard ----

server.tool(
  "get_clipboard",
  "Read the phone's current clipboard content",
  {},
  async () => {
    const content = await termux("termux-clipboard-get");
    return text(content || "(clipboard empty)");
  }
);

// ---- 7. Set Clipboard ----

server.tool(
  "set_clipboard",
  "Set the phone's clipboard content",
  {
    content: z.string().describe("Text to copy to clipboard"),
  },
  async ({ content }) => {
    await termux("termux-clipboard-set", [content]);
    return text("Clipboard set");
  }
);

// ---- 8. Take Photo ----

server.tool(
  "take_photo",
  "Take a photo with the phone camera. Returns the file path of the saved photo.",
  {
    camera: z
      .number()
      .optional()
      .describe("Camera ID: 0 = back camera, 1 = front camera (default: 0)"),
  },
  async ({ camera }) => {
    const filename = `/data/data/com.termux/files/home/photos/photo-${Date.now()}.jpg`;
    await termux("mkdir", ["-p", "/data/data/com.termux/files/home/photos"]);
    const camId = String(camera ?? 0);
    await termux("termux-camera-photo", ["-c", camId, filename], { timeout: 15_000 });
    return text({ message: "Photo taken", path: filename, camera: camId });
  }
);

// ---- 9. Get Call Log ----

server.tool(
  "get_call_log",
  "Get recent call history (incoming, outgoing, missed)",
  {
    limit: z.number().optional().describe("Number of entries to return (default 25)"),
  },
  async ({ limit }) => {
    const cmdArgs = ["-l", String(limit || 25)];
    const calls = await termuxJson("termux-call-log", cmdArgs);
    return text(calls);
  }
);

// ---- 10. Make Call ----

server.tool(
  "make_call",
  "Initiate a phone call to a number (opens the dialer)",
  {
    number: z.string().describe("Phone number to call"),
  },
  async ({ number }) => {
    await termux("termux-telephony-call", [number]);
    return text(`Call initiated to ${number}`);
  }
);

// ---- 11. Get WiFi Info ----

server.tool(
  "get_wifi_info",
  "Get current WiFi connection details (SSID, IP, link speed, etc.)",
  {},
  async () => {
    const info = await termuxJson("termux-wifi-connectioninfo");
    return text(info);
  }
);

// ---- 12. Flashlight ----

server.tool(
  "flashlight",
  "Control the phone flashlight/torch",
  {
    state: z.string().describe("'on' or 'off'"),
  },
  async ({ state }) => {
    await termux("termux-torch", [state === "on" ? "on" : "off"]);
    return text(`Flashlight turned ${state}`);
  }
);

// ---- 13. Vibrate ----

server.tool(
  "vibrate",
  "Make the phone vibrate",
  {
    duration_ms: z
      .number()
      .optional()
      .describe("Vibration duration in milliseconds (default 1000)"),
  },
  async ({ duration_ms }) => {
    await termux("termux-vibrate", ["-d", String(duration_ms || 1000)]);
    return text("Phone vibrated");
  }
);

// ---- 14. Send Notification ----

server.tool(
  "send_notification",
  "Show a notification on the phone",
  {
    title: z.string().optional().describe("Notification title"),
    content: z.string().optional().describe("Notification body text"),
  },
  async ({ title, content }) => {
    const cmdArgs = [];
    if (title) cmdArgs.push("-t", title);
    if (content) cmdArgs.push("-c", content);
    cmdArgs.push("--id", `mcp-${Date.now()}`);
    await termux("termux-notification", cmdArgs);
    return text("Notification sent");
  }
);

// ---- 15. Get Volume ----

server.tool(
  "get_volume",
  "Get current volume levels for all audio streams",
  {},
  async () => {
    const vol = await termuxJson("termux-volume");
    return text(vol);
  }
);

// ---- 16. Set Volume ----

server.tool(
  "set_volume",
  "Set volume for an audio stream",
  {
    stream: z
      .string()
      .optional()
      .describe("Audio stream: ring, notification, music, alarm, call (default: music)"),
    volume: z.number().describe("Volume level (0-15 typical range)"),
  },
  async ({ stream, volume }) => {
    await termux("termux-volume", [stream || "music", String(volume)]);
    return text(`Volume set: ${stream || "music"} → ${volume}`);
  }
);

// ---- 17. Record Audio ----

server.tool(
  "record_audio",
  "Record audio from the phone microphone. Returns the file path.",
  {
    duration_seconds: z
      .number()
      .optional()
      .describe("Recording duration in seconds (default 10, max 300)"),
  },
  async ({ duration_seconds }) => {
    const dur = Math.min(duration_seconds || 10, 300);
    const filename = `/data/data/com.termux/files/home/recordings/recording-${Date.now()}.m4a`;
    await termux("mkdir", ["-p", "/data/data/com.termux/files/home/recordings"]);
    await termux("termux-microphone-record", ["-f", filename, "-l", String(dur)], {
      timeout: (dur + 5) * 1000,
    });
    // termux-microphone-record returns immediately — wait for the recording to finish
    await new Promise((resolve) => setTimeout(resolve, dur * 1000));
    await termux("termux-microphone-record", ["-q"]); // stop recording
    return text({ message: `Recorded ${dur}s of audio`, path: filename });
  }
);

// ---- 18. Device Info (composite) ----

server.tool(
  "device_info",
  "Get comprehensive device info: battery, WiFi, volume, and system details",
  {},
  async () => {
    const [battery, wifi, volume] = await Promise.all([
      termuxJson("termux-battery-status").catch(() => null),
      termuxJson("termux-wifi-connectioninfo").catch(() => null),
      termuxJson("termux-volume").catch(() => null),
    ]);
    const info = {
      hostname: os.hostname(),
      platform: os.platform(),
      arch: os.arch(),
      uptime_hours: Math.round((os.uptime() / 3600) * 10) / 10,
      memory_mb: Math.round(os.freemem() / 1024 / 1024),
      battery,
      wifi,
      volume,
    };
    return text(info);
  }
);

// ---- Bonus: Shell Command (restricted) ----

const BLOCKED_COMMANDS = [
  "rm -rf /",
  "mkfs",
  "dd if=",
  "reboot",
  "shutdown",
  "> /dev/",
  "chmod 777 /",
];

server.tool(
  "shell",
  "Run a shell command on the phone (with safety filters). For quick lookups and diagnostics.",
  {
    command: z.string().describe("Shell command to execute"),
  },
  async ({ command }) => {
    const lower = command.toLowerCase();
    for (const blocked of BLOCKED_COMMANDS) {
      if (lower.includes(blocked)) {
        return err(`Blocked command: contains '${blocked}'`);
      }
    }
    try {
      const { stdout, stderr } = await exec("sh", ["-c", command], {
        timeout: 15_000,
        maxBuffer: 5 * 1024 * 1024,
      });
      const output = [stdout.trim(), stderr.trim()].filter(Boolean).join("\n---stderr---\n");
      return text(output || "(no output)");
    } catch (e) {
      return err(e.message);
    }
  }
);

// ---------------------------------------------------------------------------
// HTTP Transport — Express server with Streamable HTTP
// ---------------------------------------------------------------------------

const app = express();
app.use(express.json());

/** Track active MCP transports by session ID */
const transports = new Map();

// Health check endpoint
app.get("/health", (_req, res) => {
  res.json({
    status: "ok",
    server: "phone-mcp",
    version: "1.0.0",
    uptime: process.uptime(),
    tools: 18,
  });
});

// MCP Streamable HTTP — POST (main RPC endpoint)
app.post("/mcp", async (req, res) => {
  try {
    const sessionId = req.headers["mcp-session-id"];
    let transport;

    if (sessionId && transports.has(sessionId)) {
      transport = transports.get(sessionId);
    } else {
      transport = new StreamableHTTPServerTransport({
        sessionIdGenerator: () => randomUUID(),
        onsessioninitialized: (id) => {
          transports.set(id, transport);
          debug(`Session initialized: ${id}`);
        },
      });

      transport.onclose = () => {
        const sid = [...transports.entries()].find(([, t]) => t === transport)?.[0];
        if (sid) {
          transports.delete(sid);
          debug(`Session closed: ${sid}`);
        }
      };

      await server.connect(transport);
    }

    await transport.handleRequest(req, res, req.body);
  } catch (e) {
    log("Error handling POST /mcp:", e.message);
    if (!res.headersSent) {
      res.status(500).json({ error: e.message });
    }
  }
});

// MCP Streamable HTTP — GET (SSE streaming)
app.get("/mcp", async (req, res) => {
  const sessionId = req.headers["mcp-session-id"];
  if (!sessionId || !transports.has(sessionId)) {
    res.status(400).json({ error: "Missing or invalid session ID" });
    return;
  }
  const transport = transports.get(sessionId);
  await transport.handleRequest(req, res);
});

// MCP Streamable HTTP — DELETE (session cleanup)
app.delete("/mcp", async (req, res) => {
  const sessionId = req.headers["mcp-session-id"];
  if (sessionId && transports.has(sessionId)) {
    const transport = transports.get(sessionId);
    await transport.handleRequest(req, res);
    transports.delete(sessionId);
  } else {
    res.status(404).json({ error: "Session not found" });
  }
});

// ---------------------------------------------------------------------------
// Startup
// ---------------------------------------------------------------------------

function getLocalIP() {
  const interfaces = os.networkInterfaces();
  for (const name of Object.keys(interfaces)) {
    for (const iface of interfaces[name]) {
      if (iface.family === "IPv4" && !iface.internal) {
        return iface.address;
      }
    }
  }
  return "127.0.0.1";
}

app.listen(PORT, "0.0.0.0", () => {
  const ip = getLocalIP();
  log("========================================");
  log(" phone-mcp-server is running!");
  log(`   Local:   http://localhost:${PORT}/mcp`);
  log(`   Network: http://${ip}:${PORT}/mcp`);
  log(`   Health:  http://${ip}:${PORT}/health`);
  log("   Tools:   18 phone tools via Termux:API");
  log("========================================");
  log("");
  log("Add this to your MCP client config:");
  log(
    JSON.stringify(
      {
        mcpServers: {
          phone: {
            url: `http://${ip}:${PORT}/mcp`,
          },
        },
      },
      null,
      2
    )
  );
});

// Graceful shutdown
process.on("SIGINT", () => {
  log("Shutting down...");
  for (const transport of transports.values()) {
    transport.close?.();
  }
  process.exit(0);
});

process.on("SIGTERM", () => {
  log("Shutting down...");
  process.exit(0);
});
