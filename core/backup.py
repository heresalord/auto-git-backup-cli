# auto_git_backup/core/backup.py
import subprocess
from datetime import datetime
from pathlib import Path
from git import Repo, InvalidGitRepositoryError
from core.utils import list_modified_files
from rich.console import Console
from rich.prompt import Confirm

console = Console()


def is_git_repo(path="."):
    try:
        _ = Repo(path).git_dir
        return True
    except InvalidGitRepositoryError:
        return False


def run_backup_once(config):
    """Perform a Git backup with a timestamped commit message."""
    repo_path = config.get("project_path", ".")
    repo_path_obj = Path(repo_path)

    if not repo_path_obj.exists() or not repo_path_obj.is_dir():
        console.print(f"[red]Error: The project path '{repo_path}' does not exist or is not a directory.[/red]")
        return

    if not is_git_repo(repo_path):
        console.print(f"[yellow]Warning: The folder '{repo_path}' is not a Git repository.[/yellow]")
        if Confirm.ask("Do you want to initialize a new Git repository here now?"):
            try:
                subprocess.run(["git", "init"], cwd=repo_path, check=True)
                console.print(f"[green]Initialized a new Git repository at '{repo_path}'.[/green]")
            except Exception as e:
                console.print(f"[red]Failed to initialize Git repository: {e}[/red]")
                return
        else:
            console.print("[red]Backup aborted because no Git repository was found.[/red]")
            return

    try:
        repo = Repo(repo_path)
    except InvalidGitRepositoryError:
        console.print(f"[red]Error: Failed to load Git repository at '{repo_path}'.[/red]")
        return

    changed_files = list_modified_files(repo, config.get("watch_extensions", []), config.get("excluded_paths", []))

    if not changed_files:
        console.print("[yellow]No changes detected. Nothing to back up.[/yellow]")
        return

    try:
        repo.git.add(all=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_message = f"{config.get('commit_message_prefix', '[AutoBackup]')} {timestamp}"
        repo.index.commit(commit_message)
        console.print(f"[green]Backup committed:[/green] {commit_message}")
    except Exception as e:
        console.print(f"[red]Error during commit:[/red] {e}")
