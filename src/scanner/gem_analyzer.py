"""
Hidden Gems Analyzer - Deep analysis for quality low-visibility projects
"""
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class GemAnalyzer:
    """Analyzes repositories to find hidden gems"""

    def __init__(self, github_client):
        self.client = github_client
        
    def analyze_repo(self, repo_full_name: str) -> Dict:
        """
        Perform deep analysis on a repository
        Returns scoring and recommendation
        """
        logger.info(f"🔍 Analyzing {repo_full_name} for hidden gem potential...")
        
        try:
            repo = self.client.get_repo(repo_full_name)
            
            # Gather all metrics
            commit_score, commit_data = self._analyze_commits(repo)
            quality_score, quality_data = self._analyze_code_quality(repo)
            engagement_score, engagement_data = self._analyze_engagement(repo)
            maturity_score, maturity_data = self._analyze_maturity(repo)
            
            # Calculate weighted total score
            total_score = (
                commit_score * 0.30 +
                quality_score * 0.25 +
                engagement_score * 0.25 +
                maturity_score * 0.20
            )
            
            # Determine recommendation
            if total_score >= 75:
                recommendation = "APPROVE"
                priority = "HIGH"
            elif total_score >= 60:
                recommendation = "REVIEW"
                priority = "MEDIUM"
            else:
                recommendation = "REJECT"
                priority = "LOW"
            
            result = {
                "repo": repo_full_name,
                "total_score": round(total_score, 2),
                "recommendation": recommendation,
                "priority": priority,
                "scores": {
                    "commit_activity": round(commit_score, 2),
                    "code_quality": round(quality_score, 2),
                    "developer_engagement": round(engagement_score, 2),
                    "project_maturity": round(maturity_score, 2)
                },
                "data": {
                    "commits": commit_data,
                    "quality": quality_data,
                    "engagement": engagement_data,
                    "maturity": maturity_data
                },
                "metadata": {
                    "stars": repo.stargazers_count,
                    "forks": repo.forks_count,
                    "language": repo.language,
                    "created_at": repo.created_at.isoformat(),
                    "updated_at": repo.updated_at.isoformat()
                }
            }
            
            logger.info(f"✅ Analysis complete: {total_score:.2f}/100 - {recommendation}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze {repo_full_name}: {e}")
            return None
    
    def _analyze_commits(self, repo) -> Tuple[float, Dict]:
        """Analyze commit activity and quality"""
        try:
            commits = list(repo.get_commits()[:50])  # Last 50 commits
            
            if len(commits) < 10:
                return 0, {"reason": "Too few commits"}
            
            # Calculate commit frequency
            six_months_ago = datetime.now() - timedelta(days=180)
            recent_commits = [c for c in commits if c.commit.author.date > six_months_ago]
            commits_per_week = len(recent_commits) / 26  # ~26 weeks in 6 months
            
            # Check for negative keywords in recent commits
            negative_keywords = ["alpha", "test", "wip", "beta", "experimental", "todo", "fix typo"]
            messages = [c.commit.message.lower() for c in recent_commits[:20]]
            
            negative_count = sum(
                1 for msg in messages 
                if any(kw in msg for kw in negative_keywords)
            )
            negative_ratio = negative_count / len(messages) if messages else 1
            
            # Check message quality (length and descriptiveness)
            avg_message_length = sum(len(c.commit.message) for c in recent_commits) / len(recent_commits)
            descriptive_messages = sum(
                1 for c in recent_commits 
                if len(c.commit.message.split()) >= 3  # At least 3 words
            )
            descriptive_ratio = descriptive_messages / len(recent_commits)
            
            # Check author diversity
            authors = set(c.commit.author.name for c in commits if c.commit.author)
            author_diversity = min(len(authors) / 5, 1.0)  # Max score at 5+ authors
            
            # Scoring
            frequency_score = min(commits_per_week / 5, 1.0) * 30  # Max at 5 commits/week
            quality_score = (1 - negative_ratio) * 30  # Penalty for negative keywords
            message_score = min(avg_message_length / 50, 1.0) * descriptive_ratio * 20
            diversity_score = author_diversity * 20
            
            total = frequency_score + quality_score + message_score + diversity_score
            
            data = {
                "total_commits": len(commits),
                "recent_commits": len(recent_commits),
                "commits_per_week": round(commits_per_week, 2),
                "negative_ratio": round(negative_ratio, 2),
                "avg_message_length": round(avg_message_length, 1),
                "descriptive_ratio": round(descriptive_ratio, 2),
                "unique_authors": len(authors),
                "breakdown": {
                    "frequency": round(frequency_score, 2),
                    "quality": round(quality_score, 2),
                    "messages": round(message_score, 2),
                    "diversity": round(diversity_score, 2)
                }
            }
            
            return total, data
            
        except Exception as e:
            logger.error(f"Error analyzing commits: {e}")
            return 0, {"error": str(e)}
    
    def _analyze_code_quality(self, repo) -> Tuple[float, Dict]:
        """Analyze code structure and quality indicators"""
        try:
            score = 0
            data = {}
            
            # README quality (0-25 points)
            try:
                readme = repo.get_readme()
                readme_content = readme.decoded_content.decode('utf-8')
                readme_length = len(readme_content)
                
                readme_score = min(readme_length / 2000, 1.0) * 25  # Max at 2000 chars
                score += readme_score
                data["readme_length"] = readme_length
                data["readme_score"] = round(readme_score, 2)
            except:
                data["readme_score"] = 0
            
            # License (0-15 points)
            if repo.license:
                score += 15
                data["has_license"] = True
                data["license"] = repo.license.name
            else:
                data["has_license"] = False
            
            # Project structure (0-25 points)
            try:
                contents = repo.get_contents("")
                file_names = [c.name for c in contents]
                dir_names = [c.name for c in contents if c.type == "dir"]
                
                structure_score = 0
                
                # Check for standard directories
                if "src" in dir_names or "lib" in dir_names:
                    structure_score += 8
                    data["has_src_dir"] = True
                
                if "tests" in dir_names or "test" in dir_names or any("test" in f for f in file_names):
                    structure_score += 8
                    data["has_tests"] = True
                
                if "docs" in dir_names or "documentation" in dir_names:
                    structure_score += 5
                    data["has_docs_dir"] = True
                
                # Check for important files
                if "CONTRIBUTING.md" in file_names or "CONTRIBUTING" in file_names:
                    structure_score += 4
                    data["has_contributing"] = True
                
                score += structure_score
                data["structure_score"] = round(structure_score, 2)
                
            except:
                data["structure_score"] = 0
            
            # CI/CD (0-20 points)
            try:
                workflows_dir = repo.get_contents(".github/workflows")
                if workflows_dir:
                    score += 20
                    data["has_ci_cd"] = True
                    data["workflow_count"] = len(workflows_dir) if isinstance(workflows_dir, list) else 1
            except:
                try:
                    # Check for other CI configs
                    root_contents = repo.get_contents("")
                    ci_files = [".travis.yml", ".circleci", "azure-pipelines.yml", ".gitlab-ci.yml"]
                    has_ci = any(c.name in ci_files for c in root_contents)
                    if has_ci:
                        score += 15
                        data["has_ci_cd"] = True
                except:
                    data["has_ci_cd"] = False
            
            # Language-specific quality indicators (0-15 points)
            lang_score = self._analyze_language_specifics(repo)
            score += lang_score
            data["language_specific_score"] = round(lang_score, 2)
            
            return score, data
            
        except Exception as e:
            logger.error(f"Error analyzing code quality: {e}")
            return 0, {"error": str(e)}
    
    def _analyze_language_specifics(self, repo) -> float:
        """Check language-specific quality indicators"""
        lang = repo.language
        if not lang:
            return 0
        
        try:
            contents = repo.get_contents("")
            file_names = [c.name for c in contents]
            
            score = 0
            
            if lang == "Python":
                if "setup.py" in file_names or "pyproject.toml" in file_names:
                    score += 5
                if "requirements.txt" in file_names or "Pipfile" in file_names:
                    score += 5
                if "tox.ini" in file_names or "pytest.ini" in file_names:
                    score += 5
                    
            elif lang == "JavaScript" or lang == "TypeScript":
                if "package.json" in file_names:
                    score += 5
                if "tsconfig.json" in file_names:
                    score += 5
                if ".eslintrc" in file_names or ".eslintrc.js" in file_names:
                    score += 5
                    
            elif lang == "Rust":
                if "Cargo.toml" in file_names:
                    score += 10
                if "Cargo.lock" in file_names:
                    score += 5
                    
            elif lang in ["Go", "Java", "C++", "C#"]:
                # Generic checks for compiled languages
                score += 5  # Base score for having a compiled language
            
            return score
            
        except:
            return 0
    
    def _analyze_engagement(self, repo) -> Tuple[float, Dict]:
        """Analyze developer responsiveness and community engagement"""
        try:
            score = 0
            data = {}
            
            # Issues analysis (0-50 points)
            try:
                open_issues = repo.open_issues_count
                closed_issues_list = list(repo.get_issues(state='closed')[:30])
                
                if closed_issues_list:
                    # Calculate average response time
                    response_times = []
                    for issue in closed_issues_list[:10]:
                        if issue.comments > 0:
                            comments = list(issue.get_comments()[:1])
                            if comments:
                                time_to_response = (comments[0].created_at - issue.created_at).days
                                response_times.append(time_to_response)
                    
                    if response_times:
                        avg_response_time = sum(response_times) / len(response_times)
                        # Score: <1 day = 25pts, <3 days = 20pts, <7 days = 15pts, <14 days = 10pts
                        if avg_response_time < 1:
                            score += 25
                        elif avg_response_time < 3:
                            score += 20
                        elif avg_response_time < 7:
                            score += 15
                        elif avg_response_time < 14:
                            score += 10
                        
                        data["avg_response_days"] = round(avg_response_time, 2)
                    
                    # Closed ratio
                    total_issues = len(closed_issues_list) + open_issues
                    closed_ratio = len(closed_issues_list) / total_issues if total_issues > 0 else 0
                    
                    ratio_score = closed_ratio * 25
                    score += ratio_score
                    
                    data["closed_ratio"] = round(closed_ratio, 2)
                    data["open_issues"] = open_issues
                    data["closed_issues_sampled"] = len(closed_issues_list)
                    
            except Exception as e:
                logger.warning(f"Issues analysis failed: {e}")
                data["issues_error"] = str(e)
            
            # Pull Requests analysis (0-50 points)
            try:
                prs = list(repo.get_pulls(state='all')[:20])
                
                if prs:
                    merged_prs = [pr for pr in prs if pr.merged]
                    external_prs = [pr for pr in prs if pr.user.login != repo.owner.login]
                    
                    # Merge ratio
                    merge_ratio = len(merged_prs) / len(prs) if prs else 0
                    score += merge_ratio * 25
                    
                    # External contributions
                    external_ratio = len(external_prs) / len(prs) if prs else 0
                    score += external_ratio * 25
                    
                    data["pr_merge_ratio"] = round(merge_ratio, 2)
                    data["external_pr_ratio"] = round(external_ratio, 2)
                    data["total_prs_sampled"] = len(prs)
                    data["merged_prs"] = len(merged_prs)
                    data["external_prs"] = len(external_prs)
                    
            except Exception as e:
                logger.warning(f"PRs analysis failed: {e}")
                data["prs_error"] = str(e)
            
            return score, data
            
        except Exception as e:
            logger.error(f"Error analyzing engagement: {e}")
            return 0, {"error": str(e)}
    
    def _analyze_maturity(self, repo) -> Tuple[float, Dict]:
        """Analyze project maturity and stability"""
        try:
            score = 0
            data = {}
            
            # Releases (0-40 points)
            try:
                releases = list(repo.get_releases()[:10])
                
                if releases:
                    latest_release = releases[0]
                    version = latest_release.tag_name
                    
                    # Check for semantic versioning
                    if re.match(r'v?\d+\.\d+\.\d+', version):
                        data["has_semver"] = True
                        
                        # Parse version
                        version_parts = re.findall(r'\d+', version)
                        if version_parts:
                            major = int(version_parts[0])
                            if major >= 1:
                                score += 20  # v1.0+
                            else:
                                score += 10  # v0.x
                    
                    # Regular releases
                    if len(releases) >= 3:
                        score += 10
                        data["release_count"] = len(releases)
                    
                    # Recent release
                    days_since_release = (datetime.now() - latest_release.created_at.replace(tzinfo=None)).days
                    if days_since_release < 90:
                        score += 10
                        data["days_since_release"] = days_since_release
                    
                    data["latest_version"] = version
                    
            except:
                data["has_releases"] = False
            
            # Documentation (0-30 points)
            try:
                contents = repo.get_contents("")
                file_names = [c.name.lower() for c in contents]
                
                # Changelog
                if "changelog.md" in file_names or "changelog" in file_names:
                    score += 10
                    data["has_changelog"] = True
                
                # Examples
                if "examples" in file_names or "example" in file_names:
                    score += 10
                    data["has_examples"] = True
                
                # Documentation directory
                if "docs" in file_names:
                    docs_contents = repo.get_contents("docs")
                    if isinstance(docs_contents, list) and len(docs_contents) > 2:
                        score += 10
                        data["has_detailed_docs"] = True
                        
            except:
                pass
            
            # Age and stability (0-30 points)
            age_days = (datetime.now() - repo.created_at.replace(tzinfo=None)).days
            
            if age_days > 365:  # > 1 year
                score += 15
            elif age_days > 180:  # > 6 months
                score += 10
            elif age_days > 90:  # > 3 months
                score += 5
            
            data["age_days"] = age_days
            
            # Activity (can be stable without recent changes)
            days_since_update = (datetime.now() - repo.updated_at.replace(tzinfo=None)).days
            
            if days_since_update < 30:
                score += 15  # Very active
            elif days_since_update < 90:
                score += 10  # Active
            elif days_since_update < 180:
                score += 5   # Moderate
            # No penalty for older but stable projects
            
            data["days_since_update"] = days_since_update
            
            return score, data
            
        except Exception as e:
            logger.error(f"Error analyzing maturity: {e}")
            return 0, {"error": str(e)}
    
    def has_red_flags(self, repo) -> Tuple[bool, List[str]]:
        """Check for automatic rejection criteria"""
        red_flags = []
        
        try:
            # No activity in >6 months
            six_months_ago = datetime.now() - timedelta(days=180)
            if repo.updated_at.replace(tzinfo=None) < six_months_ago:
                red_flags.append("No activity in >6 months")
            
            # Very short README
            try:
                readme = repo.get_readme()
                if len(readme.decoded_content) < 200:
                    red_flags.append("README too short (<200 chars)")
            except:
                red_flags.append("No README found")
            
            # No license
            if not repo.license:
                red_flags.append("No open source license")
            
            # Check issues response rate
            try:
                issues = list(repo.get_issues(state='open')[:20])
                if len(issues) > 10:
                    responded = sum(1 for i in issues if i.comments > 0)
                    response_rate = responded / len(issues)
                    if response_rate < 0.3:  # <30% responded
                        red_flags.append("Poor issue response rate (<30%)")
            except:
                pass
            
            return len(red_flags) > 0, red_flags
            
        except Exception as e:
            logger.error(f"Error checking red flags: {e}")
            return False, []
