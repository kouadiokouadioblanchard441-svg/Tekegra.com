/**
 * Vercel serverless entry-point.
 * Wraps the Express app so every request to /api/* is handled here.
 */
import app from "../artifacts/api-server/src/app.js";

export default app;
