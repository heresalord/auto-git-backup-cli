# auto_git_backup/core/restore.py

from git import Repo
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table

console = Console()


def list_backups(config):
    """Liste les commits de sauvegarde créés par l'outil."""
    repo = Repo(".")
    prefix = config.get("commit_message_prefix", "[AutoBackup]")
    commits = list(repo.iter_commits(config.get("branch", "autobackup/main"), max_count=50))
    
    backups = [
        (i + 1, c.hexsha[:7], c.committed_datetime.strftime("%Y-%m-%d %H:%M:%S"), c.message.strip())
        for i, c in enumerate(commits) if c.message.startswith(prefix)
    ]

    table = Table(title="Sauvegardes disponibles")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Commit", style="magenta")
    table.add_column("Date", style="green")
    table.add_column("Message", style="white")

    for id_, sha, date, msg in backups:
        table.add_row(str(id_), sha, date, msg)

    if backups:
        console.print(table)
    else:
        console.print("[yellow]Aucune sauvegarde trouvée.[/yellow]")
    
    return backups


def restore_backup(config):
    """Permet de restaurer une sauvegarde à partir d’un commit spécifique."""
    backups = list_backups(config)
    if not backups:
        return

    choice = Prompt.ask("ID du commit à restaurer", default=str(backups[0][0]))
    try:
        index = int(choice) - 1
        if index < 0 or index >= len(backups):
            raise ValueError
        commit_sha = backups[index][1]
        if Confirm.ask(f"Confirmer la restauration au commit {commit_sha}?"):
            Repo(".").git.checkout(commit_sha)
            console.print(f"[green]Restauration effectuée au commit {commit_sha}[/green]")
    except (ValueError, IndexError):
        console.print("[red]ID invalide. Opération annulée.[/red]")
