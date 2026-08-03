import type { NextFunction, Request, Response } from "express";
import jwt from "jsonwebtoken";
import type { SignOptions } from "jsonwebtoken";

const configuredSecret = process.env.SESSION_SECRET;
if (!configuredSecret || configuredSecret.length < 32) {
  throw new Error("SESSION_SECRET must be configured with at least 32 characters.");
}
const secret: string = configuredSecret;
const sessionTtl: SignOptions["expiresIn"] =
  (process.env.SESSION_TTL as SignOptions["expiresIn"] | undefined) ?? "8h";

export function signToken(): string {
  return jwt.sign({ role: "admin" }, secret, {
    expiresIn: sessionTtl,
    issuer: "lucky-jet-ai-bot",
    audience: "admin-panel",
  });
}

export function verifyToken(token: string): boolean {
  try {
    jwt.verify(token, secret, {
      issuer: "lucky-jet-ai-bot",
      audience: "admin-panel",
    });
    return true;
  } catch {
    return false;
  }
}

export function requireAuth(
  req: Request,
  res: Response,
  next: NextFunction,
): void {
  const auth = req.headers.authorization;
  if (!auth?.startsWith("Bearer ")) {
    res.status(401).json({ error: "Missing token" });
    return;
  }
  const token = auth.slice(7);
  if (!verifyToken(token)) {
    res.status(401).json({ error: "Invalid token" });
    return;
  }
  next();
}
