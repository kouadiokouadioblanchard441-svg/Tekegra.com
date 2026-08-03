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

// Keep the API URL configurable for local development and same-origin hosting.
const BASE_URL = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}`
  : "";

// Set the base URL only when the API is hosted on a separate origin.
if (BASE_URL) {
  setBaseUrl(BASE_URL);
}

// Inject auth token from localStorage on every request
setAuthTokenGetter(() => localStorage.getItem("admin_token"));

export type ErrorType<E> = E & { message: string };
export type BodyType<B> = B;
