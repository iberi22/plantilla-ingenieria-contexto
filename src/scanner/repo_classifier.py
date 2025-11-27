import logging
from typing import Dict, Any, List

class RepoClassifier:
    """
    Classifies repositories to distinguish real projects from mocks, tutorials, and toys.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.negative_keywords = [
            "demo", "test", "example", "tutorial", "course", "starter",
            "template", "boilerplate", "assignment", "homework", "learn", "study"
        ]
        self.positive_files = [
            "package.json", "requirements.txt", "setup.py", "Cargo.toml",
            "go.mod", "pom.xml", "build.gradle", "Dockerfile", "Makefile"
        ]

    def classify_repo(self, repo_data: Dict[str, Any], insights: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify a repository and return a score and verdict.

        Args:
            repo_data: Basic GitHub repo metadata.
            insights: Advanced insights from InsightsCollector.

        Returns:
            Dict containing 'score' (0-100), 'is_real_project' (bool), and 'reasons' (list).
        """
        score = 50 # Base score
        reasons = []

        # 1. Metadata Checks
        desc = (repo_data.get("description") or "").lower()
        name = (repo_data.get("name") or "").lower()
        full_text = f"{name} {desc}"

        # Negative keywords
        for kw in self.negative_keywords:
            if kw in full_text:
                score -= 20
                reasons.append(f"Contains negative keyword: {kw}")

        # Description length
        if len(desc) > 100:
            score += 10
            reasons.append("Detailed description")
        elif len(desc) < 20:
            score -= 10
            reasons.append("Short description")

        # Topics
        if repo_data.get("topics"):
            score += 10
            reasons.append("Has topics")

        # License
        if repo_data.get("license"):
            score += 10
            reasons.append("Has license")

        # 2. Activity & Community (Insights)
        stars = repo_data.get("stargazers_count", 0)
        if stars > 100:
            score += 20
            reasons.append("High stars (>100)")
        elif stars > 10:
            score += 5

        contributors = insights.get("contributors_count", 0)
        if contributors > 1:
            score += 10
            reasons.append("Multiple contributors")
        else:
            score -= 5
            reasons.append("Single contributor")

        commit_activity = insights.get("commit_frequency_score", 0)
        if commit_activity > 5.0:
            score += 10
            reasons.append("High commit activity")
        elif commit_activity == 0:
            score -= 10
            reasons.append("No recent activity")

        health = insights.get("health_percentage", 0)
        if health > 50:
            score += 5

        # 3. Critical Checks (Overrides)
        # If it's archived, immediate penalty
        if repo_data.get("archived"):
            score = 0
            reasons.append("Archived")

        # Cap score
        score = max(0, min(100, score))

        # Verdict
        is_real = score >= 60

        return {
            "score": score,
            "is_real_project": is_real,
            "reasons": reasons
        }
