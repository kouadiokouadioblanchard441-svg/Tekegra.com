import path from "node:path";
import express, { type Express } from "express";
import cors from "cors";
import helmet from "helmet";
import rateLimit from "express-rate-limit";
import pinoHttp from "pino-http";
import router from "./routes/index.js";
import { logger } from "./lib/logger.js";

const app: Express = express();
// The production bundle is plesk-deployment/dist/index.cjs. Resolve the
// frontend relative to the launched entrypoint so the same Express process
// serves both the API and the compiled React application.
const entrypointDir = process.argv[1]
  ? path.dirname(path.resolve(process.argv[1]))
  : process.cwd();
const clientDist = path.resolve(entrypointDir, "..", "client-dist");

const allowedOrigins = (process.env.CORS_ORIGINS ?? process.env.DOMAIN_URL ?? "")
  .split(",")
  .map((origin) => origin.trim())
  .filter(Boolean);

app.disable("x-powered-by");
app.set("trust proxy", 1);
app.use(helmet({ crossOriginResourcePolicy: { policy: "cross-origin" } }));
app.use(
  pinoHttp({
    logger,
    serializers: {
      req: (req) => ({
        id: req.id,
        method: req.method,
        url: req.url?.split("?")[0],
      }),
      res: (res) => ({ statusCode: res.statusCode }),
    },
  }),
);
app.use(
  cors(
    allowedOrigins.length
      ? {
          origin: (origin, callback) => {
            if (!origin || allowedOrigins.includes(origin)) {
              callback(null, true);
            } else {
              callback(new Error("CORS origin is not allowed"));
            }
          },
          credentials: false,
        }
      : { origin: false },
  ),
);
app.use(express.json({ limit: "1mb" }));
app.use(express.urlencoded({ extended: true, limit: "1mb" }));

app.get("/readyz", (_req, res) => res.json({ status: "ok" }));
app.use(
  "/api/admin/login",
  rateLimit({
    windowMs: 15 * 60 * 1000,
    limit: 10,
    standardHeaders: "draft-8",
    legacyHeaders: false,
    message: { error: "Too many login attempts. Try again later." },
  }),
);
app.use("/api", router);

app.use(express.static(clientDist, { index: false, maxAge: "1d" }));
app.get("*splat", (_req, res) => {
  res.sendFile(path.join(clientDist, "index.html"));
});

app.use((error: Error, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
  logger.error({ err: error }, "Unhandled request error");
  if (!res.headersSent) res.status(500).json({ error: "Internal server error" });
});

export default app;