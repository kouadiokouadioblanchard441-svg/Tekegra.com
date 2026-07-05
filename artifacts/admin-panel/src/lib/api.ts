import Axios from "axios";

// Support external API URL for Vercel deployment
const BASE_URL = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api`
  : "/api";

export const axiosInstance = Axios.create({ baseURL: BASE_URL });

// Inject auth token on every request
axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem("admin_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Redirect to /login on 401
axiosInstance.interceptors.response.use(
  (r) => r,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("admin_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export type ErrorType<E> = E & { message: string };
export type BodyType<B> = B;
