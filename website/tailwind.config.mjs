/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
	darkMode: 'class',
	theme: {
		extend: {
			fontFamily: {
				mono: ['"Fira Code"', 'monospace'],
				sans: ['"Fira Code"', 'monospace'],
			},
			colors: {
				bone: {
					DEFAULT: '#F5F5DC', // Updated from Design System
					dark: '#E8E8C0',    // Updated from Design System
				},
				dark: {
					bg: '#121212',      // Updated from Design System
					surface: '#1E1E1E', // Updated from Design System
					surfaceDark: '#0A0A0A', // Updated from Design System
				},
				accent: '#10B981', // Emerald-500
				error: '#F87171',  // Red-400
			},
			animation: {
				'marquee': 'marquee var(--duration) linear infinite',
				'fade-in-up': 'fadeInUp 0.8s ease-out forwards',
				'border-beam': 'borderBeam 4s linear infinite',
				'blob': 'blob 7s infinite',
				'slide-down': 'slideDown 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards',
			},
			keyframes: {
				marquee: {
					'0%': { transform: 'translateX(0)' },
					'100%': { transform: 'translateX(calc(-100% - var(--gap)))' },
				},
				fadeInUp: {
					'0%': { opacity: '0', transform: 'translateY(20px)', filter: 'blur(10px)' },
					'100%': { opacity: '1', transform: 'translateY(0)', filter: 'blur(0)' },
				},
				borderBeam: {
					'100%': { 'offset-distance': '100%' },
				},
				blob: {
					'0%': { transform: 'translate(0px, 0px) scale(1)' },
					'33%': { transform: 'translate(30px, -50px) scale(1.1)' },
					'66%': { transform: 'translate(-20px, 20px) scale(0.9)' },
					'100%': { transform: 'translate(0px, 0px) scale(1)' },
				},
				slideDown: {
					'0%': { transform: 'translateY(-100%)', opacity: '0' },
					'100%': { transform: 'translateY(0)', opacity: '1' },
				}
			}
		},
	},
	plugins: [],
}
