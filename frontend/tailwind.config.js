/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        void: '#050507',
        cyber: '#00F0FF',
        neon: '#FF0055',
        glass: 'rgba(15, 15, 20, 0.65)',
        glassBorder: 'rgba(0, 240, 255, 0.15)',
      },
      boxShadow: {
        'cyber-glow': '0 0 15px rgba(0, 240, 255, 0.4)',
        'neon-glow': '0 0 15px rgba(255, 0, 85, 0.4)',
      }
    },
  },
  plugins: [],
}