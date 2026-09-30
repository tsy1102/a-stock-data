import sys
from types import ModuleType

import pytest

from core.eltdx_adapter import download_eltdx_report_file


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        (b"zip-data", b"zip-data"),
        (bytearray(b"zip-data"), b"zip-data"),
        (memoryview(b"zip-data"), b"zip-data"),
        (b"", None),
        ("unexpected", None),
    ],
)
def test_download_eltdx_report_file_validates_payload(
    monkeypatch: pytest.MonkeyPatch,
    payload: object,
    expected: bytes | None,
) -> None:
    closed: list[bool] = []

    class FakeResources:
        def download_file(self, filename: str) -> object:
            assert filename == "zhb.zip"
            return payload

    class FakeClient:
        def __init__(self, **kwargs: object) -> None:
            self.resources = FakeResources()

        def close(self) -> None:
            closed.append(True)

    module = ModuleType("eltdx")
    module.TdxClient = FakeClient  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "eltdx", module)

    assert download_eltdx_report_file("zhb.zip") == expected
    assert closed == [True]
