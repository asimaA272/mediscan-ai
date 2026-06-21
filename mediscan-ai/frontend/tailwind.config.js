/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        bg: {
          DEFAULT: "#0A0E14",
          panel: "#10151C",
          elevated: "#161D27",
        },
        accent: {
          cyan: "#22D3EE",
          blue: "#3B82F6",
          green: "#34D399",
          amber: "#FBBF24",
          red: "#F87171",
        },
        line: "#1F2733",
        muted: "#7C8BA1",
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        body: ["'Inter'", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
    },
  },
  plugins: [],
}
