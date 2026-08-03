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
  if (runtime.statusFile && runtime.pid) {
    try {
      const parsed = JSON.parse(
        readFileSync(runtime.statusFile, "utf8"),
      ) as TelegramBotRuntime["botStatus"];
      if (parsed?.pid === runtime.pid) {
        botStatus = parsed;
      }
    } catch {
      // The file may not exist while start.sh is installing dependencies.
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