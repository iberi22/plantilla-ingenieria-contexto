// Complete Hidden Gems Pipeline with Rayon Parallelism
mod analyzer;
mod ai_reviewer;

use analyzer::{GemAnalyzer, Metadata};
use ai_reviewer::AIReviewer;
use serde::{Deserialize, Serialize};
use reqwest::Client;
use std::error::Error;
use std::env;
use log::{info, error};
use rayon::prelude::*;

#[derive(Debug, Serialize, Deserialize)]
struct HiddenGemRepo {
    full_name: String,
    #[serde(rename = "stargazers_count")]
    stars: i32,
    #[serde(rename = "forks_count")]
    forks: i32,
    language: Option<String>,
    created_at: String,
    pushed_at: String,
}

#[derive(Debug, Deserialize)]
struct SearchResponse {
    items: Vec<HiddenGemRepo>,
}

#[derive(Debug, Deserialize)]
struct RepoDetails {
    default_branch: String,
}

#[derive(Debug, Deserialize)]
struct FileContent {
    content: String,
}

async fn fetch_readme(client: &Client, token: &str, repo: &str) -> Option<String> {
    let url = format!("https://api.github.com/repos/{}/readme", repo);
    
    let response = client
        .get(&url)
        .header("Authorization", format!("Bearer {}", token))
        .header("Accept", "application/vnd.github+json")
        .send()
        .await
        .ok()?;

    if response.status().is_success() {
        let file: FileContent = response.json().await.ok()?;
        // Decode base64 content
        use base64::{Engine as _, engine::general_purpose};
        let decoded = general_purpose::STANDARD.decode(&file.content.replace("\n", "")).ok()?;
        String::from_utf8(decoded).ok()
    } else {
        None
    }
}

