/**
 * Global API URL resolver for local dev and cloud deployment.
 * Resolves VITE_API_URL if configured; otherwise falls back to window.location origin (or relative path).
 */
export function getApiUrl(path: string): string {
  const envUrl = import.meta.env.VITE_API_URL;
  if (!envUrl) {
    return path;
  }
  const baseUrl = envUrl.startsWith("http://") || envUrl.startsWith("https://")
    ? envUrl.replace(/\/+$/, "")
    : `https://${envUrl.replace(/\/+$/, "")}`;
  const cleanPath = path.startsWith("/") ? path : `/${path}`;
  return `${baseUrl}${cleanPath}`;
}
