import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	build: {
		rollupOptions: {
			external: ['canvas']
		},
		target: 'esnext'
	},
	optimizeDeps: {
		include: [
			'svelte',
			'svelte/internal',
			'svelte/store',
			'@sveltejs/kit',
			'pdfjs-dist'
		],
		force: true,
		esbuildOptions: {
			target: 'esnext'
		}
	},
	server: {
		fs: {
			strict: false
		},
		watch: {
			usePolling: true
		}
	}
});