async fn scan_repositories(token: &str, tier: &str) -> Result<Vec<(String, Metadata)>, Box<dyn Error>> {
    let (min_stars, max_stars, min_forks, max_forks) = match tier {
        "micro" => (10, 100, 5, 50),
        "small" => (100, 500, 10, 100),
        "medium" => (500, 2000, 20, 200),
        _ => (100, 500, 10, 100),
    };

    info!("🔍 Scanning {} tier: stars {}..{}, forks {}..{}", 
          tier, min_stars, max_stars, min_forks, max_forks);

    let query = format!(
        "stars:{}..{}+forks:{}..{}+pushed:>2024-06-01+is:public",
        min_stars, max_stars, min_forks, max_forks
    );

    let client = Client::builder()
        .user_agent("bestof-opensource-scanner/1.0")
        .build()?;

    let url = format!(
        "https://api.github.com/search/repositories?q={}&sort=updated&order=desc&per_page=20",
        query
    );

    info!("📡 Fetching candidates from GitHub...");

    let response = client
        .get(&url)
        .header("Authorization", format!("Bearer {}", token))
        .header("Accept", "application/vnd.github+json")
        .send()
        .await?;

    if !response.status().is_success() {
        return Err(format!("GitHub API error: {}", response.status()).into());
    }

    let search_result: SearchResponse = response.json().await?;
    
    info!("✅ Found {} candidate repositories", search_result.items.len());

    let repos: Vec<(String, Metadata)> = search_result
        .items
        .into_iter()
        .take(10)
        .map(|r| {
            (
                r.full_name.clone(),
                Metadata {
                    stars: r.stars,
                    forks: r.forks,
                    language: r.language,
                    created_at: r.created_at,
                    last_push: r.pushed_at,
                },
            )
        })
        .collect();

    Ok(repos)
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    env_logger::init();

    let token = env::var("GITHUB_TOKEN")
        .expect("GITHUB_TOKEN environment variable not set");

    let tier = env::args().nth(1).unwrap_or_else(|| "small".to_string());
    let max_repos: usize = env::args()
        .nth(2)
        .and_then(|s| s.parse().ok())
        .unwrap_or(2);

    info!("🚀 HIDDEN GEMS PIPELINE STARTING");
    info!("   Tier: {}", tier);
    info!("   Target: {} quality repos", max_repos);
    info!("   Parallelism: Rayon enabled");
    info!("================================================================================");

    // Phase 1: Scan for candidates
    info!("📍 PHASE 1: Scanning for candidates...");
    let candidates = scan_repositories(&token, &tier).await?;
    info!("✅ Phase 1 complete: {} candidates\n", candidates.len());

    // Phase 2: Parallel analysis with Rayon
    info!("📍 PHASE 2: Analyzing repositories in parallel...");
    let analyzer = GemAnalyzer::new(token.clone());
    let mut analyses = analyzer.analyze_repos_parallel(candidates).await;
    
    // Sort by score
    analyses.sort_by(|a, b| b.total_score.partial_cmp(&a.total_score).unwrap());
    
    let approved: Vec<_> = analyses
        .iter()
        .filter(|a| a.recommendation == "APPROVE")
        .take(max_repos)
        .collect();

    info!("✅ Phase 2 complete:");
    info!("   - {} analyzed", analyses.len());
    info!("   - {} approved", approved.len());
    info!("   - {} for review", analyses.iter().filter(|a| a.recommendation == "REVIEW").count());
    println!();

    // Phase 3: AI Review (optional, for approved repos)
    if env::var("ENABLE_AI_REVIEW").is_ok() {
        info!("📍 PHASE 3: Running AI reviews in parallel...");
        let ai_reviewer = AIReviewer::new(token.clone());
        
        let client = Client::builder()
            .user_agent("bestof-opensource/1.0")
            .build()?;

        // Fetch READMEs first
        let mut readme_tasks = Vec::new();
        for analysis in approved.iter() {
            let repo = analysis.repo.clone();
            let client_clone = client.clone();
            let token_clone = token.clone();
            
            readme_tasks.push(tokio::spawn(async move {
                (repo.clone(), fetch_readme(&client_clone, &token_clone, &repo).await)
            }));
        }

        let readmes: Vec<(String, Option<String>)> = futures::future::join_all(readme_tasks)
            .await
            .into_iter()
            .filter_map(|r| r.ok())
            .collect();

        // Run AI reviews in parallel with Rayon
        let ai_reviews: Vec<_> = readmes
            .par_iter()
            .filter_map(|(repo, readme)| {
                if let Some(readme_content) = readme {
                    let rt = tokio::runtime::Runtime::new().ok()?;
                    let analysis = analyses.iter().find(|a| &a.repo == repo)?;
                    
                    match rt.block_on(ai_reviewer.review_repository(
                        repo,
                        readme_content,
                        &analysis.metadata.language,
                        analysis.metadata.stars,
                    )) {
                        Ok(review) => Some((repo.clone(), review)),
                        Err(e) => {
                            error!("AI review failed for {}: {}", repo, e);
                            None
                        }
                    }
                } else {
                    None
                }
            })
            .collect();

        info!("✅ Phase 3 complete: {} AI reviews", ai_reviews.len());

        // Merge AI reviews back into analyses
        for (repo, review) in ai_reviews {
            if let Some(analysis) = analyses.iter_mut().find(|a| a.repo == repo) {
                let ai_quality = ai_reviewer.calculate_quality_score(&review);
                analysis.scores.ai_code_quality = Some(ai_quality);
                analysis.ai_review = Some(review);
                
                // Update total score with AI component (25% weight)
                analysis.total_score = (analysis.total_score * 0.75) + (ai_quality * 0.25);
            }
        }
    }

    // Output results as JSON
    info!("\n================================================================================");
    info!("🎉 PIPELINE COMPLETE!");
    info!("   Candidates scanned: {}", analyses.len());
    info!("   Approved: {}", analyses.iter().filter(|a| a.recommendation == "APPROVE").count());
    info!("   For review: {}", analyses.iter().filter(|a| a.recommendation == "REVIEW").count());
    info!("================================================================================\n");

    // Print JSON output
    println!("__RESULTS_JSON__");
    println!("{}", serde_json::to_string_pretty(&analyses)?);
    println!("__END_JSON__");

    Ok(())
}
