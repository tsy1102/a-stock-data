import sys
from types import ModuleType, SimpleNamespace

import pytest

from core import eltdx_adapter
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


def test_shortline_bundle_uses_bj_prefix_and_scopes_ladder(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: dict[str, list[str]] = {}
    monkeypatch.setattr(
        eltdx_adapter, "_SHORTLINE_BUNDLE_CACHE", {"key": None, "ts": 0.0, "val": None}
    )

    class FakeHelpers:
        def limit_ladder(self, *, codes: list[str]) -> SimpleNamespace:
            calls["ladder"] = codes
            return SimpleNamespace(rows=[])

        def shortline_indicators(self, codes: list[str]) -> SimpleNamespace:
            calls["shortline"] = codes
            return SimpleNamespace(
                rows=[{"full_code": code, "last_price": 12.34} for code in codes]
            )

    class FakeClient:
        def __init__(self, **_kwargs: object) -> None:
            self.helpers = FakeHelpers()

        def close(self) -> None:
            return None

    module = ModuleType("eltdx")
    module.TdxClient = FakeClient  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "eltdx", module)

    ladder, shortline = eltdx_adapter.get_eltdx_shortline_bundle(["920118"])

    assert ladder == []
    assert calls == {"ladder": ["bj920118"], "shortline": ["bj920118"]}
    assert shortline["bj920118"]["last_price"] == 12.34
    assert eltdx_adapter.get_eltdx_shortline_for_code("920118")["last_price"] == 12.34
    assert eltdx_adapter.get_eltdx_shortline_for_code("sh920118")["last_price"] == 12.34


def test_limit_ladder_accepts_scoped_codes_and_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[list[str]] = []

    class FakeHelpers:
        def limit_ladder(self, *, codes: list[str]) -> SimpleNamespace:
            calls.append(codes)
            return SimpleNamespace(rows=[{"full_code": code, "ladder_level": 2} for code in codes])

    class FakeClient:
        def __init__(self, **_kwargs: object) -> None:
            self.helpers = FakeHelpers()

        def close(self) -> None:
            return None

    module = ModuleType("eltdx")
    module.TdxClient = FakeClient  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "eltdx", module)

    result = eltdx_adapter.get_eltdx_limit_ladder(timeout=1.0, codes=["920118"])

    assert calls == [["bj920118"]]
    assert result == [{"full_code": "bj920118", "ladder_level": 2}]
