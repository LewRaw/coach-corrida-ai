import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./context/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#090d16",
        surface: "#111827",
        "surface-card": "#161f33",
        "surface-card-hover": "#1c2742",
        "surface-border": "#222f4c",
        primary: {
          50: "#f0fdfa",
          100: "#ccfbf1",
          500: "#0284c7",
          600: "#0369a1",
          700: "#075985",
        },
        brand: {
          emerald: "#10b981",
          teal: "#14b8a6",
          amber: "#f59e0b",
          rose: "#f43f5e",
          blue: "#3b82f6",
        },
      },
      fontFamily: {
        sans: ["system-ui", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
      },
    },
  },
  plugins: [],
};
export default config;
