from datetime import datetime

from stock_common.sc_datasource import _holders


class _JsonResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def test_strategic_announcement_paths_preserve_id_and_pdf_url(monkeypatch):
    timestamp_ms = 1795536000000
    row = {
        "secCode": "600449",
        "announcementTitle": "<em>示例公司董事会决议公告</em>",
        "announcementTime": timestamp_ms,
        "announcementTypeName": None,
        "announcementId": "1225685351",
        "adjunctUrl": "finalpage/2026-11-25/1225685351.PDF",
    }
    monkeypatch.setattr(_holders, "_cninfo_get_orgid", lambda _code: "gssh0600449")
    monkeypatch.setattr("stock_common.sc_network._source_rate_limit_wait", lambda _url: None)
    monkeypatch.setattr(
        _holders,
        "_quick_request",
        lambda *_args, **_kwargs: _JsonResponse({"announcements": [row]}),
    )

    result = _holders.get_strategic_announcements("600449", page_size=1, keywords=["公告"])

    assert len(result) == 1
    announcement = result[0]
    assert announcement["title"] == "示例公司董事会决议公告"
    assert announcement["date"] == datetime.fromtimestamp(timestamp_ms / 1000).strftime("%Y-%m-%d")
    assert announcement["type"] == ""
    assert announcement["announcement_id"] == "1225685351"
    assert announcement["adjunct_url"] == "finalpage/2026-11-25/1225685351.PDF"
    assert "url" not in announcement
