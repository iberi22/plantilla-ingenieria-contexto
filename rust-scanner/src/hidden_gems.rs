// Hidden Gems Scanner - Find quality low-visibility projects
use serde::{Deserialize, Serialize};
use reqwest;
use std::error::Error;

#[derive(Debug, Serialize, Deserialize)]
pub struct HiddenGemRepo {
    pub name: String,
    pub full_name: String,
    pub html_url: String,
    pub description: Option<String>,
    #[serde(rename = "stargazers_count")]
    pub stars: i32,
    #[serde(rename = "forks_count")]
    pub forks: i32,
    pub language: Option<String>,
    pub license: Option<License>,
    pub created_at: String,
    pub updated_at: String,
    pub pushed_at: String,
    pub size: i32,
    pub open_issues: i32,
    pub has_wiki: bool,
    pub has_pages: bool,
    pub topics: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct License {
    pub name: String,
    pub spdx_id: String,
}

#[derive(Debug, Deserialize)]
struct SearchResponse {
    items: Vec<HiddenGemRepo>,
    total_count: i32,
}

pub struct HiddenGemsScanner {
    client: reqwest::Client,
    github_token: String,
}

impl HiddenGemsScanner {
    pub fn new(github_token: String) -> Self {
        let client = reqwest::Client::builder()
            .user_agent("bestof-opensource-scanner/1.0")
            .build()
            .unwrap();

        HiddenGemsScanner {
            client,
            github_token,
        }
    }

    pub async fn scan_tier(&self, tier: &str) -> Result<Vec<HiddenGemRepo>, Box<dyn Error>> {
        let (min_stars, max_stars, min_forks, max_forks) = match tier {
            "micro" => (10, 100, 5, 50),
            "small" => (100, 500, 10, 100),
            "medium" => (500, 2000, 20, 200),
            _ => (100, 500, 10, 100), // Default to small
        };

        info!("🔍 Scanning {} tier: stars {}..{}, forks {}..{}",
              tier, min_stars, max_stars, min_forks, max_forks);

        let query = format!(
            "stars:{}..{}+forks:{}..{}+pushed:>2024-06-01+is:public",
            min_stars, max_stars, min_forks, max_forks
        );

        let mut found_repos = Vec::new();
        let mut page = 1;

        // Limit to 5 projects per run to conserve API usage (reviews + images)
        const MAX_PROJECTS: usize = 5;

        while found_repos.len() < MAX_PROJECTS && page <= 5 {
            let url = format!(
                "https://api.github.com/search/repositories?q={}&sort=updated&order=desc&per_page=20&page={}",
                query, page
            );

            info!("📡 Fetching page {}...", page);

            let response = self.client
                .get(&url)
                .header("Authorization", format!("Bearer {}", self.github_token))
                .header("Accept", "application/vnd.github+json")
                .header("X-GitHub-Api-Version", "2022-11-28")
                .send()
                .await?;

            if !response.status().is_success() {
                let status = response.status();
                let error_text = response.text().await?;
                return Err(format!("GitHub API error {}: {}", status, error_text).into());
            }

            let search_result: SearchResponse = response.json().await?;

            info!("📦 Found {} repositories on page {}", search_result.items.len(), page);

            for repo in search_result.items {
                if self.is_valid_hidden_gem(&repo)? {
                    info!("✅ Valid gem: {} ({} ⭐, {} 🍴)",
                          repo.full_name, repo.stars, repo.forks);
                    found_repos.push(repo);

                    if found_repos.len() >= MAX_PROJECTS {
                        break;
                    }
                }
            }

            page += 1;
        }

        info!("✨ Found {} hidden gems in tier {}", found_repos.len(), tier);
        Ok(found_repos)
    }

