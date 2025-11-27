#!/usr/bin/env python3
"""
Hidden Gems Pipeline - Complete workflow for discovering quality low-visibility projects
"""
import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from github import Github
from scanner.gem_analyzer import GemAnalyzer
from scanner.ai_reviewer import AIReviewer
from blog_generator.generator import BlogGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HiddenGemsPipeline:
    """Complete pipeline for discovering and publishing hidden gems"""
    
    def __init__(self, github_token: str, google_api_key: str):
        self.github_token = github_token
        self.google_api_key = google_api_key
        self.github_client = Github(github_token)
        self.analyzer = GemAnalyzer(self.github_client)
        self.ai_reviewer = AIReviewer(google_api_key)
        self.blog_generator = BlogGenerator(google_api_key)
        
        # Find Rust scanner
        self.rust_scanner_path = self._find_rust_scanner()
        
    def _find_rust_scanner(self) -> Optional[Path]:
        """Locate the hidden gems Rust scanner binary"""
        base_path = Path(__file__).parent.parent / "rust-scanner"
        
        possible_paths = [
            base_path / "target" / "release" / "hidden-gems-scanner.exe",
            base_path / "target" / "release" / "hidden-gems-scanner",
        ]
        
        for path in possible_paths:
            if path.exists():
                logger.info(f"✅ Found Rust scanner at {path}")
                return path
        
        logger.warning("⚠️  Rust scanner not found, will skip pre-filtering")
        return None
    
    def run_rust_scanner(self, tier: str = "small") -> List[Dict]:
        """Run Rust scanner to get initial candidate repos"""
        if not self.rust_scanner_path:
            logger.warning("Rust scanner not available")
            return []
        
        try:
            logger.info(f"🚀 Running Rust scanner for tier: {tier}")
            
            env = os.environ.copy()
            env["GITHUB_TOKEN"] = self.github_token
            env["RUST_LOG"] = "info"
            
            result = subprocess.run(
                [str(self.rust_scanner_path), tier],
                env=env,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                logger.error(f"Rust scanner failed: {result.stderr}")
                return []
            
            # Parse output
            output = result.stdout
            
            if "__REPO_JSON__" in output and "__END_JSON__" in output:
                json_start = output.index("__REPO_JSON__") + len("__REPO_JSON__")
                json_end = output.index("__END_JSON__")
                json_str = output[json_start:json_end].strip()
                
                repos = json.loads(json_str)
                logger.info(f"✅ Rust scanner found {len(repos)} candidate repositories")
                return repos
            
            logger.warning("No JSON output from Rust scanner")
            return []
            
        except subprocess.TimeoutExpired:
            logger.error("Rust scanner timed out")
            return []
        except Exception as e:
            logger.error(f"Error running Rust scanner: {e}")
            return []
    
    def analyze_candidate(self, repo_full_name: str) -> Optional[Dict]:
        """Run complete analysis on a candidate repository"""
        logger.info(f"\n{'='*80}")
        logger.info(f"🔍 ANALYZING: {repo_full_name}")
        logger.info(f"{'='*80}\n")
        
        try:
            repo = self.github_client.get_repo(repo_full_name)
            
            # Step 1: Check for red flags
            has_red_flags, flags = self.analyzer.has_red_flags(repo)
            if has_red_flags:
                logger.warning(f"🚩 RED FLAGS DETECTED: {', '.join(flags)}")
                return {
                    "repo": repo_full_name,
                    "status": "REJECTED",
                    "reason": "red_flags",
                    "details": flags
                }
            
            # Step 2: Deep analysis
            analysis = self.analyzer.analyze_repo(repo_full_name)
            if not analysis:
                logger.error("Analysis failed")
                return None
            
            logger.info(f"📊 Analysis Score: {analysis['total_score']:.2f}/100")
            logger.info(f"   - Commits: {analysis['scores']['commit_activity']}")
            logger.info(f"   - Quality: {analysis['scores']['code_quality']}")
            logger.info(f"   - Engagement: {analysis['scores']['developer_engagement']}")
            logger.info(f"   - Maturity: {analysis['scores']['project_maturity']}")
            
            # Step 3: AI Code Review (if analysis score is promising)
            if analysis['total_score'] >= 50:
                logger.info("\n🤖 Running AI code review...")
                
                # Get README
                try:
                    readme = repo.get_readme()
                    readme_content = readme.decoded_content.decode('utf-8')
                except:
                    readme_content = "No README available"
                
                # Get recent file samples
                recent_files = self._get_recent_files(repo)
                
                ai_scores = self.ai_reviewer.review_repository(
                    repo, 
                    readme_content, 
                    recent_files
                )
                
                if ai_scores:
                    ai_quality_score = self.ai_reviewer.calculate_quality_score(ai_scores)
                    analysis['scores']['ai_code_quality'] = ai_quality_score
                    analysis['ai_review'] = ai_scores
                    
                    # Update total score with AI review (25% weight)
                    original_score = analysis['total_score']
                    analysis['total_score'] = (
                        original_score * 0.75 + ai_quality_score * 0.25
                    )
                    
                    logger.info(f"🤖 AI Review Score: {ai_quality_score:.2f}/100")
                    logger.info(f"📈 Updated Total: {analysis['total_score']:.2f}/100")
                    
                    if ai_scores.get('summary'):
                        logger.info(f"💡 AI Summary: {ai_scores['summary']}")
            
            # Final recommendation
            logger.info(f"\n{'='*80}")
            logger.info(f"🎯 FINAL RESULT: {analysis['recommendation']} ({analysis['priority']} priority)")
            logger.info(f"{'='*80}\n")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing {repo_full_name}: {e}")
            return None
    
    def _get_recent_files(self, repo, max_files: int = 5) -> List[Dict]:
        """Get samples of recently modified files"""
        files = []
        
        try:
            commits = list(repo.get_commits()[:10])
            seen_paths = set()
            
            for commit in commits:
                if len(files) >= max_files:
                    break
                
                for file in commit.files:
                    if len(files) >= max_files:
                        break
                    
                    # Skip non-code files
                    if not self._is_code_file(file.filename):
                        continue
                    
                    # Skip already seen files
                    if file.filename in seen_paths:
                        continue
                    
                    seen_paths.add(file.filename)
                    
                    # Get file content
                    try:
                        content_file = repo.get_contents(file.filename)
                        if content_file.size < 10000:  # Skip large files
                            content = content_file.decoded_content.decode('utf-8')
                            
                            files.append({
                                "path": file.filename,
                                "language": self._detect_language(file.filename),
                                "content": content[:1000],  # First 1000 chars
                                "size": content_file.size
                            })
                    except:
                        continue
        
        except Exception as e:
            logger.warning(f"Error getting recent files: {e}")
        
        return files
    
    def _is_code_file(self, filename: str) -> bool:
        """Check if file is a code file"""
        code_extensions = [
            '.py', '.js', '.ts', '.jsx', '.tsx', '.rs', '.go', '.java',
            '.cpp', '.c', '.h', '.hpp', '.cs', '.rb', '.php', '.swift',
            '.kt', '.scala', '.r', '.m', '.mm', '.dart', '.vue'
        ]
        return any(filename.endswith(ext) for ext in code_extensions)
    
    def _detect_language(self, filename: str) -> str:
        """Detect language from filename"""
        ext_map = {
            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
            '.jsx': 'jsx', '.tsx': 'tsx', '.rs': 'rust', '.go': 'go',
            '.java': 'java', '.cpp': 'cpp', '.c': 'c', '.cs': 'csharp',
            '.rb': 'ruby', '.php': 'php', '.swift': 'swift', '.kt': 'kotlin'
        }
        
        for ext, lang in ext_map.items():
            if filename.endswith(ext):
                return lang
        
        return ''
    
    def generate_blog_post(self, analysis: Dict) -> Optional[Path]:
        """Generate blog post for approved hidden gem"""
        try:
            repo_name = analysis['repo']
            logger.info(f"📝 Generating blog post for {repo_name}...")
            
            repo = self.github_client.get_repo(repo_name)
            
            # Get README
            try:
                readme = repo.get_readme()
                readme_content = readme.decoded_content.decode('utf-8')
            except:
                readme_content = ""
            
            # Create repository data structure
            repo_data = {
                "full_name": repo.full_name,
                "name": repo.name,
                "description": repo.description or "",
                "html_url": repo.html_url,
                "stargazers_count": repo.stargazers_count,
                "forks_count": repo.forks_count,
                "language": repo.language,
                "topics": repo.get_topics(),
                "created_at": repo.created_at.isoformat(),
                "readme": readme_content[:5000],  # First 5000 chars
                "homepage": repo.homepage,
                "license": repo.license.name if repo.license else None,
            }
            
            # Add analysis insights to blog context
            blog_context = {
                "is_hidden_gem": True,
                "discovery_score": analysis['total_score'],
                "key_strengths": analysis.get('ai_review', {}).get('key_strengths', []),
                "analysis_scores": analysis['scores']
            }
            
            # Generate blog post
            blog_post = self.blog_generator.generate_blog_post(repo_data, blog_context)
            
            if blog_post:
                logger.info(f"✅ Blog post generated successfully")
                return blog_post
            
            logger.error("Blog generation failed")
            return None
            
        except Exception as e:
            logger.error(f"Error generating blog post: {e}")
            return None
    
    def run_pipeline(self, tier: str = "small", max_repos: int = 5):
        """Run complete hidden gems discovery pipeline"""
        logger.info("\n" + "="*80)
        logger.info("🚀 HIDDEN GEMS PIPELINE STARTING")
        logger.info(f"   Tier: {tier}")
        logger.info(f"   Target: {max_repos} quality repos")
        logger.info("="*80 + "\n")
        
        # Step 1: Rust scanner pre-filter
        candidates = self.run_rust_scanner(tier)
        
        if not candidates:
            logger.error("No candidates found by Rust scanner")
            return
        
        logger.info(f"\n✅ Phase 1 complete: {len(candidates)} candidates")
        
        # Step 2: Deep analysis
        approved_repos = []
        review_repos = []
        
        for candidate in candidates:
            if len(approved_repos) >= max_repos:
                break
            
            repo_name = candidate['full_name']
            analysis = self.analyze_candidate(repo_name)
            
            if analysis:
                if analysis.get('status') == 'REJECTED':
                    continue
                
                if analysis['recommendation'] == 'APPROVE':
                    approved_repos.append(analysis)
                elif analysis['recommendation'] == 'REVIEW':
                    review_repos.append(analysis)
        
        logger.info(f"\n✅ Phase 2 complete:")
        logger.info(f"   - {len(approved_repos)} approved")
        logger.info(f"   - {len(review_repos)} need review")
        
        # Step 3: Generate blog posts
        generated_posts = []
        
        for analysis in approved_repos:
            post_path = self.generate_blog_post(analysis)
            if post_path:
                generated_posts.append(post_path)
        
        logger.info(f"\n✅ Phase 3 complete: {len(generated_posts)} blog posts generated")
        
        # Summary
        logger.info("\n" + "="*80)
        logger.info("🎉 PIPELINE COMPLETE!")
        logger.info(f"   Candidates scanned: {len(candidates)}")
        logger.info(f"   Approved: {len(approved_repos)}")
        logger.info(f"   For review: {len(review_repos)}")
        logger.info(f"   Blog posts: {len(generated_posts)}")
        logger.info("="*80 + "\n")
        
        return {
            "candidates": len(candidates),
            "approved": approved_repos,
            "review": review_repos,
            "posts_generated": generated_posts
        }


def main():
    """Main entry point"""
    # Get credentials
    github_token = os.getenv("GITHUB_TOKEN")
    google_api_key = os.getenv("GOOGLE_API_KEY")
    
    if not github_token:
        logger.error("GITHUB_TOKEN not set")
        sys.exit(1)
    
    if not google_api_key:
        logger.error("GOOGLE_API_KEY not set")
        sys.exit(1)
    
    # Get tier from command line
    tier = sys.argv[1] if len(sys.argv) > 1 else "small"
    max_repos = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    # Run pipeline
    pipeline = HiddenGemsPipeline(github_token, google_api_key)
    results = pipeline.run_pipeline(tier, max_repos)
    
    # Save results
    results_file = Path(__file__).parent.parent / "output" / f"hidden_gems_{tier}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    results_file.parent.mkdir(exist_ok=True)
    
    with open(results_file, 'w') as f:
        json.dump({
            "tier": tier,
            "timestamp": datetime.now().isoformat(),
            "statistics": {
                "candidates": results["candidates"],
                "approved_count": len(results["approved"]),
                "review_count": len(results["review"]),
                "posts_count": len(results["posts_generated"])
            },
            "approved_repos": [r["repo"] for r in results["approved"]],
            "review_repos": [r["repo"] for r in results["review"]]
        }, f, indent=2)
    
    logger.info(f"📁 Results saved to {results_file}")


if __name__ == "__main__":
    main()
