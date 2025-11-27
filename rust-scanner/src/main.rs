use anyhow::{Context, Result};
use chrono::{DateTime, Utc};
use reqwest::Client;
use serde::{Deserialize, Serialize};
use std::env;
use log::{info, warn, error};

#[derive(Debug, Deserialize, Serialize)]
struct GitHubRepo {
    full_name: String,
    name: String,
    description: Option<String>,
    html_url: String,
    stargazers_count: u32,
    forks_count: u32,
    open_issues_count: u32,
    license: Option<License>,
    archived: bool,
    disabled: bool,
    pushed_at: DateTime<Utc>,
    default_branch: String,
}

#[derive(Debug, Deserialize, Serialize)]
struct License {
    name: String,
    spdx_id: String,
}

#[derive(Debug, Deserialize)]
struct SearchResponse {
    items: Vec<GitHubRepo>,
    total_count: u32,
}

#[derive(Debug, Deserialize)]
struct ReadmeResponse {
    size: u32,
}

#[derive(Debug, Deserialize)]
struct WorkflowRunsResponse {
    workflow_runs: Vec<WorkflowRun>,
}

#[derive(Debug, Deserialize)]
struct WorkflowRun {
    id: u64,
    status: String,
    conclusion: Option<String>,
}

pub struct GitHubScanner {
    client: Client,
    token: String,
}

impl GitHubScanner {
    pub fn new(token: String) -> Self {
        let client = Client::builder()
            .user_agent("bestof-opensource-scanner/1.0")
            .build()
            .expect("Failed to build HTTP client");

        Self { client, token }
    }

    pub async fn scan_recent_repos(&self, limit: u32) -> Result<Vec<GitHubRepo>> {
        info!("🔍 Scanning GitHub for recent quality repositories...");

        // Buscar repos con buen engagement, últimos 6 meses, sin filtros negativos de template
        let query = "stars:>200+forks:>20+pushed:>2025-05-01";
        let url = format!(
            "https://api.github.com/search/repositories?q={}&sort=stars&order=desc&per_page={}",
            query, limit
        );

        info!("Query URL: {}", url);

        let response = self
            .client
            .get(&url)
            .header("Authorization", format!("token {}", self.token))
            .header("Accept", "application/vnd.github.v3+json")
            .send()
            .await
            .context("Failed to search repositories")?;

        if !response.status().is_success() {
            let status = response.status();
            let text = response.text().await?;
            error!("GitHub API error ({}): {}", status, text);
            anyhow::bail!("GitHub API returned error: {}", status);
        }

        let response_text = response.text().await?;

        let search_response: SearchResponse = serde_json::from_str(&response_text)
            .context("Failed to parse search response")?;

        info!("Found {} repositories", search_response.items.len());
        Ok(search_response.items)
    }

