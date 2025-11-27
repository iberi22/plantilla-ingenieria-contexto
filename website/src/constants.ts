import { type Project, ProjectCategory } from "./types";

export const BASE_URL = "/bestof-opensorce";

export const HERO_WORDS = ["DISCOVER", "ANALYZE", "CONTRIBUTE", "EVOLVE"];

export const PROJECTS: Project[] = [
	{
		id: "1",
		name: "AutoGPT",
		description:
			"An experimental open-source attempt to make GPT-4 fully autonomous.",
		url: "https://github.com/Significant-Gravitas/Auto-GPT",
		category: ProjectCategory.AI_TOOLS,
		tags: ["Python", "LLM", "Agent"],
		logo: "🤖",
		publishDate: "2025-02-15",
		author: "Sarah Dev",
		longContent:
			"AutoGPT represents a paradigm shift in how we perceive AI agents. Rather than simple prompt-response loops, it attempts to chain thoughts to achieve complex goals. In our analysis this week, we look at how its dependency graph has grown and the implications for production stability.",
		insights: {
			stars: 162000,
			forks: 35000,
			openIssues: 420,
			seriousIssuesCount: 12,
			lastCommit: "2 days ago",
			summary:
				"High activity, but complex dependency management issues reported recently.",
		},
	},
	{
		id: "2",
		name: "LangChain",
		description: "Building applications with LLMs through composability.",
		url: "https://github.com/langchain-ai/langchain",
		category: ProjectCategory.AI_TOOLS,
		tags: ["Python", "TypeScript", "Framework"],
		logo: "🦜",
		publishDate: "2025-02-14",
		author: "Alex Code",
		longContent:
			"The glue of the AI ecosystem. LangChain has become the de-facto standard for chaining LLM calls. However, recent breaking changes have caused friction. This post explores the balance between rapid innovation and API stability.",
		insights: {
			stars: 84000,
			forks: 12000,
			openIssues: 850,
			seriousIssuesCount: 45,
			lastCommit: "1 hour ago",
			summary:
				"Rapid breaking changes in recent versions causing integration friction.",
		},
	},
	{
		id: "3",
		name: "Stable Diffusion WebUI",
		description: "Stable Diffusion web UI with an easy-to-use interface.",
		url: "https://github.com/AUTOMATIC1111/stable-diffusion-webui",
		category: ProjectCategory.AI_MODELS,
		tags: ["Python", "Gradio", "Image Gen"],
		logo: "🎨",
		publishDate: "2025-02-10",
		author: "Visual AI Team",
		longContent:
			"Generative AI art for the masses. This WebUI unlocked the potential of Stable Diffusion for non-coders. We dive into the extension ecosystem that makes this tool infinitely extensible.",
		insights: {
			stars: 130000,
			forks: 26000,
			openIssues: 1200,
			seriousIssuesCount: 8,
			lastCommit: "3 days ago",
			summary:
				"Very mature community, but installation can be brittle on non-NVIDIA hardware.",
		},
	},
	{
		id: "4",
		name: "Metasploit",
		description: "The world's most used penetration testing framework.",
		url: "https://github.com/rapid7/metasploit-framework",
		category: ProjectCategory.CYBERSECURITY,
		tags: ["Ruby", "Security", "Pentest"],
		logo: "🛡️",
		publishDate: "2025-02-08",
		author: "SecOps Daily",
		longContent:
			"An old guard in a new world. Metasploit continues to be relevant even in the age of AI-driven attacks. We review its latest modules and how Ruby continues to power this security giant.",
		insights: {
			stars: 32000,
			forks: 14000,
			openIssues: 230,
			seriousIssuesCount: 2,
			lastCommit: "5 hours ago",
			summary:
				"Rock stable. Industry standard. Documentation is vast but scattered.",
		},
	},
	{
		id: "5",
		name: "Shadcn UI",
		description:
			"Beautifully designed components built with Radix UI and Tailwind CSS.",
		url: "https://github.com/shadcn-ui/ui",
		category: ProjectCategory.UI_UX,
		tags: ["React", "Tailwind", "Accessible"],
		logo: "💅",
		publishDate: "2025-02-05",
		author: "Frontend Weekly",
		longContent:
			"Not a library, but a philosophy. Copy-paste components have changed how we build React apps. We discuss why 'owning your code' is the trend of 2025.",
		insights: {
			stars: 55000,
			forks: 3000,
			openIssues: 150,
			seriousIssuesCount: 0,
			lastCommit: "1 day ago",
			summary:
				"Exceptional quality. Not a library, but a copy-paste component collection.",
		},
	},
	{
		id: "6",
		name: "Supabase",
		description: "The open source Firebase alternative.",
		url: "https://github.com/supabase/supabase",
		category: ProjectCategory.DATABASES,
		tags: ["PostgreSQL", "Realtime", "Auth"],
		logo: "⚡",
		publishDate: "2025-02-01",
		author: "DBA Insider",
		longContent:
			"PostgreSQL with superpowers. Supabase provides the DX of Firebase with the power of SQL. Is it ready for enterprise scale? Our metrics say yes.",
		insights: {
			stars: 65000,
			forks: 5000,
			openIssues: 600,
			seriousIssuesCount: 15,
			lastCommit: "4 hours ago",
			summary:
				"Strong growth. Some reports of realtime latency spikes in specific regions.",
		},
	},
];

export const TESTIMONIALS = [
	"This directory saved me hours of research.",
	"The AI insights are scary accurate.",
	"Finally, a clean list of tools that actually work.",
	"Minimalist design, maximum information.",
	"I found my new favorite framework here.",
	"Open Source needs more curation like this.",
];
