/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
          950: '#082f49',
        },
        navy: {
          800: '#0e1726',
          850: '#0b1320',
          900: '#080d1a',
          950: '#04070e',
        },
        cyber: {
          cyan: '#06b6d4',
          indigo: '#6366f1',
          purple: '#a855f7',
          emerald: '#10b981',
          amber: '#f59e0b',
          rose: '#f43f5e',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow-cyan': 'glowCyan 2s ease-in-out infinite alternate',
      },
      keyframes: {
        glowCyan: {
          '0%': { boxShadow: '0 0 5px rgba(6, 182, 212, 0.2), 0 0 10px rgba(6, 182, 212, 0.2)' },
          '100%': { boxShadow: '0 0 15px rgba(6, 182, 212, 0.6), 0 0 25px rgba(6, 182, 212, 0.4)' },
        }
      }
    },
  },
  plugins: [],
}
