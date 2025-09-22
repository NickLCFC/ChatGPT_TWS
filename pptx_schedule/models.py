"""Data models used by the PPTX schedule extractor."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Iterable, List, Sequence


@dataclass
class ScheduleEntry:
    """Represents a single date found inside a schedule table."""

    slide_index: int
    cell_text: str
    value: date


@dataclass
class ExtractedProject:
    """Container for the information extracted from a PPTX presentation."""

    project_name: str
    schedule_entries: List[ScheduleEntry]
    source_path: Path


@dataclass
class ExtractionConfig:
    """Configuration options that control the extraction heuristics."""

    project_name_patterns: Sequence[str] = field(
        default_factory=lambda: [
            r"專案名稱[:：]\s*(?P<value>.+)",
            r"Project\s*Name[:：]\s*(?P<value>.+)",
        ]
    )
    project_name_keywords: Sequence[str] = field(
        default_factory=lambda: ["專案名稱", "project name", "project"]
    )
    schedule_table_keywords: Sequence[str] = field(
        default_factory=lambda: ["schedule", "日期", "timeline", "milestone"]
    )
    dayfirst: bool = False

    def extend_patterns(self, patterns: Iterable[str]) -> "ExtractionConfig":
        """Return a copy of the config with additional project name patterns."""

        merged = list(self.project_name_patterns) + list(patterns)
        return ExtractionConfig(
            project_name_patterns=merged,
            project_name_keywords=self.project_name_keywords,
            schedule_table_keywords=self.schedule_table_keywords,
            dayfirst=self.dayfirst,
        )
