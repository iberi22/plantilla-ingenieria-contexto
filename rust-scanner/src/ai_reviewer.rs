// GitHub Models API Integration for AI Code Review
use serde::{Deserialize, Serialize};
use reqwest::Client;
use std::error::Error;
use log::info;

use crate::analyzer::AIReview;

#[derive(Debug, Serialize)]
struct ChatMessage {
    role: String,
    content: String,
}

#[derive(Debug, Serialize)]
struct ChatRequest {
    messages: Vec<ChatMessage>,
    model: String,
    temperature: f32,
    max_tokens: i32,
}

#[derive(Debug, Deserialize)]
struct ChatResponse {
    choices: Vec<Choice>,
}

#[derive(Debug, Deserialize)]
struct Choice {
    message: Message,
}

#[derive(Debug, Deserialize)]
struct Message {
    content: String,
}

#[derive(Debug, Deserialize)]
struct AIScores {
    architecture_score: i32,
    documentation_score: i32,
    testing_score: i32,
    practices_score: i32,
    innovation_score: i32,
    key_strengths: Vec<String>,
    improvements: Vec<String>,
    assessment: String,
}

pub struct AIReviewer {
    client: Client,
    github_token: String,
    model: String,
}

impl AIReviewer {
    pub fn new(github_token: String) -> Self {
        let client = Client::builder()
            .user_agent("bestof-opensource-ai/1.0")
            .timeout(std::time::Duration::from_secs(60))
            .build()
            .unwrap();

        AIReviewer {
            client,
            github_token,
            model: "gpt-4o".to_string(),
        }
    }

    pub async fn review_repository(
        &self,
        repo: &str,
        readme: &str,
        language: &Option<String>,
        stars: i32,
    ) -> Result<AIReview, Box<dyn Error>> {
        info!("🤖 Starting AI review for {}...", repo);

        let prompt = self.create_review_prompt(repo, readme, language, stars);
        
        let response = self.call_github_models(&prompt).await?;
        let scores = self.parse_ai_response(&response)?;

        info!("✅ AI review complete for {}", repo);

        Ok(AIReview {
            architecture: scores.architecture_score,
            documentation: scores.documentation_score,
            testing: scores.testing_score,
            practices: scores.practices_score,
            innovation: scores.innovation_score,
            key_strengths: scores.key_strengths,
            improvements: scores.improvements,
            assessment: scores.assessment,
        })
    }

    fn create_review_prompt(
        &self,
        repo: &str,
        readme: &str,
        language: &Option<String>,
        stars: i32,
    ) -> String {
        let lang = language.as_ref().map(|s| s.as_str()).unwrap_or("unknown");
        let readme_excerpt = if readme.len() > 3000 {
            &readme[..3000]
        } else {
            readme
        };

        format!(
            r#"Analyze this GitHub repository and provide a quality assessment.

Repository: {}
Language: {}
Stars: {}

README excerpt:
{}

Evaluate the project on these 5 dimensions (score 1-10 each):
1. Architecture: Code structure, modularity, design patterns
2. Documentation: README quality, comments, guides
3. Testing: Test coverage, CI/CD, quality assurance
4. Best Practices: Code style, security, performance
5. Innovation: Uniqueness, problem-solving approach

Also provide:
- 3 key strengths
- 3 areas for improvement
- Overall assessment (1 sentence)

Respond ONLY with valid JSON:
{{
  "architecture_score": <1-10>,
  "documentation_score": <1-10>,
  "testing_score": <1-10>,
  "practices_score": <1-10>,
  "innovation_score": <1-10>,
  "key_strengths": ["strength1", "strength2", "strength3"],
  "improvements": ["improvement1", "improvement2", "improvement3"],
  "assessment": "one sentence summary"
}}"#,
            repo, lang, stars, readme_excerpt
        )
    }

    async fn call_github_models(&self, prompt: &str) -> Result<String, Box<dyn Error>> {
        let url = "https://models.inference.ai.azure.com/chat/completions";

        let request = ChatRequest {
            messages: vec![
                ChatMessage {
                    role: "system".to_string(),
                    content: "You are a code review expert. Respond only with valid JSON.".to_string(),
                },
                ChatMessage {
                    role: "user".to_string(),
                    content: prompt.to_string(),
                },
            ],
            model: self.model.clone(),
            temperature: 0.3,
            max_tokens: 800,
        };

        let response = self.client
            .post(url)
            .header("Authorization", format!("Bearer {}", self.github_token))
            .header("Content-Type", "application/json")
            .json(&request)
            .send()
            .await?;

        if !response.status().is_success() {
            let status = response.status();
            let error_text = response.text().await?;
            return Err(format!("GitHub Models API error {}: {}", status, error_text).into());
        }

        let chat_response: ChatResponse = response.json().await?;
        
        if let Some(choice) = chat_response.choices.first() {
            Ok(choice.message.content.clone())
        } else {
            Err("No response from AI model".into())
        }
    }

    fn parse_ai_response(&self, response: &str) -> Result<AIScores, Box<dyn Error>> {
        // Remove markdown code blocks if present
        let cleaned = response
            .trim()
            .trim_start_matches("```json")
            .trim_start_matches("```")
            .trim_end_matches("```")
            .trim();

        // Try to extract JSON object
        let json_start = cleaned.find('{').unwrap_or(0);
        let json_end = cleaned.rfind('}').unwrap_or(cleaned.len());
        let json_str = &cleaned[json_start..=json_end];

        let scores: AIScores = serde_json::from_str(json_str)?;

        // Validate scores are in range
        if scores.architecture_score < 1 || scores.architecture_score > 10 {
            return Err("Invalid architecture score".into());
        }

        Ok(scores)
    }

    pub fn calculate_quality_score(&self, review: &AIReview) -> f64 {
        let avg = (review.architecture + review.documentation + review.testing + 
                   review.practices + review.innovation) as f64 / 5.0;
        (avg / 10.0) * 100.0
    }
}
