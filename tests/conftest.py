"""conftest.py — pytest 共享 fixtures。

所有测试共享的 mock 工具：
  - mock_requests: 全局拦截 urllib.request + requests，避免测试触发真实网络
  - tmp_text: 临时文件写入器
  - fake_strategy_config: 伪造的 strategy_config.yaml（如测试需要）

使用 pytest.mark.real_network 标记的测试不会被网络 mock 拦截。

----------------------------------------------------------------------
AGENTS.md compliance note (see AGENTS.md 2.1.1):
  本文件示范 pytest 作为 Python 库的正确用法。所有 `import pytest` /
  `@pytest.fixture` / `@pytest.mark.*` / `pytest.skip()` 等调用都是
  Python 语言特性,与 shell 完全无关,理应且必须直接使用。

  仅当主动通过 shell 触发一次完整测试套件时,才走：
    .\\scripts\\run_tests.ps1
  而不是直接 `pytest tests/` / `python -m pytest ...`。

  写新测试时若需要：
    - 自定义 marker: 先到 pyproject.toml [tool.pytest.ini_options] markers
      注册,避免 PytestUnknownMarkWarning
    - 触发真实网络: 加 @pytest.mark.real_network,否则会被本文件
      _no_real_network 拦截
    - 异步测试: `import pytest_asyncio` 然后 `@pytest.mark.asyncio`
----------------------------------------------------------------------
"""
from __future__ import annotations

import json
import os
import tempfile
from unittest import mock

import pytest

pytest_plugins = ["pytest_asyncio"]


# ── 网络 mock：在所有测试里自动生效（scope="session"）──────────
@pytest.fixture(autouse=True)
def _no_real_network(monkeypatch, request):
    """禁止测试期间任何真实的 HTTP/TCP 调用。

    使用 @pytest.mark.real_network 标记的测试会跳过此 mock。
    V14.0 增强：可通过设置环境变量 REAL_NETWORK=1 显式允许真实网络调用，
    否则 real_network 标记的测试在 CI 环境（无显式标记）下也会被自动 skip。
    """
    if request.node.get_closest_marker("real_network"):
        # V14.0: 检查是否在允许真实网络的环境（显式设置 REAL_NETWORK=1）
        import os
        if not os.environ.get("REAL_NETWORK") and not os.environ.get("CI_RUN_REAL_NETWORK"):
            # CI 默认 skip（避免 CI 环境真实网络失败）
            import pytest
            if os.environ.get("CI"):  # 仅在 CI 环境 skip，本地仍可跑
                pytest.skip("real_network test: set REAL_NETWORK=1 to enable")
        return

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


# ── test_em_rate_limit.py 的 endpoint fixture ──────────────────────
@pytest.fixture(params=[
    {
        "name": "datacenter",
        "url": "https://datacenter-web.eastmoney.com/api/data/v1/get",
        "params": {
            "reportName": "RPT_DAILYBILLBOARD_DETAILSNEW",
            "columns": "SECURITY_CODE,SECURITY_NAME_ABBR",
            "pageNumber": "1",
            "pageSize": "1",
            "sortColumns": "TRADE_DATE",
            "sortTypes": "-1",
        },
        "check": lambda r: r.get("success", False) is not False and r.get("result", {}).get("data") is not None,
    },
    {
        "name": "push2",
        "url": "http://83.push2.eastmoney.com/api/qt/clist/get",
        "params": {
            "pn": "1",
            "pz": "1",
            "po": "1",
            "np": "1",
            "fltt": "2",
            "invt": "2",
            "fs": "m:0 t:6,m:0 t:80",
            "fields": "f12,f14,f2,f3",
        },
        "check": lambda r: r.get("data", {}).get("diff") is not None and len(r["data"]["diff"]) > 0,
    },
    {
        "name": "reportapi",
        "url": "https://reportapi.eastmoney.com/report/list",
        "params": {
            "pageSize": "1",
            "industry": "*",
            "rating": "*",
            "beginTime": "2024-01-01",
            "endTime": "2030-01-01",
            "pageNo": "1",
            "code": "600519",
            "qType": "0",
        },
        "check": lambda r: r.get("data") is not None and isinstance(r.get("data"), list),
    },
])
def endpoint(request):
    """test_em_rate_limit.py 使用的 endpoint fixture，遍历三个东财域名。"""
    return request.param
