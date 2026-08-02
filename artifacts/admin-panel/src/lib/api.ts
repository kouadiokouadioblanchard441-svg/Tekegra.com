/**
 * API client configuration.
 *
 * The generated hooks (React Query) use customFetch (native fetch) from
 * lib/api-client-react. This file configures the base URL and auth token
 * injection for that client — no axios dependency needed.
 */
import {
  setBaseUrl,
  setAuthTokenGetter,
} from "@workspace/api-client-react";

// Support external API URL for Vercel deployment
const BASE_URL = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}`
  : "";

// Set base URL for the generated client (only needed for cross-origin, e.g. Vercel)
if (BASE_URL) {
  setBaseUrl(BASE_URL);
}

// Inject auth token from localStorage on every request
setAuthTokenGetter(() => localStorage.getItem("admin_token"));

export type ErrorType<E> = E & { message: string };
export type BodyType<B> = B;
