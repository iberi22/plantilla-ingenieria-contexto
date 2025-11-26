<script lang="ts">
  import type { Project } from '../types';
  import { PROJECTS } from '../constants';

  export let project: Project;

  $: relatedProjects = PROJECTS
      .filter(p => p.id !== project.id) // Exclude current
      .map(p => {
        let score = 0;
        if (p.category === project.category) score += 3; // High weight for category
        const sharedTags = p.tags.filter(tag => project.tags.includes(tag));
        score += sharedTags.length; // weight for tags
        return { ...p, score };
      })
      .filter(p => p.score > 0) // Must have some relevance
      .sort((a, b) => b.score - a.score)
      .slice(0, 3); // Take top 3
</script>

<div class="group relative border-l-2 border-white/10 pl-8 py-4 transition-all hover:border-emerald-500/50">
  <!-- Timeline Dot -->
  <div class="absolute -left-[5px] top-6 h-2.5 w-2.5 rounded-full bg-bone-dark/20 ring-4 ring-[#121212] transition-colors group-hover:bg-emerald-500"></div>

  <div class="flex flex-col md:flex-row gap-6 md:items-start">
    <!-- Meta Column -->
    <div class="w-full md:w-48 flex-shrink-0 pt-1">
      <div class="text-xs font-mono text-emerald-500/80 mb-1 uppercase tracking-wider">
        {project.publishDate || 'Recent'}
      </div>
      <div class="text-[10px] text-bone-dark/40 uppercase tracking-widest font-bold">
        by {project.author || 'BestOfOS'}
      </div>
      <div class="mt-3 inline-block px-2 py-1 bg-white/5 rounded text-[10px] text-bone-dark/60">
        {project.category}
      </div>
    </div>

    <!-- Content Column -->
    <div class="flex-grow">
      <h2 class="text-2xl md:text-3xl font-bold text-bone mb-3 group-hover:text-white transition-colors flex items-center gap-3">
         <span class="text-2xl opacity-80">{project.logo}</span>
         {project.name}
      </h2>

      <div class="prose prose-invert prose-sm max-w-none text-bone-dark/70 mb-4 font-sans leading-relaxed">
        <p>{project.longContent || project.description}</p>
      </div>

      <div class="flex items-center gap-4 border-t border-white/5 pt-4 mt-4">
         <div class="flex items-center gap-1.5 text-xs font-mono text-bone-dark/50">
            <span class="text-emerald-400">★</span>
            {project.insights.stars.toLocaleString()}
         </div>
         <div class="flex items-center gap-1.5 text-xs font-mono text-bone-dark/50">
            <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            {project.insights.lastCommit}
         </div>

         <a href={project.url} target="_blank" rel="noreferrer" class="ml-auto text-xs font-bold uppercase tracking-widest text-bone hover:text-emerald-400 transition-colors flex items-center gap-1">
           Read Repo <span class="text-lg leading-3">›</span>
         </a>
      </div>

      <!-- Related Projects Section -->
      {#if relatedProjects.length > 0}
        <div class="mt-6 pt-4 border-t border-dashed border-white/5">
          <h4 class="text-[10px] uppercase tracking-widest text-bone-dark/30 font-bold mb-3">
            Related Projects
          </h4>
          <div class="flex flex-wrap gap-3">
            {#each relatedProjects as rel (rel.id)}
              <a
                href={rel.url}
                target="_blank"
                rel="noreferrer"
                class="flex items-center gap-2 text-xs text-bone-dark/60 hover:text-emerald-300 transition-colors bg-white/5 px-3 py-1.5 rounded border border-transparent hover:border-emerald-500/20 hover:bg-white/10"
              >
                <span class="opacity-70">{rel.logo}</span>
                <span>{rel.name}</span>
              </a>
            {/each}
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>