    pub async fn validate_repo(&self, repo: &GitHubRepo) -> bool {
        info!("🔎 Validating repo: {}", repo.full_name);

        // 1. Basic metadata checks
        if let Some(desc) = &repo.description {
            if desc.len() < 50 {
                info!("  ⏭️  Skipping: Description too short (need 50+ chars)");
                return false;
            }
        } else {
            info!("  ⏭️  Skipping: No description");
            return false;
        }

        if repo.license.is_none() {
            info!("  ⏭️  Skipping: No license");
            return false;
        }

        if repo.archived || repo.disabled {
            info!("  ⏭️  Skipping: Archived or disabled");
            return false;
        }

        // Verificar engagement mínimo (stars y forks)
        if repo.stargazers_count < 200 {
            info!("  ⏭️  Skipping: Not enough stars (need 200+)");
            return false;
        }

        if repo.forks_count < 20 {
            info!("  ⏭️  Skipping: Not enough forks (need 20+)");
            return false;
        }

        // 2. Keyword filtering
        let name_desc = format!(
            "{} {}",
            repo.name.to_lowercase(),
            repo.description.as_ref().unwrap().to_lowercase()
        );

        // Keywords que indican proyectos no productivos
        let exclude_keywords = [
            "alpha", "beta", "test", "demo", "example", "tutorial",
            "course", "starter", "template", "playground", "boilerplate",
            "sample", "prototype", "learning", "practice", "homework"
        ];

        if exclude_keywords.iter().any(|k| name_desc.contains(k)) {
            info!("  ⏭️  Skipping: Contains exclude keywords");
            return false;
        }

        // Keywords que indican innovación y calidad (bonus, no requerido)
        let innovation_keywords = [
            "ai", "ml", "machine learning", "deep learning", "llm", "gpt",
            "blockchain", "web3", "decentralized", "distributed",
            "real-time", "performance", "optimization", "scalable",
            "compiler", "framework", "engine", "runtime",
            "neural", "model", "inference", "training",
            "cloud-native", "serverless", "microservices",
            "quantum", "edge computing", "iot", "autonomous",
            "zero-knowledge", "privacy-preserving", "secure",
            "rust", "go", "typescript", "python", "webassembly", "wasm"
        ];

        let has_innovation = innovation_keywords.iter().any(|k| name_desc.contains(k));
        if has_innovation {
            info!("  ✨ Innovation keywords found!");
        }

        // 3. Check README (proyectos innovadores tienen buena documentación)
        if !self.has_substantial_readme(&repo.full_name).await {
            info!("  ⏭️  Skipping: README too short (need 800+ chars)");
            return false;
        }

        // 4. Check CI status (opcional - muchos proyectos buenos no usan GitHub Actions)
        let has_ci = self.check_ci_status(&repo.full_name).await;
        if has_ci {
            info!("  ✨ CI/CD found!");
        }

        info!("  ✅ Repo validation passed!");
        true
    }

    async fn has_substantial_readme(&self, full_name: &str) -> bool {
        let url = format!("https://api.github.com/repos/{}/readme", full_name);

        match self
            .client
            .get(&url)
            .header("Authorization", format!("token {}", self.token))
            .header("Accept", "application/vnd.github.v3+json")
            .send()
            .await
        {
            Ok(response) => {
                if response.status().is_success() {
                    if let Ok(readme) = response.json::<ReadmeResponse>().await {
                        // Proyectos innovadores tienen documentación extensa
                        return readme.size > 800;
                    }
                }
                false
            }
            Err(_) => false,
        }
    }

    async fn check_ci_status(&self, full_name: &str) -> bool {
        let url = format!(
            "https://api.github.com/repos/{}/actions/runs?per_page=5&status=success",
            full_name
        );

        match self
            .client
            .get(&url)
            .header("Authorization", format!("token {}", self.token))
            .header("Accept", "application/vnd.github.v3+json")
            .send()
            .await
        {
            Ok(response) => {
                if response.status().is_success() {
                    if let Ok(runs) = response.json::<WorkflowRunsResponse>().await {
                        return !runs.workflow_runs.is_empty();
                    }
                }
                false
            }
            Err(_) => false,
        }
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();

    info!("🦀 GitHub Scanner (Rust) v1.0");
    info!("{}", "=".repeat(60));

    let token = env::var("GITHUB_TOKEN")
        .context("GITHUB_TOKEN environment variable not set")?;

    let scanner = GitHubScanner::new(token);

    // Scan for repositories (aumentar cantidad para mejor selección)
    let repos = scanner.scan_recent_repos(100).await?;

    info!("\n🔍 Validating repositories...");

    let mut valid_repos = Vec::new();
    for repo in repos {
        if scanner.validate_repo(&repo).await {
            valid_repos.push(repo);

            // Encontrar hasta 3 repos válidos
            if valid_repos.len() >= 3 {
                break;
            }
        }
    }

    info!("{}", "=".repeat(60));
    info!("✅ Scan complete!");
    info!("Found {} valid repositories", valid_repos.len());

    if let Some(repo) = valid_repos.first() {
        info!("\n📦 Selected repository:");
        info!("  Name: {}", repo.full_name);
        info!("  Stars: ⭐ {}", repo.stargazers_count);
        info!("  Description: {}", repo.description.as_ref().unwrap_or(&"N/A".to_string()));

        // Output JSON for Python to consume
        let json_output = serde_json::to_string(&repo)?;
        println!("\n__REPO_JSON__");
        println!("{}", json_output);
        println!("__END_JSON__");
    } else {
        warn!("⚠️  No valid repositories found");
    }

    Ok(())
}
