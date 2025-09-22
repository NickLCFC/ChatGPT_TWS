from pathlib import Path
import pytest

from pptx_schedule.versioning import VersionManager


def test_version_manager_bump_and_persist(tmp_path: Path) -> None:
    store = tmp_path / "versions.json"
    manager = VersionManager(store)

    record1 = manager.bump("ProjectA", metadata={"pptx_path": "demo.pptx"})
    assert record1.version == 1

    record2 = manager.bump("ProjectA")
    assert record2.version == 2

    manager_again = VersionManager(store)
    restored = manager_again.get("ProjectA")
    assert restored is not None
    assert restored.version == 2
    assert restored.metadata.get("pptx_path") == "demo.pptx"


def test_version_manager_invalid_json(tmp_path: Path) -> None:
    store = tmp_path / "versions.json"
    store.write_text("not json", encoding="utf-8")

    with pytest.raises(ValueError):
        VersionManager(store)
