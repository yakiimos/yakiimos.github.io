import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
import mdx from '@astrojs/mdx';

import cloudflare from "@astrojs/cloudflare";

export default defineConfig({
  integrations: [
    tailwind(),
    mdx(),
  ],

  adapter: cloudflare()
});