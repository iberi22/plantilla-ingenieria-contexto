# 📝 Project Status & Tasks

## 🚀 Sprint: Tuning & 100% Implementation

**Goal:** Review workflow, enable real data in static web, improve UI, and finalize documentation.

### ✅ Completed Tasks
- [x] **Review Workflow:** Analyzed `scripts/workflow_generate_blog.py` and `website/` structure.
- [x] **Enable Real Data:**
    - Configured Astro Content Collections (`website/src/content/config.ts`).
    - Updated `website/src/pages/index.astro` to fetch real Markdown posts instead of mocks.
    - Updated backend `src/blog_generator/markdown_writer.py` to generate Astro-compatible frontmatter.
- [x] **UI Improvements:**
    - Updated `BlogCard.svelte` to link to internal blog posts (`/blog/[slug]`) instead of external URLs only.
    - Verified `website/src/pages/blog/[...slug].astro` handles rendering.

### 🚧 Pending / In Progress
- [ ] **Data Richness:** The current markdown generator still lacks deep insights (contributors, issues, etc.) in the frontmatter. The `Project` interface expects these.
- [ ] **Visuals:** Image generation is optional/mocked. Need to ensure real images are handled if available.
- [ ] **Styling:** "Fira Code" and "Dark Theme" refinements (per Roadmap) are partially present but could be enhanced.
- [ ] **Categories:** Automatic categorization logic is basic (hardcoded fallback in `index.astro`).

### 📋 Next Steps (Backlog)
1.  **Enhanced Scanner:** Implement `src/scanner/github_scanner.py` improvements to fetch deeper metrics (contributors, releases).
2.  **Category Detection:** Implement intelligent category detection in the backend generator, not just the frontend mapping.
3.  **Search/Filter:** Ensure the search bar in `Directory.svelte` works effectively with the new real data.

---

## 📚 Reference: Blog Enhancement Roadmap (Adapted for Astro)

The original `docs/planning/BLOG_ENHANCEMENT_ROADMAP.md` was written for Jekyll. We have adapted it for Astro:

- **Liquid Tags** -> **Astro Components**
- **_posts** -> **src/content/blog**
- **Frontmatter** -> **src/content/config.ts Schema**

### Current Architecture
- **Frontend:** Astro + Svelte + Tailwind
- **Backend:** Python (Flask/Scripts)
- **Data:** Markdown files in `website/src/content/blog`
