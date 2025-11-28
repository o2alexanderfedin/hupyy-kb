"""File system watcher for real-time file change detection."""

import asyncio
import fnmatch
import os
import threading
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from logging import Logger
from pathlib import Path
from typing import List, Optional, Set

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


class FileChangeType(Enum):
    """Type of file change event."""
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"


@dataclass
class FileChange:
    """Represents a file change event."""
    path: str
    change_type: FileChangeType
    dest_path: Optional[str] = None  # For move events


class DebouncedEventHandler(FileSystemEventHandler):
    """
    File system event handler with debouncing.
    Collects events and triggers callback after debounce period.
    """

    def __init__(
        self,
        logger: Logger,
        callback: Callable[[List[FileChange]], None],
        debounce_seconds: float = 1.0,
        supported_extensions: Optional[Set[str]] = None,
        ignore_patterns: Optional[List[str]] = None,
        ignore_directories: Optional[List[str]] = None
    ) -> None:
        super().__init__()
        self.logger = logger
        self.callback = callback
        self.debounce_seconds = debounce_seconds
        self.supported_extensions = supported_extensions or {
            ".md", ".txt", ".py", ".js", ".ts", ".json", ".yaml", ".yml",
            ".html", ".css", ".tsx", ".jsx", ".go", ".rs", ".java", ".c",
            ".cpp", ".h", ".hpp", ".rb", ".php", ".sh", ".bash", ".zsh",
            ".toml", ".ini", ".cfg", ".conf", ".xml", ".svg"
        }
        self.ignore_patterns = ignore_patterns or [
            "*.pyc", "*.pyo", "__pycache__", "*.swp", "*.swo", "*~",
            ".DS_Store", "Thumbs.db", "*.log", "*.tmp", "*.temp"
        ]
        self.ignore_directories = ignore_directories or [
            "node_modules", ".git", "__pycache__", "venv", ".venv",
            "env", ".env", ".idea", ".vscode", "dist", "build",
            "target", ".next", ".nuxt", "coverage", ".pytest_cache",
            ".mypy_cache", ".tox", "eggs", "*.egg-info"
        ]

        self._pending_changes: dict[str, FileChange] = {}
        self._timer: Optional[threading.Timer] = None
        self._lock = threading.Lock()
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def set_event_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Set the asyncio event loop for async callbacks."""
        self._loop = loop

    def _should_ignore(self, path: str) -> bool:
        """Check if the path should be ignored."""
        path_obj = Path(path)

        # Check ignore patterns
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(path_obj.name, pattern):
                return True

        # Check ignore directories
        parts = path_obj.parts
        for directory in self.ignore_directories:
            if directory in parts:
                return True

        # Check file extension
        if path_obj.is_file() or not os.path.exists(path):
            ext = path_obj.suffix.lower()
            if ext and ext not in self.supported_extensions:
                return True

        return False

    def _should_ignore_directory(self, path: str) -> bool:
        """Check if a directory should be ignored."""
        path_obj = Path(path)
        name = path_obj.name

        # Check if directory name matches ignore list
        for directory in self.ignore_directories:
            if fnmatch.fnmatch(name, directory):
                return True

        return False

    def _schedule_callback(self) -> None:
        """Schedule the callback after debounce period."""
        with self._lock:
            if self._timer:
                self._timer.cancel()

            self._timer = threading.Timer(
                self.debounce_seconds,
                self._trigger_callback
            )
            self._timer.start()

    def _trigger_callback(self) -> None:
        """Trigger the callback with collected changes."""
        with self._lock:
            if not self._pending_changes:
                return

            changes = list(self._pending_changes.values())
            self._pending_changes.clear()

        try:
            if self._loop and asyncio.iscoroutinefunction(self.callback):
                asyncio.run_coroutine_threadsafe(self.callback(changes), self._loop)
            else:
                self.callback(changes)
        except Exception as e:
            self.logger.error(f"Error in file change callback: {e}", exc_info=True)

    def _add_change(self, path: str, change_type: FileChangeType, dest_path: Optional[str] = None) -> None:
        """Add a change to the pending changes."""
        if self._should_ignore(path):
            return

        if dest_path and self._should_ignore(dest_path):
            return

        with self._lock:
            # For modifications, keep the latest
            # For deletes after creates, remove the entry
            if path in self._pending_changes:
                existing = self._pending_changes[path]
                if existing.change_type == FileChangeType.CREATED and change_type == FileChangeType.DELETED:
                    del self._pending_changes[path]
                    return

            self._pending_changes[path] = FileChange(
                path=path,
                change_type=change_type,
                dest_path=dest_path
            )

        self._schedule_callback()

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation event."""
        if event.is_directory:
            if self._should_ignore_directory(event.src_path):
                return
            return
        self.logger.debug(f"File created: {event.src_path}")
        self._add_change(event.src_path, FileChangeType.CREATED)

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification event."""
        if event.is_directory:
            return
        self.logger.debug(f"File modified: {event.src_path}")
        self._add_change(event.src_path, FileChangeType.MODIFIED)

    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file deletion event."""
        if event.is_directory:
            return
        self.logger.debug(f"File deleted: {event.src_path}")
        self._add_change(event.src_path, FileChangeType.DELETED)

    def on_moved(self, event: FileSystemEvent) -> None:
        """Handle file move event."""
        if event.is_directory:
            return
        self.logger.debug(f"File moved: {event.src_path} -> {event.dest_path}")
        self._add_change(event.src_path, FileChangeType.MOVED, event.dest_path)

    def stop(self) -> None:
        """Stop the event handler and cancel pending callbacks."""
        with self._lock:
            if self._timer:
                self._timer.cancel()
                self._timer = None
            self._pending_changes.clear()


