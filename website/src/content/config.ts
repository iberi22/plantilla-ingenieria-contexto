import { defineCollection, z } from "astro:content";

const blogCollection = defineCollection({
	type: "content",
	schema: z.object({
		layout: z.string().optional(),
		title: z.string(),
		date: z.coerce.date().optional(),
		description: z.string().optional(),
		repo: z.string().optional(),
		stars: z.number().optional(),
		language: z.string().optional(),
		repo_data: z
			.object({
				full_name: z.string(),
				description: z.string().optional(),
				stars: z.number().optional(),
				language: z.string().optional(),
				url: z.string().optional(),
				owner: z.string().optional(),
			})
			.optional(),
		categories: z.array(z.string()).optional(),
		tags: z.array(z.string()).optional(),
		images: z.record(z.string()).optional(),
		video: z.string().optional(),
		production_metrics: z.record(z.any()).optional(),
		critical_issues: z.array(z.any()).optional(),
	}),
});

export const collections = {
	blog: blogCollection,
};
