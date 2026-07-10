"""conftest.py — pytest 共享 fixtures。

所有测试共享的 mock 工具：
  - mock_requests: 全局拦截 urllib.request + requests，避免测试触发真实网络
  - tmp_text: 临时文件写入器
  - fake_strategy_config: 伪造的 strategy_config.yaml（如测试需要）
"""
from __future__ import annotations

import json
import os
import tempfile
from unittest import mock

import pytest


# ── 网络 mock：在所有测试里自动生效（scope="session"）──────────
@pytest.fixture(autouse=True)
def _no_real_network(monkeypatch):
    """禁止测试期间任何真实的 HTTP/TCP 调用。"""

    class _FakeResp:
        def __init__(self, text_body="", status_code=200):
            self._text = text_body
            self.status_code = status_code

        def json(self):
            try:
                return json.loads(self._text)
            except Exception:
                return {}

        def read(self):
            return self._text.encode("utf-8")

        def close(self):
            pass

    # 1) 拦截 requests.get / post
    def fake_get(*args, **kwargs):
        return _FakeResp("{}")

    def fake_post(*args, **kwargs):
        return _FakeResp("{}")

    try:
        monkeypatch.setattr("requests.get", fake_get)
        monkeypatch.setattr("requests.post", fake_post)
    except Exception as _e:
        print(f"[conftest] monkeypatch requests failed: {_e}", flush=True)
        # monkeypatch 失败意味着真实网络调用可能泄漏，标记警告
        import warnings
        warnings.warn(f"conftest: failed to mock requests, real network calls may leak: {_e}")

    # 2) 拦截 urllib.request.urlopen（代理探测会走到这里）
    def fake_urlopen(*args, **kwargs):
        raise OSError("network mock: real connections disabled")

    try:
        monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    except Exception as _e:
        print(f"[conftest] monkeypatch urlopen failed: {_e}", flush=True)
        import warnings
        warnings.warn(f"conftest: failed to mock urlopen, real network calls may leak: {_e}")


# ── 临时工作目录：避免污染真实项目根 ───────────────────────────
@pytest.fixture
def tmp_project(tmp_path):
    """返回一个模拟项目根目录（含最小的 client_secrets.json）。"""
    # 写入伪 client_secrets.json
    fake_secrets = {
        "installed": {
            "client_id": "fake-id.apps.googleusercontent.com",
            "project_id": "fake-proj",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "fake-secret",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
        }
    }
    secrets_file = tmp_path / "client_secrets.json"
    secrets_file.write_text(json.dumps(fake_secrets), encoding="utf-8")

    # 写入伪 strategy_config.yaml
    (tmp_path / "strategy_config.yaml").write_text(
        "report:\n  default_formats: [txt, md]\n", encoding="utf-8"
    )
    return str(tmp_path)
