import { Request, Response, NextFunction } from "express";
import jwt from "jsonwebtoken";

const secret = process.env.SESSION_SECRET ?? "";

if (!secret) {
  throw new Error("SESSION_SECRET is required for admin sessions.");
}

export function signToken(): string {
  return jwt.sign({ role: "admin" }, secret, { expiresIn: "30d" });
}

export function verifyToken(token: string): boolean {
  try {
    jwt.verify(token, secret);
    return true;
  } catch {
    return false;
  }
}

export function requireAuth(req: Request, res: Response, next: NextFunction): void {
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
