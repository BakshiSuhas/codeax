import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}", "./lib/**/*.{js,ts,jsx,tsx}", "./styles/**/*.css"],
  theme: {
    extend: {
      colors: {
        gh: {
          bg: "#010409",
          card: "#0d1117",
          border: "#30363d",
          green: "#238636",
          text: "#c9d1d9",
          heading: "#f0f6fc"
        }
      }
    }
  },
  plugins: []
};

export default config;
