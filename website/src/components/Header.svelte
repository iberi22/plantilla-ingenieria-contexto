<script lang="ts">
	const darkMode = true; // Default to true as per design system
	// In a real app, we might want to toggle this on <html> class.
	// Since we are "Dark Mode Only" per design system ("High contrast, dark mode only"),
	// maybe we don't need a toggle?
	// "Aesthetic: Cyber-Minimalism. High contrast, dark mode only".
	// So I will remove the dark mode toggle and just keep the structure.

	export let viewMode: "directory" | "blog" = "directory";


  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();

  function setViewMode(mode: 'directory' | 'blog') {
    viewMode = mode;
    dispatch('viewChange', mode);
    // Also dispatch a custom event for other components to listen if needed,
    // or we can bind viewMode in the parent.
  }
</script>

<header class="fixed top-0 left-0 right-0 z-[60] backdrop-blur-xl bg-[#121212]/70 border-b border-white/5 h-16 flex items-center px-6 justify-between supports-[backdrop-filter]:bg-[#121212]/60">
  <div class="flex items-center gap-2 group cursor-pointer" on:click={() => window.scrollTo({top:0, behavior:'smooth'})}>
    <div class="w-5 h-5 bg-bone rounded-sm rotate-45 group-hover:rotate-90 transition-transform duration-500"></div>
    <span class="font-bold text-lg tracking-tight text-bone font-mono">BestOf<span class="opacity-40">OS</span></span>
  </div>

  <!-- View Mode Switcher (Only visible if we are on home page, but for now keep it) -->
  <div class="absolute left-1/2 -translate-x-1/2 hidden md:flex items-center p-1 bg-white/5 rounded-full border border-white/5">
      <button
        on:click={() => setViewMode('directory')}
        class={`px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider transition-all ${viewMode === 'directory' ? 'bg-bone text-black shadow-lg' : 'text-bone-dark/60 hover:text-bone'}`}
      >
        Directory
      </button>
      <button
        on:click={() => setViewMode('blog')}
        class={`px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider transition-all ${viewMode === 'blog' ? 'bg-bone text-black shadow-lg' : 'text-bone-dark/60 hover:text-bone'}`}
      >
        Blog
      </button>
  </div>

  <div class="flex items-center gap-6">
    <a href="https://github.com/iberi22/bestof-opensorce" target="_blank" rel="noreferrer" class="text-xs font-mono text-bone-dark/60 hover:text-bone transition-colors hidden md:block uppercase tracking-wider">
      Contribute
    </a>
    <!-- Dark mode toggle removed as per "Dark Mode Only" spec -->
  </div>
</header>
