import { readFileSync } from "node:fs";

export type TelegramBotState =
  | "disabled"
  | "starting"
  | "running"
  | "exited"
  | "missing"
  | "stopped";

export interface TelegramBotRuntime {
  state: TelegramBotState;
  pid?: number;
  script?: string;
  statusFile?: string;
  stderrFile?: string;
  startedAt?: string;
  lastExit?: {
    code: number | null;
    signal: NodeJS.Signals | null;
    at: string;
  };
  lastError?: string;
  botStatus?: {
    status?: string;
    pid?: number;
    at?: string;
    botId?: number;
    botUsername?: string;
    botName?: string;
    error?: string;
    stage?: string;
    exitCode?: number;
  };
}

let runtime: TelegramBotRuntime = { state: "stopped" };

export function setTelegramBotRuntime(
  update: Partial<TelegramBotRuntime>,
): void {
  runtime = { ...runtime, ...update };
}

export function getTelegramBotRuntime(): TelegramBotRuntime {
  let botStatus = runtime.botStatus;
  if (runtime.statusFile) {
    try {
      const parsed = JSON.parse(
        readFileSync(runtime.statusFile, "utf8"),
      ) as TelegramBotRuntime["botStatus"];
      // Keep the last shell/Python startup result visible after the child
      // exits. The parent clears runtime.pid in its exit handler, but the
      // status file is exactly what explains a pre-polling failure.
      if (parsed && (!runtime.pid || parsed.pid === runtime.pid)) {
        botStatus = parsed;
      }
    } catch {
      // The file may not exist while start.sh is installing dependencies.
    }
  }
  if (runtime.stderrFile) {
    try {
      const stderr = readFileSync(runtime.stderrFile, "utf8").trim();
      if (stderr) {
        botStatus = {
          ...(botStatus ?? {}),
          status: "failed",
          error: stderr.slice(-4000),
        };
      }
    } catch {
      // The file is created only when the child writes to stderr.
    }
  }
  const state =
    botStatus?.status === "polling"
      ? "running"
      : botStatus?.status === "failed"
        ? "exited"
        : runtime.state;

  return {
    ...runtime,
    state,
    botStatus,
    lastExit: runtime.lastExit && { ...runtime.lastExit },
  };
}

export function recordTelegramBotError(error: string): void {
  const safeError = error.slice(-4000);
  runtime = {
    ...runtime,
    state: "exited",
    lastError: safeError,
    botStatus: {
      ...(runtime.botStatus ?? {}),
      status: "failed",
      error: safeError,
    },
  };
}