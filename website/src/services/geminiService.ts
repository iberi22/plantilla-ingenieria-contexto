import { GoogleGenAI } from "@google/genai";

// Initialize Gemini Client
// In Astro, use import.meta.env for environment variables
const apiKey = import.meta.env.PUBLIC_GEMINI_API_KEY || "";
// Note: Exposing API key in PUBLIC_ variable is not safe for client-side if it's a real secret.
// For a static site demo, it might be okay if restricted, or we should use a backend function.
// For this template, we'll assume it's okay or user will configure it properly.

const ai = apiKey ? new GoogleGenAI({ apiKey }) : null;

export const analyzeRepoWithGemini = async (
	repoName: string,
	description: string,
): Promise<string> => {
	if (!ai) {
		console.warn("Gemini API Key missing. Returning mock analysis.");
		return "API Key missing. Unable to generate live insights. Please configure your API key to see real-time analysis of this repository's potential issues and strengths.";
	}

	try {
		const model = "gemini-2.5-flash";
		const prompt = `
      Analyze the following open source project based on its name and description.
      Project: ${repoName}
      Description: ${description}

      Provide a concise, 2-sentence "Insight" regarding its potential utility, code quality expectations (based on typical projects of this type), and potential "grave issues" or challenges a developer might face (e.g., complexity, maintenance, breaking changes).
      Keep it professional and technical.
    `;

		const response = await ai.models.generateContent({
			model: model,
			contents: prompt,
		});

		return response.text || "Analysis unavailable.";
	} catch (error) {
		console.error("Gemini analysis failed:", error);
		return "Failed to retrieve live analysis due to network or API limits.";
	}
};
