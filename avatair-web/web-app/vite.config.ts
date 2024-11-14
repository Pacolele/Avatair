import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/dist/config.js';
import path from 'path';

export default defineConfig({
    plugins: [sveltekit()],
    test: {
        // Adjust the pattern to correctly match your test files
        include: ['src//*.test.js', 'src//.spec.js', 'src/**/.test.ts', 'src/*/.spec.ts']
    }
});

