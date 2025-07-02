# auto_git_backup/core/utils.py
import os
from pathlib import Path
from git import Repo


def should_ignore(path: str, ignored_paths: list) -> bool:
    """Vérifie si un chemin correspond à une règle d'exclusion."""
    for ignored in ignored_paths:
        if ignored in path:
            return True
    return False


def list_modified_files(repo, watch_extensions: list, ignored_paths: list) -> list:
    """Retourne la liste des fichiers modifiés non ignorés avec extensions surveillées."""
    changed_files = [item.a_path for item in repo.index.diff(None)]
    filtered = []
    for f in changed_files:
        ext = Path(f).suffix
        if ext in watch_extensions and not should_ignore(f, ignored_paths):
            filtered.append(f)
    return filtered


def format_path(path: Path) -> str:
    """Retourne un chemin formaté en chaîne relative propre."""
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)
    
def get_git_remotes(repo):
    """Return a dict of remote_name -> remote_url."""
    return {remote.name: remote.url for remote in repo.remotes}

def add_git_remote(repo, name, url):
    """Add a new remote or update if exists."""
    existing = [r for r in repo.remotes if r.name == name]
    if existing:
        existing[0].set_url(url)
    else:
        repo.create_remote(name, url)

def remove_git_remote(repo, name):
    """Remove a remote by name."""
    repo.delete_remote(name)