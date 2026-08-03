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
  startedAt?: string;
  lastExit?: {
    code: number | null;
    signal: NodeJS.Signals | null;
    at: string;
  };
  lastError?: string;
}

let runtime: TelegramBotRuntime = { state: "stopped" };

export function setTelegramBotRuntime(
  update: Partial<TelegramBotRuntime>,
): void {
  runtime = { ...runtime, ...update };
}

export function getTelegramBotRuntime(): TelegramBotRuntime {
  return { ...runtime, lastExit: runtime.lastExit && { ...runtime.lastExit } };
}