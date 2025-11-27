import { defineCollection, z } from 'astro:content';

const blogCollection = defineCollection({
	type: 'content',
	schema: z.object({
		title: z.string(),
        // Allow string or date for flexibility
		date: z.union([z.string(), z.date()]).transform((str) => new Date(str)),
		repo: z.string(),
		stars: z.number().optional().default(0),
		language: z.string().optional(),
		tags: z.array(z.string()).optional().default([]),
		images: z.object({
			architecture: z.string().optional(),
			flow: z.string().optional(),
			screenshot: z.string().optional(),
		}).optional(),
        description: z.string().optional(),
        // Support both single category and array of categories
        category: z.string().optional(),
        categories: z.array(z.string()).optional(),
        repo_data: z.any().optional(), // Allow any structure for repo_data
	}),
});

export const collections = {
	'blog': blogCollection,
};
