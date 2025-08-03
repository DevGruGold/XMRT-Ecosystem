import os
from github import Github
from github.GithubException import GithubException
import logging


class GitHubClient:
    def __init__(self, token: str, repo_name: str, owner: str):
        self.github = Github(token)
        self.repo_name = repo_name
        self.owner = owner
        self.repo = self._get_repo()
        self.logger = logging.getLogger(__name__)

    def _get_repo(self):
        try:
            return self.github.get_user(self.owner).get_repo(self.repo_name)
        except GithubException as e:
            self.logger.error(
                f"Error getting repository {self.owner}/{self.repo_name}: {e}"
            )
            raise

    def create_branch(self, branch_name: str, base_branch: str = "main"):
        try:
            base_ref = self.repo.get_git_ref(f"heads/{base_branch}")
            self.repo.create_git_ref(f"refs/heads/{branch_name}", base_ref.object.sha)
            self.logger.info(
                f"Branch '{branch_name}' created successfully from '{base_branch}'."
            )
            return True
        except GithubException as e:
            self.logger.error(f"Error creating branch '{branch_name}': {e}")
            return False

    def commit_and_push(
        self, branch_name: str, file_path: str, content: str, commit_message: str
    ):
        try:
            contents = self.repo.get_contents(file_path, ref=branch_name)
            self.repo.update_file(
                contents.path, commit_message, content, contents.sha, branch=branch_name
            )
            self.logger.info(
                f"File '{file_path}' updated and committed to branch '{branch_name}'."
            )
            return True
        except GithubException as e:
            self.logger.error(
                f"Error committing file '{file_path}' to branch '{branch_name}': {e}"
            )
            return False
        except Exception as e:
            # If file does not exist, create it
            try:
                self.repo.create_file(
                    file_path, commit_message, content, branch=branch_name
                )
                self.logger.info(
                    f"File '{file_path}' created and committed to branch '{branch_name}'."
                )
                return True
            except GithubException as e:
                self.logger.error(
                    f"Error creating file '{file_path}' to branch '{branch_name}': {e}"
                )
                return False

    def create_pull_request(
        self, title: str, body: str, head_branch: str, base_branch: str = "main"
    ):
        try:
            pr = self.repo.create_pull(
                title=title, body=body, head=head_branch, base=base_branch
            )
            self.logger.info(f"Pull request '{pr.title}' created: {pr.html_url}")
            return pr.html_url
        except GithubException as e:
            self.logger.error(f"Error creating pull request: {e}")
            return None

    def get_issue(self, issue_number: int):
        try:
            issue = self.repo.get_issue(number=issue_number)
            return issue
        except GithubException as e:
            self.logger.error(f"Error getting issue {issue_number}: {e}")
            return None

    def comment_on_issue(self, issue_number: int, comment_body: str):
        try:
            issue = self.get_issue(issue_number)
            if issue:
                issue.create_comment(comment_body)
                self.logger.info(f"Comment added to issue {issue_number}.")
                return True
            return False
        except GithubException as e:
            self.logger.error(f"Error commenting on issue {issue_number}: {e}")
            return False

    def close_issue(self, issue_number: int):
        try:
            issue = self.get_issue(issue_number)
            if issue:
                issue.edit(state="closed")
                self.logger.info(f"Issue {issue_number} closed.")
                return True
            return False
        except GithubException as e:
            self.logger.error(f"Error closing issue {issue_number}: {e}")
            return False

    def get_file_content(self, file_path: str, ref: str = "main"):
        try:
            contents = self.repo.get_contents(file_path, ref=ref)
            return contents.decoded_content.decode()
        except GithubException as e:
            self.logger.error(
                f"Error getting content of file '{file_path}' from ref '{ref}': {e}"
            )
            return None
