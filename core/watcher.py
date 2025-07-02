# auto_git_backup/core/watcher.py

import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich.console import Console
from core.backup import run_backup_once  # corrected import path

console = Console()

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, config):
        self.config = config
        self.last_commit_time = 0
        self.debounce_delay = 2  # seconds to wait before backup after event
        self.pending_backup = False
        self.project_path = Path(config.get("project_path", ".")).resolve()

    def should_ignore(self, path: Path):
        ignored = self.config.get("excluded_paths", [])
        # Check if any ignored folder is part of the path parts
        return any(part in ignored for part in path.parts)

    def should_watch_extension(self, path: Path):
        watch_exts = self.config.get("watch_extensions", [])
        return any(path.name.endswith(ext) for ext in watch_exts)

    def on_any_event(self, event):
        # Get full absolute path of event file
        event_path = Path(event.src_path).resolve()

        # Only watch inside the project_path folder
        if self.project_path not in event_path.parents and event_path != self.project_path:
            return

        if self.should_ignore(event_path):
            return

        if not self.should_watch_extension(event_path):
            return

        now = time.time()
        # Debounce logic: if enough time passed since last commit, trigger immediately,
        # else schedule it after debounce delay
        if now - self.last_commit_time >= self.config.get("commit_interval", 10):
            console.print(f"[cyan]Changes detected at {event_path}, running backup...[/cyan]")
            run_backup_once(self.config)
            self.last_commit_time = now
            self.pending_backup = False
        else:
            if not self.pending_backup:
                self.pending_backup = True
                # Schedule delayed backup
                time_to_wait = self.debounce_delay
                console.print(f"[cyan]Changes detected at {event_path}, will backup in {time_to_wait}s...[/cyan]")
                # Run backup after delay in a separate thread or using a timer
                # For simplicity, start a delayed call here:
                from threading import Timer
                Timer(time_to_wait, self._delayed_backup).start()

    def _delayed_backup(self):
        now = time.time()
        if now - self.last_commit_time >= self.config.get("commit_interval", 10):
            console.print("[cyan]Running delayed backup...[/cyan]")
            run_backup_once(self.config)
            self.last_commit_time = now
        self.pending_backup = False


def watch_changes(config):
    """Start watching the project folder for changes and auto backup."""
    project_path = Path(config.get("project_path", ".")).resolve()
    observer = Observer()
    handler = ChangeHandler(config)
    observer.schedule(handler, str(project_path), recursive=True)

    console.print(f"[blue]Watching folder: {project_path}[/blue]")
    console.print("[dim]Press Ctrl+C to stop watching.[/dim]")

    try:
        observer.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        console.print("[red]Watching stopped.[/red]")

    observer.join()
