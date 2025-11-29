import { defineConfig } from 'astro/config';
import tailwind from "@astrojs/tailwind";
import svelte from "@astrojs/svelte";
import sitemap from "@astrojs/sitemap";

// https://astro.build/config
export default defineConfig({
  site: 'https://iberi22.github.io',
  base: '/bestof-opensorce',
  integrations: [
    tailwind(),
    svelte(),
    sitemap({
      changefreq: 'daily',
      priority: 0.7,
      lastmod: new Date(),
      filter: (page) => !page.includes('/api-pricing'), // Exclude API pricing from sitemap priority
    })
  ],
  // SEO optimizations
  compressHTML: true,
  build: {
    inlineStylesheets: 'auto',
  },
});
