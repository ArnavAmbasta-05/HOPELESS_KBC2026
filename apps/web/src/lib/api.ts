/**
 * Global API URL resolver for local dev and cloud deployment.
 * Connects directly to the live KoreX FastAPI cloud backend on Render in production.
 */
const PRODUCTION_API_URL = "https://korex-api-tuqp.onrender.com";

export function getApiUrl(path: string): string {
  const cleanPath = path.startsWith("/") ? path : `/${path}`;

  // 1. Explicit Vite env variable
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl && typeof envUrl === "string" && envUrl.trim() !== "") {
    const baseUrl = envUrl.startsWith("http://") || envUrl.startsWith("https://")
      ? envUrl.replace(/\/+$/, "")
      : `https://${envUrl.replace(/\/+$/, "")}`;
    return `${baseUrl}${cleanPath}`;
  }

  // 2. Production browser context (hosted on onrender.com, vercel.app, etc.)
  if (
    typeof window !== "undefined" &&
    window.location.hostname !== "localhost" &&
    window.location.hostname !== "127.0.0.1"
  ) {
    return `${PRODUCTION_API_URL}${cleanPath}`;
  }

  // 3. Local dev fallback (relative URL proxied by Vite dev server)
  return cleanPath;
}
