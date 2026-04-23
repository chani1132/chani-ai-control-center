/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        dark: {
          900: "#0d0f14",
          800: "#13151c",
          700: "#1a1d27",
          600: "#222535",
        },
      },
    },
  },
  plugins: [],
};
