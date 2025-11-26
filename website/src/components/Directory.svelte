<script lang="ts">
  import { ProjectCategory, type Project } from '../types';
  import ProjectCard from './ProjectCard.svelte';
  import BlogCard from './BlogCard.svelte';
  import { fade } from 'svelte/transition';

  export let projects: Project[];

  let viewMode: 'directory' | 'blog' = 'directory';
  let selectedCategory: ProjectCategory | 'All' = 'All';
  let searchQuery = '';

  // Listen to view mode changes from window/header if we want global control,
  // but for now let's control it here or pass it down.
  // Actually, the Header is outside. We might need a store or just handle it locally for this section.
  // Let's add a local toggle in the sticky bar as well, or assume the prop is passed.
  // For simplicity in this demo, I'll add the toggle in the sticky bar too.

  $: filteredProjects = projects.filter(p => {
    const matchesCategory = selectedCategory === 'All' || p.category === selectedCategory;
    const matchesSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          p.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          p.tags.some(t => t.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesCategory && matchesSearch;
  });

  const categories = Object.values(ProjectCategory);
</script>

<div class="sticky top-16 z-40 backdrop-blur-lg bg-[#121212]/80 border-b border-white/5 py-4 px-6 mb-8">
  <div class="max-w-7xl mx-auto flex flex-col md:flex-row gap-4 justify-between items-center">

    <!-- Search -->
    <div class="relative w-full md:w-64">
      <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-bone-dark/40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
      <input
        type="text"
        bind:value={searchQuery}
        placeholder="Search projects..."
        class="w-full bg-white/5 border border-transparent focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/50 rounded-full py-2 pl-10 pr-4 text-sm text-bone placeholder-bone-dark/20 outline-none transition-all"
      />
    </div>

    <!-- Categories -->
    <div class="flex gap-2 overflow-x-auto pb-2 md:pb-0 w-full md:w-auto no-scrollbar">
      {#each categories as category}
        <button
          on:click={() => selectedCategory = category}
          class={`whitespace-nowrap px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border transition-all ${selectedCategory === category ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/50' : 'text-bone-dark/40 border-white/5 hover:border-white/20 hover:text-bone'}`}
        >
          {category}
        </button>
      {/each}
    </div>

    <!-- View Toggle (Mobile/Desktop) -->
    <div class="flex items-center bg-white/5 rounded-full p-1 border border-white/5">
       <button
         on:click={() => viewMode = 'directory'}
         class={`p-2 rounded-full transition-all ${viewMode === 'directory' ? 'bg-bone text-black' : 'text-bone-dark/40 hover:text-bone'}`}
         title="Grid View"
       >
         <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg>
       </button>
       <button
         on:click={() => viewMode = 'blog'}
         class={`p-2 rounded-full transition-all ${viewMode === 'blog' ? 'bg-bone text-black' : 'text-bone-dark/40 hover:text-bone'}`}
         title="List View"
       >
         <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" /></svg>
       </button>
    </div>
  </div>
</div>

<div class="max-w-7xl mx-auto px-6 pb-20 min-h-[50vh]">
  {#if viewMode === 'directory'}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" in:fade={{ duration: 300 }}>
      {#each filteredProjects as project (project.id)}
        <ProjectCard {project} />
      {/each}
    </div>
  {:else}
    <div class="flex flex-col gap-8 max-w-4xl mx-auto" in:fade={{ duration: 300 }}>
      {#each filteredProjects as project (project.id)}
        <BlogCard {project} />
      {/each}
    </div>
  {/if}

  {#if filteredProjects.length === 0}
    <div class="text-center py-20">
      <p class="text-bone-dark/40 text-xl font-light">No projects found matching your criteria.</p>
      <button
        on:click={() => { searchQuery = ''; selectedCategory = 'All'; }}
        class="mt-4 text-emerald-400 hover:underline text-sm uppercase tracking-wider"
      >
        Clear Filters
      </button>
    </div>
  {/if}
</div>

<style>
  .no-scrollbar::-webkit-scrollbar {
    display: none;
  }
  .no-scrollbar {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
</style>
