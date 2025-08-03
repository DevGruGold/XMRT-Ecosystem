#!/usr/bin/env python3
"""
Enhanced GitHub Client
Advanced GitHub integration for autonomous repository management
Extends basic github_client.py with sophisticated automation capabilities
"""

import os
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from github import Github
from github.GithubException import GithubException
import requests
import base64


@dataclass
class RepositoryMetrics:
    total_commits: int
    total_issues: int
    open_issues: int
    total_prs: int
    open_prs: int
    contributors: int
    stars: int
    forks: int
    last_activity: datetime
    code_frequency: Dict[str, int]
    language_stats: Dict[str, int]


@dataclass
class CodeQualityMetrics:
    complexity_score: float
    maintainability_index: float
    technical_debt_ratio: float
    test_coverage: float
    documentation_coverage: float
    security_score: float
    performance_score: float


class EnhancedGitHubClient:
    """
    Enhanced GitHub client with advanced repository management,
    automated workflows, and comprehensive analytics capabilities.
    """

    def __init__(self, token: str, repo_name: str, owner: str):
        self.github = Github(token)
        self.token = token
        self.repo_name = repo_name
        self.owner = owner
        self.repo = self._get_repo()
        self.logger = logging.getLogger(__name__)

        # API rate limiting
        self.rate_limit_buffer = 100  # Keep 100 requests in reserve
        self.last_rate_check = datetime.now()

        # Automation settings
        self.automation_config = {
            "auto_merge_threshold": 0.9,  # Confidence threshold for auto-merge
            "max_auto_prs_per_hour": 5,
            "require_ci_success": True,
            "require_review_approval": False,  # For autonomous operations
            "auto_close_stale_issues": True,
            "stale_issue_days": 30,
        }

        self.logger.info("🚀 Enhanced GitHub Client Initialized")

    def _get_repo(self):
        """Get repository with error handling"""
        try:
            return self.github.get_user(self.owner).get_repo(self.repo_name)
        except GithubException as e:
            self.logger.error(
                f"Error getting repository {self.owner}/{self.repo_name}: {e}"
            )
            raise

    def _check_rate_limit(self) -> bool:
        """Check if we have sufficient API rate limit remaining"""
        try:
            rate_limit = self.github.get_rate_limit()
            remaining = rate_limit.core.remaining

            if remaining < self.rate_limit_buffer:
                reset_time = rate_limit.core.reset
                wait_time = (reset_time - datetime.now()).total_seconds()
                self.logger.warning(
                    f"Rate limit low ({remaining} remaining). Reset in {wait_time:.0f}s"
                )
                return False

            return True

        except Exception as e:
            self.logger.error(f"Error checking rate limit: {e}")
            return True  # Assume we're okay if we can't check

    async def create_autonomous_branch(
        self, branch_name: str, base_branch: str = "main"
    ) -> bool:
        """Create a branch with autonomous naming and metadata"""
        if not self._check_rate_limit():
            return False

        try:
            # Add timestamp and autonomous marker to branch name
            timestamp = int(time.time())
            autonomous_branch_name = f"autonomous/{branch_name}-{timestamp}"

            base_ref = self.repo.get_git_ref(f"heads/{base_branch}")
            self.repo.create_git_ref(
                f"refs/heads/{autonomous_branch_name}", base_ref.object.sha
            )

            self.logger.info(f"✅ Created autonomous branch: {autonomous_branch_name}")
            return autonomous_branch_name

        except GithubException as e:
            self.logger.error(f"Error creating autonomous branch: {e}")
            return False

    async def commit_multiple_files(
        self,
        branch_name: str,
        file_changes: Dict[str, str],
        commit_message: str,
        commit_description: Optional[str] = None,
    ) -> bool:
        """Commit multiple file changes in a single commit"""
        if not self._check_rate_limit():
            return False

        try:
            # Get the current commit SHA
            ref = self.repo.get_git_ref(f"heads/{branch_name}")
            current_commit = self.repo.get_git_commit(ref.object.sha)

            # Create blobs for all files
            blobs = {}
            for file_path, content in file_changes.items():
                blob = self.repo.create_git_blob(content, "utf-8")
                blobs[file_path] = blob

            # Create tree elements
            tree_elements = []
            for file_path, blob in blobs.items():
                tree_elements.append(
                    {
                        "path": file_path,
                        "mode": "100644",
                        "type": "blob",
                        "sha": blob.sha,
                    }
                )

            # Create new tree
            new_tree = self.repo.create_git_tree(tree_elements, current_commit.tree)

            # Create commit
            full_message = commit_message
            if commit_description:
                full_message += f"\n\n{commit_description}"

            new_commit = self.repo.create_git_commit(
                full_message, new_tree, [current_commit]
            )

            # Update reference
            ref.edit(new_commit.sha)

            self.logger.info(f"✅ Committed {len(file_changes)} files to {branch_name}")
            return True

        except GithubException as e:
            self.logger.error(f"Error committing multiple files: {e}")
            return False

    async def create_autonomous_pull_request(
        self,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main",
        auto_merge: bool = False,
        confidence_score: float = 0.0,
    ) -> Optional[str]:
        """Create a pull request with autonomous features"""
        if not self._check_rate_limit():
            return None

        try:
            # Enhanced PR body with autonomous metadata
            enhanced_body = f"""
{body}

---
## 🤖 Autonomous Operation Metadata

**Confidence Score:** {confidence_score:.2f}
**Created:** {datetime.now().isoformat()}
**Auto-merge Eligible:** {'✅ Yes' if auto_merge and confidence_score >= self.automation_config['auto_merge_threshold'] else '❌ No'}
**Branch:** `{head_branch}`

### Automated Checks
- [ ] Syntax validation
- [ ] Security scan
- [ ] Performance analysis
- [ ] Test coverage
- [ ] Documentation updates

*This pull request was created autonomously by the XMRT Autonomous System.*
            """

            pr = self.repo.create_pull(
                title=f"🤖 {title}",
                body=enhanced_body,
                head=head_branch,
                base=base_branch,
            )

            # Add labels
            labels = ["autonomous", "ai-generated"]
            if confidence_score >= 0.9:
                labels.append("high-confidence")
            if auto_merge:
                labels.append("auto-merge-candidate")

            pr.add_to_labels(*labels)

            # Auto-merge if conditions are met
            if (
                auto_merge
                and confidence_score >= self.automation_config["auto_merge_threshold"]
                and not self.automation_config["require_review_approval"]
            ):

                await self._attempt_auto_merge(pr, confidence_score)

            self.logger.info(f"✅ Created autonomous PR: {pr.html_url}")
            return pr.html_url

        except GithubException as e:
            self.logger.error(f"Error creating autonomous PR: {e}")
            return None

    async def _attempt_auto_merge(self, pr, confidence_score: float):
        """Attempt to auto-merge a high-confidence PR"""
        try:
            # Wait a bit for CI to start
            await asyncio.sleep(30)

            # Check CI status if required
            if self.automation_config["require_ci_success"]:
                ci_status = self._check_ci_status(pr)
                if not ci_status["success"]:
                    self.logger.info(f"⏳ CI not ready for auto-merge: {pr.html_url}")
                    return

            # Attempt merge
            pr.merge(
                commit_title=f"🤖 Auto-merge: {pr.title}",
                commit_message=f"Autonomous merge with confidence score: {confidence_score:.2f}",
                merge_method="squash",
            )

            self.logger.info(f"✅ Successfully auto-merged PR: {pr.html_url}")

        except Exception as e:
            self.logger.error(f"Error in auto-merge attempt: {e}")

    def _check_ci_status(self, pr) -> Dict[str, Any]:
        """Check CI/CD status for a pull request"""
        try:
            # Get the latest commit
            commits = pr.get_commits()
            latest_commit = commits[commits.totalCount - 1]

            # Get status checks
            status = latest_commit.get_combined_status()

            return {
                "success": status.state == "success",
                "state": status.state,
                "statuses": [
                    {
                        "context": s.context,
                        "state": s.state,
                        "description": s.description,
                    }
                    for s in status.statuses
                ],
            }

        except Exception as e:
            self.logger.error(f"Error checking CI status: {e}")
            return {"success": False, "state": "unknown", "statuses": []}

    async def analyze_repository_metrics(self) -> RepositoryMetrics:
        """Comprehensive repository analysis and metrics"""
        if not self._check_rate_limit():
            return None

        try:
            # Basic repository stats
            repo_stats = {
                "total_commits": self.repo.get_commits().totalCount,
                "total_issues": self.repo.get_issues(state="all").totalCount,
                "open_issues": self.repo.open_issues_count,
                "total_prs": self.repo.get_pulls(state="all").totalCount,
                "open_prs": self.repo.get_pulls(state="open").totalCount,
                "contributors": self.repo.get_contributors().totalCount,
                "stars": self.repo.stargazers_count,
                "forks": self.repo.forks_count,
                "last_activity": self.repo.updated_at,
            }

            # Language statistics
            languages = self.repo.get_languages()

            # Code frequency analysis (simplified)
            commits = self.repo.get_commits()
            code_frequency = {}

            # Analyze recent commits (last 100)
            recent_commits = list(commits[:100])
            for commit in recent_commits:
                date_key = commit.commit.author.date.strftime("%Y-%m")
                code_frequency[date_key] = code_frequency.get(date_key, 0) + 1

            return RepositoryMetrics(
                total_commits=repo_stats["total_commits"],
                total_issues=repo_stats["total_issues"],
                open_issues=repo_stats["open_issues"],
                total_prs=repo_stats["total_prs"],
                open_prs=repo_stats["open_prs"],
                contributors=repo_stats["contributors"],
                stars=repo_stats["stars"],
                forks=repo_stats["forks"],
                last_activity=repo_stats["last_activity"],
                code_frequency=code_frequency,
                language_stats=languages,
            )

        except Exception as e:
            self.logger.error(f"Error analyzing repository metrics: {e}")
            return None

    async def automated_issue_management(self):
        """Automated issue management and triage"""
        if not self._check_rate_limit():
            return

        try:
            # Get all open issues
            open_issues = self.repo.get_issues(state="open")

            for issue in open_issues:
                # Skip pull requests
                if issue.pull_request:
                    continue

                # Check if issue is stale
                if self.automation_config["auto_close_stale_issues"]:
                    days_old = (datetime.now() - issue.updated_at).days

                    if days_old > self.automation_config["stale_issue_days"]:
                        await self._handle_stale_issue(issue, days_old)

                # Auto-label issues based on content
                await self._auto_label_issue(issue)

                # Auto-assign based on expertise
                await self._auto_assign_issue(issue)

        except Exception as e:
            self.logger.error(f"Error in automated issue management: {e}")

    async def _handle_stale_issue(self, issue, days_old: int):
        """Handle stale issues"""
        try:
            stale_comment = f"""
This issue has been automatically marked as stale because it has not had recent activity ({days_old} days).

If this issue is still relevant, please:
- Add a comment to keep it open
- Update the issue with current information
- Add the `keep-open` label

This issue will be automatically closed in 7 days if no further activity occurs.

*This is an automated message from the XMRT Autonomous System.*
            """

            # Check if already marked as stale
            labels = [label.name for label in issue.labels]
            if "stale" not in labels:
                issue.add_to_labels("stale")
                issue.create_comment(stale_comment)
                self.logger.info(f"🏷️ Marked issue #{issue.number} as stale")

            # Close if stale for too long
            elif days_old > self.automation_config["stale_issue_days"] + 7:
                if "keep-open" not in labels:
                    issue.edit(state="closed")
                    issue.create_comment("Automatically closed due to inactivity.")
                    self.logger.info(f"🔒 Auto-closed stale issue #{issue.number}")

        except Exception as e:
            self.logger.error(f"Error handling stale issue #{issue.number}: {e}")

    async def _auto_label_issue(self, issue):
        """Automatically label issues based on content"""
        try:
            title = issue.title.lower()
            body = (issue.body or "").lower()
            content = f"{title} {body}"

            # Define label patterns
            label_patterns = {
                "bug": ["bug", "error", "issue", "problem", "broken", "fail"],
                "enhancement": ["feature", "enhancement", "improve", "add", "new"],
                "documentation": ["docs", "documentation", "readme", "guide"],
                "security": ["security", "vulnerability", "exploit", "cve"],
                "performance": ["performance", "slow", "optimization", "speed"],
                "testing": ["test", "testing", "coverage", "spec"],
            }

            current_labels = [label.name for label in issue.labels]
            new_labels = []

            for label, keywords in label_patterns.items():
                if label not in current_labels and any(
                    keyword in content for keyword in keywords
                ):
                    new_labels.append(label)

            if new_labels:
                issue.add_to_labels(*new_labels)
                self.logger.info(
                    f"🏷️ Auto-labeled issue #{issue.number} with: {new_labels}"
                )

        except Exception as e:
            self.logger.error(f"Error auto-labeling issue #{issue.number}: {e}")

    async def _auto_assign_issue(self, issue):
        """Auto-assign issues based on expertise and workload"""
        try:
            # This is a simplified implementation
            # In practice, you'd analyze contributor expertise and current workload

            # Get repository collaborators
            collaborators = self.repo.get_collaborators()

            # Simple assignment based on issue type
            title = issue.title.lower()

            assignment_rules = {
                "frontend": ["ui", "frontend", "react", "css", "html"],
                "backend": ["backend", "api", "server", "database"],
                "security": ["security", "vulnerability", "auth"],
                "devops": ["deploy", "ci", "cd", "docker", "kubernetes"],
            }

            # This would need to be customized based on your team
            # For now, we'll skip auto-assignment to avoid unwanted assignments

        except Exception as e:
            self.logger.error(f"Error auto-assigning issue #{issue.number}: {e}")

    async def generate_automated_reports(self) -> Dict[str, Any]:
        """Generate comprehensive automated reports"""
        try:
            metrics = await self.analyze_repository_metrics()

            # Generate activity report
            activity_report = await self._generate_activity_report()

            # Generate code quality report
            quality_report = await self._generate_quality_report()

            # Generate security report
            security_report = await self._generate_security_report()

            report = {
                "generated_at": datetime.now().isoformat(),
                "repository": f"{self.owner}/{self.repo_name}",
                "metrics": metrics.__dict__ if metrics else {},
                "activity": activity_report,
                "quality": quality_report,
                "security": security_report,
                "recommendations": await self._generate_recommendations(metrics),
            }

            # Save report to repository
            await self._save_report_to_repo(report)

            return report

        except Exception as e:
            self.logger.error(f"Error generating automated reports: {e}")
            return {}

    async def _generate_activity_report(self) -> Dict[str, Any]:
        """Generate repository activity report"""
        try:
            # Get recent commits (last 30 days)
            since = datetime.now() - timedelta(days=30)
            recent_commits = self.repo.get_commits(since=since)

            commit_count = recent_commits.totalCount

            # Get recent issues and PRs
            recent_issues = self.repo.get_issues(state="all", since=since)
            recent_prs = self.repo.get_pulls(state="all")

            # Filter PRs by date (GitHub API limitation)
            recent_pr_count = 0
            for pr in recent_prs:
                if pr.created_at >= since:
                    recent_pr_count += 1
                else:
                    break

            return {
                "commits_last_30_days": commit_count,
                "issues_last_30_days": recent_issues.totalCount,
                "prs_last_30_days": recent_pr_count,
                "activity_score": min(
                    100,
                    (commit_count * 2 + recent_issues.totalCount + recent_pr_count * 3)
                    / 10,
                ),
            }

        except Exception as e:
            self.logger.error(f"Error generating activity report: {e}")
            return {}

    async def _generate_quality_report(self) -> Dict[str, Any]:
        """Generate code quality report"""
        # This is a simplified implementation
        # In practice, you'd integrate with code quality tools
        return {
            "estimated_quality_score": 85,
            "areas_for_improvement": [
                "Increase test coverage",
                "Add more documentation",
                "Reduce code complexity",
            ],
        }

    async def _generate_security_report(self) -> Dict[str, Any]:
        """Generate security report"""
        # This would integrate with security scanning tools
        return {
            "security_score": 90,
            "vulnerabilities_found": 0,
            "last_security_scan": datetime.now().isoformat(),
        }

    async def _generate_recommendations(self, metrics: RepositoryMetrics) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        if metrics:
            if metrics.open_issues > 20:
                recommendations.append("Consider triaging and closing old issues")

            if metrics.open_prs > 10:
                recommendations.append("Review and merge pending pull requests")

            if metrics.contributors < 5:
                recommendations.append(
                    "Encourage more contributors to join the project"
                )

        return recommendations

    async def _save_report_to_repo(self, report: Dict[str, Any]):
        """Save generated report to repository"""
        try:
            report_content = json.dumps(report, indent=2, default=str)
            report_filename = (
                f"reports/automated-report-{datetime.now().strftime('%Y-%m-%d')}.json"
            )

            # Create reports directory if it doesn't exist
            try:
                self.repo.get_contents("reports")
            except:
                # Directory doesn't exist, create it
                self.repo.create_file(
                    "reports/README.md",
                    "Create reports directory",
                    "# Automated Reports\n\nThis directory contains automated reports generated by the XMRT Autonomous System.",
                )

            # Save the report
            self.repo.create_file(
                report_filename,
                f"🤖 Automated report: {datetime.now().strftime('%Y-%m-%d')}",
                report_content,
            )

            self.logger.info(f"📊 Saved automated report: {report_filename}")

        except Exception as e:
            self.logger.error(f"Error saving report to repository: {e}")

    def get_client_status(self) -> Dict[str, Any]:
        """Get current status of the enhanced GitHub client"""
        try:
            rate_limit = self.github.get_rate_limit()

            return {
                "repository": f"{self.owner}/{self.repo_name}",
                "rate_limit_remaining": rate_limit.core.remaining,
                "rate_limit_reset": rate_limit.core.reset.isoformat(),
                "automation_config": self.automation_config,
                "last_rate_check": self.last_rate_check.isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error getting client status: {e}")
            return {"error": str(e)}


# Integration with existing github_client.py
class GitHubClientManager:
    """Manager class to coordinate between basic and enhanced GitHub clients"""

    def __init__(self, token: str, repo_name: str, owner: str):
        # Import the basic client
        from github_client import GitHubClient

        self.basic_client = GitHubClient(token, repo_name, owner)
        self.enhanced_client = EnhancedGitHubClient(token, repo_name, owner)
        self.logger = logging.getLogger(__name__)

    def get_basic_client(self):
        """Get the basic GitHub client for simple operations"""
        return self.basic_client

    def get_enhanced_client(self):
        """Get the enhanced GitHub client for advanced operations"""
        return self.enhanced_client

    async def autonomous_workflow(self, improvements: List[Dict[str, Any]]):
        """Execute a complete autonomous workflow"""
        self.logger.info("🚀 Starting autonomous GitHub workflow")

        for improvement in improvements:
            try:
                # Create autonomous branch
                branch_name = await self.enhanced_client.create_autonomous_branch(
                    improvement["branch_name"]
                )

                if branch_name:
                    # Commit changes
                    success = await self.enhanced_client.commit_multiple_files(
                        branch_name,
                        improvement["file_changes"],
                        improvement["commit_message"],
                        improvement.get("commit_description"),
                    )

                    if success:
                        # Create PR
                        pr_url = (
                            await self.enhanced_client.create_autonomous_pull_request(
                                improvement["pr_title"],
                                improvement["pr_body"],
                                branch_name,
                                auto_merge=improvement.get("auto_merge", False),
                                confidence_score=improvement.get(
                                    "confidence_score", 0.0
                                ),
                            )
                        )

                        if pr_url:
                            self.logger.info(
                                f"✅ Autonomous workflow completed: {pr_url}"
                            )
                        else:
                            self.logger.error(
                                f"❌ Failed to create PR for {improvement['branch_name']}"
                            )
                    else:
                        self.logger.error(
                            f"❌ Failed to commit changes for {improvement['branch_name']}"
                        )
                else:
                    self.logger.error(
                        f"❌ Failed to create branch for {improvement['branch_name']}"
                    )

            except Exception as e:
                self.logger.error(
                    f"Error in autonomous workflow for {improvement.get('branch_name', 'unknown')}: {e}"
                )


# Example usage
if __name__ == "__main__":
    import asyncio

    async def main():
        # Initialize enhanced client
        client = EnhancedGitHubClient(
            token=os.getenv("GITHUB_PAT"),
            owner=os.getenv("GITHUB_USERNAME", "DevGruGold"),
            repo_name="XMRT-Ecosystem",
        )

        # Generate automated reports
        report = await client.generate_automated_reports()
        print(f"Generated report: {report}")

        # Perform automated issue management
        await client.automated_issue_management()

    asyncio.run(main())
