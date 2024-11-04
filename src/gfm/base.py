"""Core implementation of GitFlowManager, can be used directly or wrapped by LLM tools."""

import subprocess
from pathlib import Path
from typing import List, Optional


class GitFlowManager:
    """
    A class to manage a Git repository using a GitFlow approach. Facilitates feature, release, and hotfix branches
    along with standard repository management tasks.

    This implementation interacts directly with the Git command-line interface (CLI) and supports operations
    such as branch creation, deletion, merges, and tagging according to GitFlow methodology.

    Attributes:
        repo_path (Path): The path to the Git repository.

    Example:
        ```python
        manager = GitFlowManager(repo_path="path/to/repo")
        manager.init()
        manager.create_feature_branch("feature/my-new-feature")
        ```

    <!-- Example Test:
    >>> manager = GitFlowManager(repo_path="path/to/repo")
    >>> manager.init()
    >>> assert manager.get_current_branch() == "main"
    -->
    """

    def __init__(self, repo_path: str):
        """
        Initializes the GitFlowManager with the path to the Git repository.

        Args:
            repo_path (str): Path to the Git repository.
        """
        self.repo_path = Path(repo_path)

    def _run_git_command(self, *args: str) -> str:
        """
        Run a Git command in the repository and return the output.

        Args:
            *args (str): Git command arguments.

        Returns:
            str: The output of the Git command.
        """
        result = subprocess.run(
            ["git", "-C", str(self.repo_path), *args],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()

    def init(self) -> None:
        """
        Initializes a Git repository at the specified path if not already initialized.

        Checks if the `.git` directory exists; if it does, no action is taken.
        Otherwise, initializes a new Git repository.

        Raises:
            RuntimeError: If Git initialization fails or if the directory does not exist.
        """
        if not self.repo_path.exists():
            raise RuntimeError(f"Repository path '{self.repo_path}' does not exist.")

        # Check if .git directory exists to confirm if the repo is already initialized
        git_dir = self.repo_path / ".git"
        if git_dir.exists():
            print(f"Repository already initialized at {self.repo_path}")
        else:
            try:
                self._run_git_command("init")
                print(f"Initialized a new Git repository at {self.repo_path}")
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Failed to initialize git repository: {e}")

    def get_current_branch(self) -> str:
        """
        Returns the name of the current branch.

        Returns:
            str: The current branch name.
        """
        return self._run_git_command("rev-parse", "--abbrev-ref", "HEAD")

    def create_branch(self, branch_name: str) -> None:
        """
        Creates a new branch.

        Args:
            branch_name (str): The name of the branch to create.
        """
        self._run_git_command("checkout", "-b", branch_name)

    def delete_branch(self, branch_name: str, force: bool = False) -> None:
        """
        Deletes a branch.

        Args:
            branch_name (str): The name of the branch to delete.
            force (bool): Whether to force delete the branch.
        """
        args = ["branch", "-d" if not force else "-D", branch_name]
        self._run_git_command(*args)

    def create_feature_branch(self, feature_name: str) -> None:
        """
        Creates a feature branch.

        Args:
            feature_name (str): The name of the feature branch.
        """
        self.create_branch(f"feature/{feature_name}")

    def create_release_branch(self, version: str) -> None:
        """
        Creates a release branch.

        Args:
            version (str): The version tag for the release.
        """
        self.create_branch(f"release/{version}")

    def create_hotfix_branch(self, hotfix_name: str) -> None:
        """
        Creates a hotfix branch.

        Args:
            hotfix_name (str): The name of the hotfix branch.
        """
        self.create_branch(f"hotfix/{hotfix_name}")

    def merge_branch(self, branch_name: str) -> None:
        """
        Merges a specified branch into the current branch.

        Args:
            branch_name (str): The name of the branch to merge.

        Raises:
            RuntimeError: If the merge operation fails.
        """
        try:
            self._run_git_command("merge", branch_name)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to merge branch '{branch_name}': {e}")

    def create_tag(self, tag_name: str, message: Optional[str] = None) -> None:
        """
        Creates a tag for the current commit.

        Args:
            tag_name (str): The name of the tag.
            message (Optional[str]): Tag message for annotated tags.
        """
        if message:
            self._run_git_command("tag", "-a", tag_name, "-m", message)
        else:
            self._run_git_command("tag", tag_name)

    def push(
        self,
        remote: str = "origin",
        branch_name: Optional[str] = None,
        tags: bool = False,
    ) -> None:
        """
        Pushes a branch or tags to the remote repository.

        Args:
            remote (str): The remote repository name (default: "origin").
            branch_name (Optional[str]): The branch to push (default: current branch).
            tags (bool): Whether to push all tags.
        """
        args = ["push", remote]
        if branch_name:
            args.append(branch_name)
        if tags:
            args.append("--tags")
        self._run_git_command(*args)
