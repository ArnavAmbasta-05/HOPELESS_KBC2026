import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    proxy: {
      // All backend routers (including weather) are under /api/v1/*.
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: true,
    rollupOptions: {
      output: {
        // Split heavy vendors into their own chunks for faster first paint.
        manualChunks: {
          three: ["three", "@react-three/fiber", "@react-three/drei"],
          leaflet: ["leaflet", "maplibre-gl"],
          charts: ["recharts"],
          motion: ["framer-motion"],
          vendor: ["react", "react-dom", "react-router-dom", "@tanstack/react-query"],
        },
      },
    },
  },
});
