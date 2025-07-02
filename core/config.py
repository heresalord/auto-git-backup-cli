# auto_git_backup/core/config.py
import json
import os
from pathlib import Path

DEFAULT_CONFIG = {
    "commit_interval": 10,
    "auto_push": False,
    "remote_name": "origin",
    "branch": "autobackup/main",
    "commit_message_prefix": "[AutoBackup]",
    "watch_extensions": [".py", ".js", ".html", ".php"],
    "excluded_paths": ["node_modules", "__pycache__"]
}

CONFIG_FILE = ".autogitbackup.json"
IGNORE_FILE = ".backupignore"


def init_config():
    """Crée les fichiers de configuration par défaut s'ils n'existent pas."""
    if not Path(CONFIG_FILE).exists():
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)

    if not Path(IGNORE_FILE).exists():
        with open(IGNORE_FILE, "w") as f:
            f.write("# Fichiers/dossiers ignorés\nnode_modules\n__pycache__\n")


def load_config():
    """Charge la configuration depuis le fichier JSON."""
    if not Path(CONFIG_FILE).exists():
        raise FileNotFoundError("Fichier de configuration introuvable. Utilisez `backupgit init`.")

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
    return config