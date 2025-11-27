export enum ProjectCategory {
	ALL = "All",
	AI_TOOLS = "AI Tools",
	AI_MODELS = "AI Models",
	AI_TRAINING = "AI Training",
	CYBERSECURITY = "Cybersecurity",
	UI_UX = "UI/UX",
	WEB_FRAMEWORKS = "Web Frameworks",
	DATABASES = "Databases",
}

export interface Insights {
	stars: number;
	forks: number;
	openIssues: number;
	seriousIssuesCount: number;
	lastCommit: string;
	summary: string;
}

export interface Project {
	id: string;
	name: string;
	description: string;
	url: string;
	category: ProjectCategory;
	tags: string[];
	insights: Insights;
	logo: string; // Emoji or URL
	image?: string; // Screenshot or cover image
	// Blog specific fields
	publishDate?: string; // ISO date string YYYY-MM-DD
	author?: string;
	longContent?: string; // Simulating a blog post body
}

export interface GeminAnalysisResult {
	analysis: string;
	rating: number; // 1-10
}
