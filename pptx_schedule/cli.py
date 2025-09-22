"""Command line interface that orchestrates PPTX extraction and Excel updates."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Mapping, Sequence

from .excel_client import ExcelUpdater, GraphExcelClient
from .extractor import extract_project_info
from .models import ExtractionConfig
from .versioning import VersionManager

DEFAULT_COLUMNS = [
    "ProjectName",
    "PptxPath",
    "ScheduleDates",
    "ScheduleCount",
    "Version",
    "UpdatedAt",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract schedule information from PPTX files and update Excel.")
    parser.add_argument("--pptx-dir", required=True, help="Directory that contains PPTX files to process.")
    parser.add_argument(
        "--token",
        default=None,
        help="Microsoft Graph access token. If omitted, GRAPH_API_TOKEN from the environment is used.",
    )
    parser.add_argument("--drive-id", help="Drive ID that stores the Excel workbook.")
    parser.add_argument("--item-id", help="Item ID (file ID) of the Excel workbook.")
    parser.add_argument("--worksheet", help="Target worksheet name in the workbook.")
    parser.add_argument("--table", help="Target table name inside the worksheet.")
    parser.add_argument(
        "--column",
        action="append",
        dest="columns",
        default=None,
        help="Column name to export. Repeat for multiple columns. Defaults to a preset selection.",
    )
    parser.add_argument(
        "--version-store",
        default="pptx_versions.json",
        help="Path to the JSON file that stores version information.",
    )
    parser.add_argument(
        "--project-name-pattern",
        action="append",
        dest="project_name_patterns",
        default=None,
        help="Additional regular expression used to locate the project name.",
    )
    parser.add_argument(
        "--project-name-keyword",
        action="append",
        dest="project_name_keywords",
        default=None,
        help="Additional keyword to search for the project name.",
    )
    parser.add_argument(
        "--schedule-keyword",
        action="append",
        dest="schedule_keywords",
        default=None,
        help="Keyword that marks a table as containing schedule information.",
    )
    parser.add_argument(
        "--dayfirst",
        action="store_true",
        help="Interpret ambiguous dates as day-first (e.g. 10/11/2024 -> 10 November).",
    )
    parser.add_argument(
        "--clear-before-update",
        action="store_true",
        help="Clear the Excel table before inserting new rows.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Extract information without modifying Excel or the version store.",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively search for PPTX files inside the provided directory.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    pptx_dir = Path(args.pptx_dir)
    if not pptx_dir.exists():
        parser.error(f"PPTX directory does not exist: {pptx_dir}")

    base_config = ExtractionConfig(dayfirst=args.dayfirst)
    config = ExtractionConfig(
        project_name_patterns=args.project_name_patterns or base_config.project_name_patterns,
        project_name_keywords=args.project_name_keywords or base_config.project_name_keywords,
        schedule_table_keywords=args.schedule_keywords or base_config.schedule_table_keywords,
        dayfirst=args.dayfirst,
    )

    pptx_paths = _discover_pptx_files(pptx_dir, recursive=args.recursive)
    if not pptx_paths:
        print("No PPTX files found. Nothing to do.")
        return 0

    version_manager = VersionManager(args.version_store)

    token = args.token or os.getenv("GRAPH_API_TOKEN")
    if not args.dry_run and not token:
        parser.error("An access token is required unless running in dry-run mode.")

    columns = args.columns or list(DEFAULT_COLUMNS)

    client = None if args.dry_run else GraphExcelClient(token)
    updater = ExcelUpdater(
        client,
        drive_id=args.drive_id or "",
        item_id=args.item_id or "",
        worksheet=args.worksheet or "",
        table_name=args.table or "",
        columns=columns,
    )

    records: List[Mapping[str, object]] = []
    for pptx_path in pptx_paths:
        project = extract_project_info(pptx_path, config=config)
        schedule_dates = sorted({entry.value.isoformat() for entry in project.schedule_entries})
        schedule_count = len(schedule_dates)

        metadata = {"pptx_path": str(pptx_path), "schedule_count": schedule_count}
        existing_version = version_manager.get(project.project_name)
        if args.dry_run:
            next_version = 1 if existing_version is None else existing_version.version + 1
            updated_at = datetime.now(timezone.utc).isoformat()
        else:
            record = version_manager.bump(project.project_name, metadata=metadata)
            next_version = record.version
            updated_at = record.updated_at

        record_map = {
            "ProjectName": project.project_name,
            "PptxPath": str(pptx_path),
            "ScheduleDates": schedule_dates,
            "ScheduleCount": schedule_count,
            "Version": next_version,
            "UpdatedAt": updated_at,
        }
        records.append(record_map)

    rows = updater.push_records(
        records,
        clear_before_update=args.clear_before_update,
        dry_run=args.dry_run,
    )

    if args.dry_run:
        print("Dry run - the following rows would be sent to Excel:")
        print(json.dumps({"columns": columns, "rows": rows}, ensure_ascii=False, indent=2))

    print(f"Processed {len(records)} PPTX files.")
    return 0


def _discover_pptx_files(root: Path, *, recursive: bool) -> List[Path]:
    pattern = "**/*.pptx" if recursive else "*.pptx"
    return sorted(path for path in root.glob(pattern) if path.is_file())


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
