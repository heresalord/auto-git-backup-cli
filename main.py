import typer
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.panel import Panel
from rich.console import Console
import json
from pathlib import Path
import subprocess
from git import repo

from core.config import load_config
from core.backup import run_backup_once
from core.restore import restore_backup
from core.watcher import watch_changes
from core.utils import get_git_remotes, add_git_remote, remove_git_remote

app = typer.Typer()
console = Console()

ASCII_BANNER = """
[bold cyan]
    █████╗ ██╗   ██╗████████╗ ██████╗  ██████╗ ██╗   ██╗██████╗  ██████╗
   ██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗██╔═══██╗██║   ██║██╔══██╗██╔════╝
   ███████║██║   ██║   ██║   ██║   ██║██║   ██║██║   ██║██║  ██║██║     
   ██╔══██║██║   ██║   ██║   ██║   ██║██║   ██║██║   ██║██║  ██║██║     
   ██║  ██║╚██████╔╝   ██║   ╚██████╔╝╚██████╔╝╚██████╔╝██████╔╝╚██████╗
   ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝  ╚═════╝  ╚═════╝ ╚═════╝  ╚═════╝
[/bold cyan]                  
[green]Auto Git Backup by KMS STUDIO DEV[/green] — [dim]Smart backup, safe code.[/dim]
"""

DEFAULT_CONFIG = {
    "commit_interval": 10,
    "auto_push": False,
    "remote_name": "origin",
    "branch": "autobackup/main",
    "commit_message_prefix": "[AutoBackup]",
    "watch_extensions": [".py", ".js", ".html", ".php"],
    "excluded_paths": ["node_modules", "__pycache__"],
    "project_path": str(Path.cwd()),
}


def init_config():
    """Initialize config and ask for project folder, optionally init git repo."""
    config_path = Path(".autogitbackup.json")
    if config_path.exists():
        console.print("[yellow]Configuration file already exists.[/yellow]")
        return

    project_path = Prompt.ask(
        "Enter the full path of the folder to backup/watch", default=str(Path.cwd())
    )
    p = Path(project_path)
    if not p.exists() or not p.is_dir():
        console.print("[red]Invalid folder path. Initialization aborted.[/red]")
        return

    # Check if folder is git repo
    if not (p / ".git").exists():
        if Confirm.ask(f"The folder '{project_path}' is not a Git repo. Initialize one now?"):
            try:
                subprocess.run(["git", "init"], cwd=project_path, check=True)
                console.print(f"[green]Initialized a new Git repository at '{project_path}'.[/green]")
            except Exception as e:
                console.print(f"[red]Failed to initialize Git repository: {e}[/red]")
                return

    config = DEFAULT_CONFIG.copy()
    config["project_path"] = project_path

    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)

    ignore_path = Path(".backupignore")
    if not ignore_path.exists():
        with open(ignore_path, "w") as f:
            f.write("node_modules\n__pycache__\n")

    console.print("[green]Configuration initialized and saved.[/green]")


def interactive_menu():
    console.print(Panel.fit(ASCII_BANNER, style="cyan"))
    while True:
        console.print("\n[bold]What do you want to do?[/bold]")
        console.print("1. Initialize configuration")
        console.print("2. Manual backup")
        console.print("3. Restore a backup")
        console.print("4. Start auto-watching and backup")
        console.print("5. Edit configuration")
        console.print("6. Show current configuration")
        console.print("0. Quit")
        console.print("7. Manage Git remotes")


        choice = IntPrompt.ask("Enter your choice", default=0)

        if choice == 1:
            init_config()
        elif choice == 2:
            config = load_config()
            run_backup_once(config)
        elif choice == 3:
            config = load_config()
            restore_backup(config)
        elif choice == 4:
            config = load_config()
            watch_changes(config)
        elif choice == 5:
            config = load_config()
            config = modify_config_interactive(config)
            with open(".autogitbackup.json", "w") as f:
                json.dump(config, f, indent=4)
            console.print("[green]Configuration updated.[/green]")
        elif choice == 6:
            config = load_config()
            console.print(Panel(str(config), title="Current Configuration"))
        elif choice == 7:
            config = load_config()
            project_path = config.get("project_path", ".")
            repo = None
            try:
                repo = Repo(project_path)
            except Exception:
                console.print("[red]Failed to open Git repository at configured path.[/red]")
                continue

            remotes = get_git_remotes(repo)
            if not remotes:
                console.print("[yellow]No remotes configured yet.[/yellow]")
            else:
                console.print("[bold]Current remotes:[/bold]")
                for name, url in remotes.items():
                    console.print(f"- {name}: {url}")

            if Confirm.ask("Do you want to add or update a remote?"):
                name = Prompt.ask("Enter remote name", default="origin")
                url = Prompt.ask("Enter remote URL (e.g. git@github.com:user/repo.git)")
                add_git_remote(repo, name, url)
                console.print(f"[green]Remote '{name}' set to {url}.[/green]")

            elif remotes and Confirm.ask("Do you want to remove an existing remote?"):
                name = Prompt.ask("Enter remote name to remove")
                if name in remotes:
                    remove_git_remote(repo, name)
                    console.print(f"[green]Remote '{name}' removed.[/green]")
                else:
                    console.print("[red]Remote not found.[/red]")
            elif choice == 0:
                console.print("[bold red]Goodbye![/bold red]")
            break

def modify_config_interactive(config):
    console.print("[bold]Interactive configuration editor[/bold]")
    for key, value in config.items():
        new_val = Prompt.ask(f"{key} (current: {value})", default=str(value))
        if isinstance(value, bool):
            config[key] = new_val.lower() in ("true", "1", "yes", "y")
        elif isinstance(value, int):
            try:
                config[key] = int(new_val)
            except ValueError:
                console.print(f"[yellow]Invalid input for {key}, keeping previous value.[/yellow]")
        elif isinstance(value, list):
            try:
                import json as js
                config[key] = js.loads(new_val)
            except Exception:
                config[key] = [x.strip() for x in new_val.split(",")]
        else:
            config[key] = new_val
    return config


@app.command()
def init():
    """Initialize the backup system."""
    init_config()


@app.command()
def backup():
    """Run a one-time backup (git commit)."""
    config = load_config()
    run_backup_once(config)


@app.command()
def restore():
    """Run interactive restore."""
    config = load_config()
    restore_backup(config)


@app.command()
def watch():
    """Start watching for changes and auto-backup."""
    config = load_config()
    watch_changes(config)


@app.command()
def info():
    """Show current config."""
    config = load_config()
    console.print(Panel(str(config), title="Current Configuration"))


def main():
    import sys

    if len(sys.argv) == 1:
        interactive_menu()
    else:
        app()


if __name__ == "__main__":
    main()