    fn is_valid_hidden_gem(&self, repo: &HiddenGemRepo) -> Result<bool, Box<dyn Error>> {
        // Must have description
        let description = match &repo.description {
            Some(desc) if desc.len() >= 30 => desc,
            _ => {
                info!("❌ {}: Description too short or missing", repo.full_name);
                return Ok(false);
            }
        };

        // Check for red flag keywords in description/name
        let red_flags = [
            "alpha", "beta", "test", "experimental", "wip",
            "work in progress", "under development", "prototype",
            "template", "boilerplate", "starter"
        ];

        let full_text = format!("{} {}",
                                repo.name.to_lowercase(),
                                description.to_lowercase());

        for flag in &red_flags {
            if full_text.contains(flag) {
                info!("🚩 {}: Contains red flag keyword '{}'", repo.full_name, flag);
                return Ok(false);
            }
        }

        // Must have open source license
        if repo.license.is_none() {
            info!("❌ {}: No license", repo.full_name);
            return Ok(false);
        }

        // Language must be specified
        if repo.language.is_none() {
            info!("❌ {}: No primary language", repo.full_name);
            return Ok(false);
        }

        // Should not be too small (likely incomplete)
        if repo.size < 50 {
            info!("❌ {}: Repository too small ({} KB)", repo.full_name, repo.size);
            return Ok(false);
        }

        // Check activity - pushed in last 6 months already covered by query
        // But verify it's not abandoned (no update in >3 months is warning)
        let pushed_date = chrono::DateTime::parse_from_rfc3339(&repo.pushed_at)?;
        let pushed_date_utc = pushed_date.with_timezone(&chrono::Utc);
        let now = chrono::Utc::now();
        let days_since_push = (now - pushed_date_utc).num_days();

        if days_since_push > 180 {
            info!("⚠️  {}: Last push {} days ago", repo.full_name, days_since_push);
            return Ok(false);
        }

        // Too many open issues compared to stars might indicate problems
        let issue_ratio = repo.open_issues as f32 / repo.stars as f32;
        if issue_ratio > 0.5 {
            info!("⚠️  {}: High issue ratio ({:.2})", repo.full_name, issue_ratio);
            // Not auto-reject, but warning
        }

        // Bonus: check for quality indicators
        let quality_score = self.calculate_quality_indicators(repo);
        if quality_score < 3 {
            info!("❌ {}: Low quality score {}/10", repo.full_name, quality_score);
            return Ok(false);
        }

        info!("✅ {}: Passed initial validation (quality: {})", repo.full_name, quality_score);
        Ok(true)
    }

    fn calculate_quality_indicators(&self, repo: &HiddenGemRepo) -> i32 {
        let mut score = 0;

        // Has topics (shows care in categorization)
        if !repo.topics.is_empty() {
            score += 2;
        }

        // Has wiki or pages (extra documentation)
        if repo.has_wiki || repo.has_pages {
            score += 2;
        }

        // Good description length
        if let Some(desc) = &repo.description {
            if desc.len() > 80 {
                score += 2;
            }
        }

        // Reasonable size (not tiny, not huge)
        if repo.size > 200 && repo.size < 100000 {
            score += 2;
        }

        // Balanced fork ratio
        let fork_ratio = repo.forks as f32 / repo.stars as f32;
        if fork_ratio > 0.05 && fork_ratio < 0.3 {
            score += 2;
        }

        score
    }
}

#[macro_use]
extern crate log;

use env_logger;

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    env_logger::Builder::from_env(env_logger::Env::default().default_filter_or("info")).init();

    let github_token = std::env::var("GITHUB_TOKEN")
        .expect("GITHUB_TOKEN environment variable not set");

    let tier = std::env::args()
        .nth(1)
        .unwrap_or_else(|| "small".to_string());

    info!("🚀 Hidden Gems Scanner starting...");
    info!("📊 Target tier: {}", tier);

    let scanner = HiddenGemsScanner::new(github_token);

    let repos = scanner.scan_tier(&tier).await?;

    println!("__REPO_JSON__");
    println!("{}", serde_json::to_string_pretty(&repos)?);
    println!("__END_JSON__");

    info!("✨ Scan complete! Found {} hidden gems", repos.len());

    Ok(())
}
