import { fileURLToPath, URL } from "url";

import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

const hash = Math.floor(Math.random() * 90000) + 100000;

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  build: {
    rollupOptions: {
      output: {
        entryFileNames: `[name].` + hash + `.js`,
        chunkFileNames: `[name].` + hash + `.js`,
        assetFileNames: `[name].` + hash + `.[ext]`
      }
    }
  }
});
