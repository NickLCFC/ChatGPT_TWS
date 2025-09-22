"""Simple JSON based version control helper for PPTX extraction runs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Mapping, Optional


@dataclass
class VersionRecord:
    """Holds the version number and last update timestamp for a project."""

    version: int
    updated_at: str
    metadata: Mapping[str, object]


class VersionManager:
    """Persist versions for projects between runs of the synchronisation script."""

    def __init__(self, storage_path: Path | str) -> None:
        self._path = Path(storage_path)
        self._state: Dict[str, VersionRecord] = {}
        self._load()

    def bump(self, project_name: str, metadata: Optional[Mapping[str, object]] = None) -> VersionRecord:
        """Increase the stored version for ``project_name`` and persist the result."""

        record = self._state.get(project_name)
        next_version = 1 if record is None else record.version + 1
        timestamp = datetime.now(timezone.utc).isoformat()
        record_metadata: Mapping[str, object] = metadata or {}
        new_record = VersionRecord(version=next_version, updated_at=timestamp, metadata=record_metadata)
        self._state[project_name] = new_record
        self._save()
        return new_record

    def get(self, project_name: str) -> Optional[VersionRecord]:
        return self._state.get(project_name)

    def reset(self, project_name: str) -> None:
        if project_name in self._state:
            del self._state[project_name]
            self._save()

    def snapshot(self) -> Mapping[str, VersionRecord]:
        return dict(self._state)

    def _load(self) -> None:
        if not self._path.exists():
            self._state = {}
            return

        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in version file {self._path}: {exc}") from exc

        projects = payload.get("projects", {}) if isinstance(payload, dict) else {}
        state: Dict[str, VersionRecord] = {}
        for name, raw in projects.items():
            if not isinstance(raw, dict):
                continue
            version = int(raw.get("version", 0))
            updated_at = str(raw.get("updated_at", ""))
            metadata = raw.get("metadata", {})
            if not isinstance(metadata, Mapping):
                metadata = {}
            state[name] = VersionRecord(version=version, updated_at=updated_at, metadata=dict(metadata))
        self._state = state

    def _save(self) -> None:
        if not self._path.parent.exists():
            self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "projects": {
                name: {
                    "version": record.version,
                    "updated_at": record.updated_at,
                    "metadata": dict(record.metadata),
                }
                for name, record in self._state.items()
            }
        }
        temp_path = self._path.with_suffix(self._path.suffix + ".tmp")
        temp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        temp_path.replace(self._path)
