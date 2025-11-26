import { defineConfig } from 'astro/config';
import tailwind from "@astrojs/tailwind";
import svelte from "@astrojs/svelte";

// https://astro.build/config
export default defineConfig({
  site: 'https://iberi22.github.io',
  base: '/plantilla-ingenieria-contexto',
  integrations: [tailwind(), svelte()],
});
