import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./context/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Vibrant Emerald & Mint Green palette as the primary athletic focus
        primary: {
          50: "#ecfdf5",
          100: "#d1fae5",
          200: "#a7f3d0",
          300: "#6ee7b7",
          400: "#34d399",
          500: "#10b981", // Main accent green
          600: "#059669",
          700: "#047857",
          800: "#065f46",
          900: "#064e3b",
          950: "#022c22",
        },
        // Neutral background & surface tokens
        surface: {
          light: "#ffffff",
          dark: "#121815",
          cardLight: "#f8fafc",
          cardDark: "#17201c",
          borderLight: "#e2e8f0",
          borderDark: "#23312a",
        },
        brand: {
          emerald: "#10b981",
          teal: "#14b8a6",
          mint: "#34d399",
          amber: "#f59e0b",
          rose: "#f43f5e",
        },
      },
      fontFamily: {
        sans: ["var(--font-plus-jakarta)", "system-ui", "-apple-system", "sans-serif"],
      },
      borderRadius: {
        "2xl": "1.25rem",
        "3xl": "1.75rem",
      },
    },
  },
  plugins: [],
};
export default config;
