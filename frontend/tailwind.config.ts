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
        // Solid PicPay / Fintech Green
        primary: {
          50: "#e8faf1",
          100: "#c7f4dc",
          200: "#95ebbf",
          300: "#57dc9b",
          400: "#26c77b",
          500: "#11C76F", // Main PicPay green (solid, vibrant)
          600: "#0ea85d",
          700: "#0e854c",
          800: "#10693f",
          900: "#0f5635",
          950: "#06301d",
        },
        picpay: "#11C76F",
        // Neutral black & gray surfaces (pure black, zero green tint in background)
        dark: {
          bg: "#000000",
          card: "#141414",
          cardHover: "#1b1b1b",
          cardSecondary: "#202020",
          border: "#262626",
          text: "#FFFFFF",
          muted: "#8E8E93",
        },
        light: {
          bg: "#F5F6F8",
          card: "#FFFFFF",
          cardHover: "#F0F2F5",
          cardSecondary: "#E9ECEF",
          border: "#E5E7EB",
          text: "#111827",
          muted: "#6B7280",
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
