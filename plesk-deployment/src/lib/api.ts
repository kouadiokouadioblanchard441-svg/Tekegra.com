/**
 * API client configuration.
 *
 * API client configuration for the same-origin Plesk deployment.
 */
import {
  setBaseUrl,
  setAuthTokenGetter,
} from "@/lib/api-client-react";

// The Node server serves both the SPA and /api, so relative URLs work on
// localhost, a Plesk domain, and behind a reverse proxy without configuration.
setBaseUrl("");

// Inject auth token from localStorage on every request
setAuthTokenGetter(() => localStorage.getItem("admin_token"));

export type ErrorType<E> = E & { message: string };
export type BodyType<B> = B;
