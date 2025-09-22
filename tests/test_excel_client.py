from unittest.mock import Mock

from pptx_schedule.excel_client import ExcelUpdater, GraphExcelClient


class DummyResponse:
    def __init__(self, status_code: int = 200, payload: object | None = None) -> None:
        self.status_code = status_code
        self._payload = payload or {}
        self.text = str(self._payload)

    def json(self) -> object:
        return self._payload


def test_graph_excel_client_add_rows_builds_request() -> None:
    session = Mock()
    session.request.return_value = DummyResponse()
    client = GraphExcelClient("token", session=session)

    client.add_rows("drive", "item", "Sheet1", "Table1", [["foo", "bar"]])

    session.request.assert_called_once()
    method, url = session.request.call_args[0][:2]
    kwargs = session.request.call_args.kwargs
    assert method == "POST"
    assert url.endswith("/tables('Table1')/rows/add")
    assert kwargs["headers"]["Authorization"] == "Bearer token"
    assert kwargs["json"] == {"values": [["foo", "bar"]]}


def test_excel_updater_dry_run_returns_serialized_rows() -> None:
    updater = ExcelUpdater(
        None,
        drive_id="drive",
        item_id="item",
        worksheet="Sheet1",
        table_name="Table1",
        columns=["Name", "Dates"],
    )

    rows = updater.push_records(
        [{"Name": "Project", "Dates": ["2024-05-01", "2024-05-02"]}], dry_run=True
    )

    assert rows == [["Project", "2024-05-01, 2024-05-02"]]


def test_excel_updater_invokes_client_when_not_dry_run() -> None:
    client = Mock(spec=GraphExcelClient)
    updater = ExcelUpdater(
        client,
        drive_id="drive",
        item_id="item",
        worksheet="Sheet1",
        table_name="Table1",
        columns=["Name"],
    )

    updater.push_records([{"Name": "Project"}], clear_before_update=True, dry_run=False)

    client.clear_table.assert_called_once_with("drive", "item", "Sheet1", "Table1")
    client.add_rows.assert_called_once_with(
        "drive",
        "item",
        "Sheet1",
        "Table1",
        [["Project"]],
    )
