<script lang="ts">
  import { onMount } from 'svelte';
  import type { Project } from '../types';
  import { analyzeRepoWithGemini } from '../services/geminiService';
  import { BASE_URL } from '../constants';

  export let project: Project;

  let cardRef: HTMLDivElement;
  let aiAnalysis: string | null = null;
  let loading = false;

  function handleMouseMove(e: MouseEvent) {
    if (!cardRef) return;
    const rect = cardRef.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    cardRef.style.setProperty('--mouse-x', `${x}px`);
    cardRef.style.setProperty('--mouse-y', `${y}px`);
  }

  async function handleAnalyzeClick(e: MouseEvent) {
    e.stopPropagation();
    if (aiAnalysis) return;

    loading = true;
    aiAnalysis = await analyzeRepoWithGemini(project.name, project.description);
    loading = false;
  }
</script>

<!-- svelte-ignore a11y-no-static-element-interactions -->
<div
  bind:this={cardRef}
  on:mousemove={handleMouseMove}
  class="flashlight-card group relative overflow-hidden rounded-xl border border-white/10 bg-white/5 p-6 transition-all duration-500 hover:scale-[1.01] hover:border-transparent"
>
  <div class="flashlight-border" />

  <div class="relative z-10 flex flex-col h-full justify-between">
    <div>
      <div class="flex items-start justify-between mb-4">
        <div class="flex items-center gap-3">
          <span class="text-3xl filter grayscale group-hover:grayscale-0 transition-all duration-300">
            {project.logo}
          </span>
          <div>
            <h3 class="text-xl font-bold tracking-tight text-bone group-hover:text-white transition-colors">
              <a href={`${BASE_URL}/blog/${project.id}`} class="hover:underline focus:outline-none">
                {project.name}
              </a>
            </h3>
            <span class="text-xs font-medium text-bone-dark/50 uppercase tracking-wider">
              {project.category}
            </span>
          </div>
        </div>
        <div class="flex items-center gap-1 text-xs text-bone-dark/70 bg-white/5 px-2 py-1 rounded">
          <span>★</span>
          <span>{project.insights.stars.toLocaleString()}</span>
        </div>
      </div>

      <p class="text-sm text-bone-dark/80 mb-6 leading-relaxed">
        {project.description}
      </p>

      <div class="space-y-3 mb-6">
        <div class="text-xs flex justify-between border-b border-white/5 pb-2">
          <span class="text-white/40">Issues</span>
          <span class="text-bone-dark">{project.insights.openIssues} open ({project.insights.seriousIssuesCount} critical)</span>
        </div>
        <div class="text-xs flex justify-between border-b border-white/5 pb-2">
          <span class="text-white/40">Last Commit</span>
          <span class="text-bone-dark">{project.insights.lastCommit}</span>
        </div>
      </div>
    </div>

    <div class="mt-auto space-y-2">
      <!-- AI Insight Button -->
      {#if aiAnalysis}
        <div class="bg-emerald-900/20 border border-emerald-500/20 p-3 rounded-lg animate-fade-in-up">
          <p class="text-xs text-emerald-100/90 font-mono">
            <span class="font-bold text-emerald-400">AI INSIGHT:</span> {aiAnalysis}
          </p>
        </div>
      {:else}
         <button
            on:click={handleAnalyzeClick}
            disabled={loading}
            class="w-full text-xs font-mono py-2 border border-dashed border-white/20 text-white/50 hover:bg-white/5 hover:text-white hover:border-white/40 transition-all rounded flex items-center justify-center gap-2"
         >
            {loading ? 'ANALYZING...' : 'GENERATE AI INSIGHTS'}
         </button>
      {/if}

       <!-- Link to Post -->
       <a href={`${BASE_URL}/blog/${project.id}`} class="block w-full text-center text-xs font-bold uppercase tracking-widest text-bone-dark/60 hover:text-emerald-400 transition-colors py-1">
          Read Full Post →
       </a>
    </div>
  </div>
</div>

<style>
  .flashlight-card {
    --mouse-x: 0px;
    --mouse-y: 0px;
  }

  .flashlight-border {
    position: absolute;
    inset: 0;
    z-index: 1;
    pointer-events: none;
    border-radius: inherit;
    padding: 1px; /* Border width */
    background: radial-gradient(
      600px circle at var(--mouse-x) var(--mouse-y),
      rgba(255, 255, 255, 0.4),
      transparent 40%
    );
    -webkit-mask:
      linear-gradient(#fff 0 0) content-box,
      linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    opacity: 0;
    transition: opacity 0.3s;
  }

  .flashlight-card:hover .flashlight-border {
    opacity: 1;
  }
</style>
