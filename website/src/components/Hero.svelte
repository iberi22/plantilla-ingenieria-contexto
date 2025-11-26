<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { HERO_WORDS, PROJECTS } from '../constants';

  let currentCardIndex = 0;
  let isHovering = false;
  let interval: any;

  function startInterval() {
    interval = setInterval(() => {
      if (!isHovering) {
        currentCardIndex = (currentCardIndex + 1) % 3;
      }
    }, 4000);
  }

  onMount(() => {
    startInterval();
  });

  onDestroy(() => {
    clearInterval(interval);
  });

  function nextCard() {
    currentCardIndex = (currentCardIndex + 1) % 3;
  }

  function prevCard() {
    currentCardIndex = currentCardIndex === 0 ? 2 : currentCardIndex - 1;
  }

  const featuredProjects = PROJECTS.slice(0, 3);
  const heroWords = ['THE', 'SOURCE', 'OF', 'OPEN'];
</script>

<section class="relative min-h-[95vh] flex flex-col items-center justify-center overflow-hidden pt-20">

  <!-- Dynamic Background Blobs -->
  <div class="absolute inset-0 overflow-hidden pointer-events-none">
    <div class="absolute top-0 -left-4 w-96 h-96 bg-emerald-500/10 rounded-full mix-blend-screen filter blur-[100px] opacity-20 animate-blob"></div>
    <div class="absolute top-1/4 -right-4 w-96 h-96 bg-purple-500/10 rounded-full mix-blend-screen filter blur-[100px] opacity-20 animate-blob" style="animation-delay: 2s"></div>
    <div class="absolute -bottom-8 left-1/3 w-80 h-80 bg-blue-500/10 rounded-full mix-blend-screen filter blur-[100px] opacity-20 animate-blob" style="animation-delay: 4s"></div>
  </div>

  <!-- Background Clip Animation Grid -->
  <div class="clip-bg-grid">
     {#each Array(12) as _, i}
       <div
        class="clip-col"
        style="animation-delay: {i * 0.05}s"
       />
     {/each}
  </div>

  <div class="relative z-10 w-full max-w-7xl px-6 grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-24 items-center">
    <!-- Left: Text Content -->
    <div class="space-y-10 text-center lg:text-left pt-10 lg:pt-0 relative z-20">
      <div class="inline-flex items-center gap-3 px-4 py-1.5 rounded-full bg-white/5 border border-white/10 text-xs font-medium text-bone animate-fade-in-up hover:bg-white/10 transition-colors cursor-default backdrop-blur-sm" style="animation-delay: 1s">
        <span class="relative flex h-2 w-2">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
        </span>
        <span class="tracking-widest uppercase text-[10px] opacity-80">Live Repository Tracking</span>
      </div>

      <h1 class="text-6xl md:text-8xl font-bold tracking-tighter text-transparent bg-clip-text bg-gradient-to-br from-bone via-bone to-bone-dark/40 leading-[0.9] filter drop-shadow-2xl">
        <!-- Vertical Clip Text Animation -->
        {#each heroWords as word, i}
           <span class="inline-block overflow-hidden align-bottom h-[1.1em] mr-4 last:mr-0">
             <span class="block animate-slide-down" style="animation-delay: {1.2 + (i * 0.1)}s">
               {word}
             </span>
           </span>
        {/each}
      </h1>

      <p class="text-lg md:text-xl text-bone-dark/60 max-w-xl mx-auto lg:mx-0 animate-fade-in-up font-light leading-relaxed" style="animation-delay: 1.8s">
        Curated. Analyzed. Visualized. <br/>
        <span class="text-bone-dark/40">Discover the projects defining the software future.</span>
      </p>

      <div class="flex flex-wrap gap-5 justify-center lg:justify-start animate-fade-in-up items-center" style="animation-delay: 2s">
        <button
          on:click={() => document.getElementById('directory')?.scrollIntoView({ behavior: 'smooth' })}
          class="relative group rounded-full px-8 py-3.5 bg-bone text-black font-bold transition-all hover:scale-105 active:scale-95 shadow-[0_0_20px_rgba(245,245,220,0.1)] hover:shadow-[0_0_30px_rgba(245,245,220,0.3)]"
        >
          <span class="relative z-10">Explore Directory</span>
        </button>

        <!-- Pill button with border beam -->
        <div class="relative rounded-full p-[1px] overflow-hidden group cursor-pointer active:scale-95 transition-transform">
           <div class="absolute inset-0 animate-border-beam" style="--duration: 4; background: conic-gradient(from 0deg at 50% 50%, transparent 0%, transparent 80%, white 100%)"></div>
           <button class="relative bg-dark-bg rounded-full px-8 py-3.5 text-bone font-medium group-hover:bg-white/5 transition-colors">
             Submit Project
           </button>
        </div>
      </div>
    </div>

    <!-- Right: Rotating Cards - IMPROVED -->
    <div
      class="relative h-[600px] w-full flex items-center justify-center animate-fade-in-up"
      style="animation-delay: 2.2s; perspective: 1200px"
      on:mouseenter={() => isHovering = true}
      on:mouseleave={() => isHovering = false}
      role="region"
      aria-label="Featured Projects Carousel"
    >
      <!-- Navigation Controls -->
      <div class="absolute top-1/2 -translate-y-1/2 w-full flex justify-between z-50 pointer-events-none px-4 lg:-px-12">
         <button on:click={prevCard} class="pointer-events-auto p-4 hover:bg-white/10 rounded-full transition-all text-bone/30 hover:text-bone hover:scale-110 backdrop-blur-sm border border-transparent hover:border-white/10">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M15 18l-6-6 6-6"/></svg>
         </button>
         <button on:click={nextCard} class="pointer-events-auto p-4 hover:bg-white/10 rounded-full transition-all text-bone/30 hover:text-bone hover:scale-110 backdrop-blur-sm border border-transparent hover:border-white/10">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9 18l6-6-6-6"/></svg>
         </button>
      </div>

      <div class="relative w-[340px] aspect-[3/4] preserve-3d">
         {#each featuredProjects as project, idx (project.id)}
           {@const isActive = idx === currentCardIndex}
           {@const isPrev = (idx + 1) % 3 === currentCardIndex}
           {@const isNext = !isActive && !isPrev}

           <div
            class="absolute inset-0 transition-all duration-700 ease-[cubic-bezier(0.19,1,0.22,1)]"
            style:transform={isActive ? 'translateX(0) translateZ(0) rotateY(0deg) scale(1)' : isPrev ? 'translateX(-140px) translateZ(-250px) rotateY(25deg) scale(0.9)' : 'translateX(140px) translateZ(-250px) rotateY(-25deg) scale(0.9)'}
            style:z-index={isActive ? 30 : 10}
            style:opacity={isActive ? 1 : 0.5}
            style:pointer-events={isActive ? 'auto' : 'none'}
           >
             <!-- Card Container -->
             <div class={`
                h-full w-full rounded-3xl p-8 flex flex-col items-center text-center relative overflow-hidden group
                bg-[#141414] border transition-colors duration-500
                ${isActive ? 'border-white/20 shadow-[0_20px_60px_-15px_rgba(0,0,0,1)]' : 'border-white/5 shadow-none grayscale'}
             `}>

                <!-- Internal Lighting/Gradient -->
                <div class={`absolute inset-0 bg-gradient-to-b from-white/10 to-transparent transition-opacity duration-500 ${isActive ? 'opacity-100' : 'opacity-20'}`}></div>

                <!-- Top Highlight Badge -->
                <div class="relative z-10 w-full flex justify-between items-center mb-8">
                   <div class="px-3 py-1 rounded-full bg-white/5 border border-white/10 backdrop-blur-md text-[10px] font-bold tracking-widest text-bone-dark/60 uppercase">
                     {project.category}
                   </div>
                   <div class="h-2 w-2 rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)]"></div>
                </div>

                <!-- Logo Area -->
                <div class="relative z-10 flex-grow flex items-center justify-center">
                   <div class={`text-8xl transition-transform duration-500 ${isActive ? 'scale-100 group-hover:scale-110' : 'scale-75'}`}>
                     {project.logo}
                   </div>
                   <!-- Ambient glow behind logo -->
                   <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32 bg-white/5 rounded-full blur-3xl -z-10"></div>
                </div>

                <!-- Content Area -->
                <div class="relative z-10 w-full mt-auto space-y-4">
                    <h3 class="text-3xl font-bold text-bone tracking-tight">{project.name}</h3>
                    <p class="text-xs text-bone-dark/60 leading-relaxed line-clamp-3">
                      {project.description}
                    </p>

                    <!-- Stats Grid -->
                    <div class="grid grid-cols-2 gap-2 pt-4 border-t border-white/5 mt-4">
                       <div class="flex flex-col p-2 rounded bg-white/5">
                          <span class="text-[10px] uppercase text-bone-dark/40 font-bold">Stars</span>
                          <span class="text-sm font-mono text-bone">{project.insights.stars.toLocaleString()}</span>
                       </div>
                       <div class="flex flex-col p-2 rounded bg-white/5">
                          <span class="text-[10px] uppercase text-bone-dark/40 font-bold">Activity</span>
                          <span class="text-sm font-mono text-bone">High</span>
                       </div>
                    </div>
                </div>
             </div>
           </div>
         {/each}
      </div>
    </div>
  </div>
</section>

<style>
  .preserve-3d {
    transform-style: preserve-3d;
  }

  /* Add custom animations here if not in global CSS */
  @keyframes blob {
    0% { transform: translate(0px, 0px) scale(1); }
    33% { transform: translate(30px, -50px) scale(1.1); }
    66% { transform: translate(-20px, 20px) scale(0.9); }
    100% { transform: translate(0px, 0px) scale(1); }
  }
  .animate-blob {
    animation: blob 7s infinite;
  }

  @keyframes slide-down {
    0% { transform: translateY(-100%); opacity: 0; }
    100% { transform: translateY(0); opacity: 1; }
  }
  .animate-slide-down {
    animation: slide-down 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  }

  @keyframes fade-in-up {
    0% { transform: translateY(20px); opacity: 0; }
    100% { transform: translateY(0); opacity: 1; }
  }
  .animate-fade-in-up {
    animation: fade-in-up 0.8s ease-out forwards;
  }

  @keyframes border-beam {
    100% { offset-distance: 100%; }
  }
  .animate-border-beam {
    /* This requires more complex CSS or a library usually, simplified here */
    animation: spin 4s linear infinite;
  }
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
</style>
