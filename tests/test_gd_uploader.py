"""test_gd_uploader.py — Google Drive 上传模块单元测试。

注意：测试期间所有 HTTP 请求会被 conftest 的 autouse fixture 拦截，
不会产生真实网络调用。
"""
from __future__ import annotations

import json
import os
from unittest import mock

from gd_uploader import (
    _find_working_proxy,
    cleanup_gd_proxy,
    get_or_create_drive_folder,
    upload_or_update_to_drive,
)


def test_find_working_proxy_no_proxy_available(monkeypatch):
    """真实系统无代理时返回 None。"""
    # 拦截所有 opener.open → 全部抛异常
    def fake_open(*args, **kwargs):
        raise OSError("network mock: all blocked")
    with monkeypatch.context() as m:
        m.setattr("urllib.request.OpenerDirector.open", fake_open)
        assert _find_working_proxy() is None


def test_cleanup_gd_proxy_removes_env():
    os.environ["HTTP_PROXY"] = "http://test:1234"
    os.environ["HTTPS_PROXY"] = "http://test:1234"
    cleanup_gd_proxy(True)
    assert "HTTP_PROXY" not in os.environ
    assert "HTTPS_PROXY" not in os.environ


def test_cleanup_gd_proxy_noop_when_unset():
    # 未设置时不应报错
    if "HTTP_PROXY" in os.environ:
        del os.environ["HTTP_PROXY"]
    if "HTTPS_PROXY" in os.environ:
        del os.environ["HTTPS_PROXY"]
    cleanup_gd_proxy(False)  # 未设置则不清除
    # 由于 was_set=False，不会动环境变量
    assert True


def test_get_or_create_drive_folder_handles_none_service():
    assert get_or_create_drive_folder(None, "a-stock-data") is None


def test_upload_or_update_to_drive_handles_none_service(tmp_path):
    fake_file = tmp_path / "fake.txt"
    fake_file.write_text("hello", encoding="utf-8")
    assert upload_or_update_to_drive(None, str(fake_file), "fake-id", "fake.txt") is False


def test_upload_or_update_to_drive_missing_local_file():
    fake_service = object()  # 非 None 但无方法
    assert upload_or_update_to_drive(fake_service, "/nonexistent/path.txt", "fake-id", "x.txt") is False


def test_upload_or_update_to_drive_happy_path(tmp_path):
    """验证 service 非 None + 文件存在时走完整路径（mock MediaIoBaseUpload）。"""
    local = tmp_path / "rpt.txt"
    local.write_text("短线报告内容", encoding="utf-8")

    class _FakeFiles:
        def __init__(self):
            self._list_called = 0

        def list(self, **kwargs):
            self._list_called += 1

            class _Exec:
                def execute(self_inner):
                    return {"files": [{"id": "existing-file-id"}]}
            return _Exec()

        def update(self, **kwargs):
            class _Exec:
                def execute(self_inner):
                    return {"id": "existing-file-id"}
            return _Exec()

        def create(self, **kwargs):
            class _Exec:
                def execute(self_inner):
                    return {"id": "new-file-id"}
            return _Exec()

    class _FakeService:
        def __init__(self):
            self._files = _FakeFiles()

        def files(self):
            return self._files

    service = _FakeService()
    # MediaIoBaseUpload 在 googleapiclient.http 中定义，在函数内部 import
    with mock.patch("googleapiclient.http.MediaIoBaseUpload"):
        ok = upload_or_update_to_drive(service, str(local), "parent-id", "rpt.txt")
        assert ok is True
        assert service.files()._list_called > 0
