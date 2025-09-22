"""Microsoft Graph Excel client helpers used to sync extracted data."""

from __future__ import annotations

import json
from typing import Iterable, List, Mapping, Optional, Sequence

import requests


class ExcelUpdateError(RuntimeError):
    """Raised when a Microsoft Graph API call related to Excel fails."""


class GraphExcelClient:
    """Small wrapper around the Microsoft Graph Excel API."""

    def __init__(
        self,
        access_token: str,
        *,
        base_url: str = "https://graph.microsoft.com/v1.0",
        session: Optional[requests.Session] = None,
    ) -> None:
        if not access_token:
            raise ValueError("An access token is required for Graph API calls.")
        self._access_token = access_token
        self._base_url = base_url.rstrip("/")
        self._session = session or requests.Session()

    def close(self) -> None:
        self._session.close()

    def clear_table(self, drive_id: str, item_id: str, worksheet: str, table_name: str) -> None:
        """Remove the data contained in an Excel table."""

        endpoint = self._table_endpoint(drive_id, item_id, worksheet, table_name, suffix="/range/clear")
        self._request("POST", endpoint, json={"applyTo": "All"})

    def add_rows(
        self,
        drive_id: str,
        item_id: str,
        worksheet: str,
        table_name: str,
        values: Sequence[Sequence[str]],
    ) -> None:
        """Append rows to an Excel table."""

        if not values:
            return
        endpoint = self._table_endpoint(drive_id, item_id, worksheet, table_name, suffix="/rows/add")
        payload = {"values": [list(row) for row in values]}
        self._request("POST", endpoint, json=payload)

    def _table_endpoint(
        self, drive_id: str, item_id: str, worksheet: str, table_name: str, *, suffix: str = ""
    ) -> str:
        worksheet_part = f"workbook/worksheets('{worksheet}')"
        table_part = f"tables('{table_name}')"
        return f"{self._base_url}/drives/{drive_id}/items/{item_id}/{worksheet_part}/{table_part}{suffix}"

    def _request(self, method: str, url: str, **kwargs) -> requests.Response:
        headers = kwargs.pop("headers", {})
        headers.setdefault("Authorization", f"Bearer {self._access_token}")
        headers.setdefault("Content-Type", "application/json")
        response = self._session.request(method, url, headers=headers, **kwargs)
        if response.status_code >= 400:
            message = self._format_error(response)
            raise ExcelUpdateError(message)
        return response

    @staticmethod
    def _format_error(response: requests.Response) -> str:
        try:
            payload = response.json()
        except json.JSONDecodeError:
            payload = response.text
        return f"Graph API request failed ({response.status_code}): {payload}"


class ExcelUpdater:
    """High level helper that converts records into Excel table rows."""

    def __init__(
        self,
        client: Optional[GraphExcelClient],
        *,
        drive_id: str,
        item_id: str,
        worksheet: str,
        table_name: str,
        columns: Sequence[str],
    ) -> None:
        if not columns:
            raise ValueError("At least one column must be provided for Excel updates.")
        self._client = client
        self._drive_id = drive_id
        self._item_id = item_id
        self._worksheet = worksheet
        self._table_name = table_name
        self._columns = list(columns)

    def push_records(
        self,
        records: Iterable[Mapping[str, object]],
        *,
        clear_before_update: bool = False,
        dry_run: bool = False,
    ) -> List[List[str]]:
        """Push records into the configured Excel table and return serialized rows."""

        rows: List[List[str]] = [self._serialize_record(record) for record in records]

        if dry_run or self._client is None:
            return rows

        if clear_before_update:
            self._client.clear_table(self._drive_id, self._item_id, self._worksheet, self._table_name)

        if rows:
            self._client.add_rows(
                self._drive_id,
                self._item_id,
                self._worksheet,
                self._table_name,
                rows,
            )
        return rows

    def _serialize_record(self, record: Mapping[str, object]) -> List[str]:
        serialized: List[str] = []
        for column in self._columns:
            value = record.get(column, "")
            if isinstance(value, (list, tuple, set)):
                serialized.append(", ".join(sorted(str(item) for item in value)))
            else:
                serialized.append("" if value is None else str(value))
        return serialized