class LocalFileSystemWatcher:
    """
    Watches a directory for file system changes with real-time detection.
    Uses watchdog for cross-platform file system events.
    """

    def __init__(
        self,
        logger: Logger,
        watch_path: str,
        callback: Callable[[List[FileChange]], None],
        debounce_seconds: float = 1.0,
        supported_extensions: Optional[Set[str]] = None,
        ignore_patterns: Optional[List[str]] = None,
        ignore_directories: Optional[List[str]] = None
    ) -> None:
        self.logger = logger
        self.watch_path = watch_path
        self.observer: Optional[Observer] = None

        self.event_handler = DebouncedEventHandler(
            logger=logger,
            callback=callback,
            debounce_seconds=debounce_seconds,
            supported_extensions=supported_extensions,
            ignore_patterns=ignore_patterns,
            ignore_directories=ignore_directories
        )

    def start(self, event_loop: Optional[asyncio.AbstractEventLoop] = None) -> bool:
        """
        Start watching the directory.

        Args:
            event_loop: Optional asyncio event loop for async callbacks

        Returns:
            True if started successfully, False otherwise
        """
        if self.observer and self.observer.is_alive():
            self.logger.warning("Watcher is already running")
            return True

        if not os.path.exists(self.watch_path):
            self.logger.error(f"Watch path does not exist: {self.watch_path}")
            return False

        if not os.path.isdir(self.watch_path):
            self.logger.error(f"Watch path is not a directory: {self.watch_path}")
            return False

        try:
            if event_loop:
                self.event_handler.set_event_loop(event_loop)

            self.observer = Observer()
            self.observer.schedule(
                self.event_handler,
                self.watch_path,
                recursive=True
            )
            self.observer.start()

            self.logger.info(f"Started watching directory: {self.watch_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start watcher: {e}", exc_info=True)
            return False

    def stop(self) -> None:
        """Stop watching the directory."""
        if self.observer:
            self.event_handler.stop()
            self.observer.stop()
            self.observer.join(timeout=5)
            self.observer = None
            self.logger.info("Stopped file system watcher")

    def is_running(self) -> bool:
        """Check if the watcher is currently running."""
        return self.observer is not None and self.observer.is_alive()
