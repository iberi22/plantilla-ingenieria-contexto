// Complete Repository Analyzer with Rayon Parallelism
use serde::{Deserialize, Serialize};
use reqwest::Client;
use chrono::{DateTime, Utc, Duration};
use std::error::Error;
use rayon::prelude::*;
use log::{info, warn};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct RepoAnalysis {
    pub repo: String,
    pub total_score: f64,
    pub recommendation: String,
    pub priority: String,
    pub scores: Scores,
    pub ai_review: Option<AIReview>,
    pub metadata: Metadata,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Scores {
    pub commit_activity: f64,
    pub code_quality: f64,
    pub developer_engagement: f64,
    pub project_maturity: f64,
    pub ai_code_quality: Option<f64>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct AIReview {
    pub architecture: i32,
    pub documentation: i32,
    pub testing: i32,
    pub practices: i32,
    pub innovation: i32,
    pub key_strengths: Vec<String>,
    pub improvements: Vec<String>,
    pub assessment: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Metadata {
    pub stars: i32,
    pub forks: i32,
    pub language: Option<String>,
    pub created_at: String,
    pub last_push: String,
}

#[derive(Debug, Deserialize)]
struct Commit {
    sha: String,
    commit: CommitDetails,
}

#[derive(Debug, Deserialize)]
struct CommitDetails {
    author: Author,
    message: String,
}

#[derive(Debug, Deserialize)]
struct Author {
    date: String,
}

#[derive(Debug, Deserialize)]
struct Issue {
    created_at: String,
    closed_at: Option<String>,
    state: String,
}

#[derive(Debug, Deserialize)]
struct PullRequest {
    created_at: String,
    merged_at: Option<String>,
    state: String,
}

#[derive(Debug, Deserialize)]
struct RepoContents {
    name: String,
    #[serde(rename = "type")]
    item_type: String,
}

pub struct GemAnalyzer {
    client: Client,
    github_token: String,
}

impl GemAnalyzer {
    pub fn new(github_token: String) -> Self {
        let client = Client::builder()
            .user_agent("bestof-opensource-analyzer/1.0")
            .timeout(std::time::Duration::from_secs(30))
            .build()
            .unwrap();

        GemAnalyzer {
            client,
            github_token,
        }
    }

    /// Analyze multiple repositories in parallel using Rayon
    pub async fn analyze_repos_parallel(&self, repos: Vec<(String, Metadata)>) -> Vec<RepoAnalysis> {
        info!("🚀 Starting parallel analysis of {} repositories with Rayon", repos.len());
        
        // Use Rayon for parallel processing
        let results: Vec<RepoAnalysis> = repos
            .par_iter()
            .filter_map(|(repo, metadata)| {
                // Create a runtime for this thread to run async code
                let rt = tokio::runtime::Runtime::new().ok()?;
                
                match rt.block_on(self.analyze_single_repo(repo.clone(), metadata.clone())) {
                    Ok(analysis) => {
                        info!("✅ Analyzed {}: {:.2}/100", repo, analysis.total_score);
                        Some(analysis)
                    }
                    Err(e) => {
                        warn!("❌ Failed to analyze {}: {}", repo, e);
                        None
                    }
                }
            })
            .collect();

        info!("✅ Parallel analysis complete: {}/{} repos analyzed", results.len(), repos.len());
        results
    }

    /// Analyze a single repository (called by parallel processor)
    async fn analyze_single_repo(&self, repo: String, metadata: Metadata) -> Result<RepoAnalysis, Box<dyn Error>> {
        info!("🔍 Analyzing {}...", repo);

        // Score components
        let commit_score = self.analyze_commit_activity(&repo).await?;
        let quality_score = self.analyze_code_quality(&repo).await?;
        let engagement_score = self.analyze_developer_engagement(&repo).await?;
        let maturity_score = self.calculate_maturity_score(&metadata);

        // Calculate total (weighted average)
        let total_score = (commit_score * 0.30)
            + (quality_score * 0.25)
            + (engagement_score * 0.25)
            + (maturity_score * 0.20);

        // Determine recommendation
        let (recommendation, priority) = if total_score >= 70.0 {
            ("APPROVE".to_string(), "HIGH".to_string())
        } else if total_score >= 60.0 {
            ("REVIEW".to_string(), "MEDIUM".to_string())
        } else {
            ("REJECT".to_string(), "LOW".to_string())
        };

        Ok(RepoAnalysis {
            repo: repo.clone(),
            total_score: (total_score * 100.0).round() / 100.0,
            recommendation,
            priority,
            scores: Scores {
                commit_activity: (commit_score * 100.0).round() / 100.0,
                code_quality: (quality_score * 100.0).round() / 100.0,
                developer_engagement: (engagement_score * 100.0).round() / 100.0,
                project_maturity: (maturity_score * 100.0).round() / 100.0,
                ai_code_quality: None,
            },
            ai_review: None,
            metadata,
        })
    }

    /// Factor 1: Commit Activity Analysis
    async fn analyze_commit_activity(&self, repo: &str) -> Result<f64, Box<dyn Error>> {
        let url = format!("https://api.github.com/repos/{}/commits?per_page=100", repo);
        
        let response = self.client
            .get(&url)
            .header("Authorization", format!("Bearer {}", self.github_token))
            .header("Accept", "application/vnd.github+json")
            .send()
            .await?;

        if !response.status().is_success() {
            return Ok(50.0); // Default score on error
        }

        let commits: Vec<Commit> = response.json().await?;
        
        if commits.is_empty() {
            return Ok(20.0);
        }

        let now = Utc::now();
        let recent_commits = commits.iter().filter(|c| {
            if let Ok(date) = DateTime::parse_from_rfc3339(&c.commit.author.date) {
                let commit_date: DateTime<Utc> = date.into();
                now.signed_duration_since(commit_date) < Duration::days(90)
            } else {
                false
            }
        }).count();

        // Score based on recent commits (0-100)
        let score = ((recent_commits as f64 / 30.0) * 100.0).min(100.0);
        Ok(score)
    }

    /// Factor 2: Code Quality Analysis
    async fn analyze_code_quality(&self, repo: &str) -> Result<f64, Box<dyn Error>> {
        let url = format!("https://api.github.com/repos/{}/contents", repo);
        
        let response = self.client
            .get(&url)
            .header("Authorization", format!("Bearer {}", self.github_token))
            .header("Accept", "application/vnd.github+json")
            .send()
            .await?;

        if !response.status().is_success() {
            return Ok(50.0);
        }

        let contents: Vec<RepoContents> = response.json().await?;
        
        let mut score: f64 = 50.0;

        // Check for quality indicators
        if contents.iter().any(|f| f.name.to_lowercase() == "readme.md") {
            score += 15.0;
        }
        if contents.iter().any(|f| f.name.to_lowercase() == "license") {
            score += 10.0;
        }
        if contents.iter().any(|f| f.name.to_lowercase().contains("test")) {
            score += 15.0;
        }
        if contents.iter().any(|f| f.name == ".github" && f.item_type == "dir") {
            score += 10.0;
        }

        Ok(score.min(100.0))
    }

    /// Factor 3: Developer Engagement Analysis
    async fn analyze_developer_engagement(&self, repo: &str) -> Result<f64, Box<dyn Error>> {
        // Analyze issues
        let issues_url = format!("https://api.github.com/repos/{}/issues?state=all&per_page=50", repo);
        let issues_response = self.client
            .get(&issues_url)
            .header("Authorization", format!("Bearer {}", self.github_token))
            .header("Accept", "application/vnd.github+json")
            .send()
            .await;

        let issues_score = if let Ok(resp) = issues_response {
            if resp.status().is_success() {
                if let Ok(issues) = resp.json::<Vec<Issue>>().await {
                    let closed = issues.iter().filter(|i| i.closed_at.is_some()).count();
                    let total = issues.len();
                    if total > 0 {
                        ((closed as f64 / total as f64) * 50.0).min(50.0)
                    } else {
                        25.0
                    }
                } else {
                    25.0
                }
            } else {
                25.0
            }
        } else {
            25.0
        };

        // Analyze pull requests
        let prs_url = format!("https://api.github.com/repos/{}/pulls?state=all&per_page=50", repo);
        let prs_response = self.client
            .get(&prs_url)
            .header("Authorization", format!("Bearer {}", self.github_token))
            .header("Accept", "application/vnd.github+json")
            .send()
            .await;

        let prs_score = if let Ok(resp) = prs_response {
            if resp.status().is_success() {
                if let Ok(prs) = resp.json::<Vec<PullRequest>>().await {
                    let merged = prs.iter().filter(|pr| pr.merged_at.is_some()).count();
                    let total = prs.len();
                    if total > 0 {
                        ((merged as f64 / total as f64) * 50.0).min(50.0)
                    } else {
                        25.0
                    }
                } else {
                    25.0
                }
            } else {
                25.0
            }
        } else {
            25.0
        };

        Ok(issues_score + prs_score)
    }

    /// Factor 4: Project Maturity Score
    fn calculate_maturity_score(&self, metadata: &Metadata) -> f64 {
        let mut score = 0.0;

        // Age score (max 30 points)
        if let Ok(created) = DateTime::parse_from_rfc3339(&metadata.created_at) {
            let age_days = Utc::now().signed_duration_since(created.with_timezone(&Utc)).num_days();
            score += ((age_days as f64 / 365.0) * 30.0).min(30.0);
        }

        // Stars score (max 35 points)
        score += ((metadata.stars as f64 / 500.0) * 35.0).min(35.0);

        // Forks score (max 35 points)
        score += ((metadata.forks as f64 / 100.0) * 35.0).min(35.0);

        score.min(100.0)
    }
}
