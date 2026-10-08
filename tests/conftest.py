"""conftest.py — pytest 共享 fixtures。

所有测试共享的 mock 工具：
  - mock_requests: 全局拦截 urllib.request + requests，避免测试触发真实网络
  - tmp_text: 临时文件写入器
  - fake_strategy_config: 伪造的 strategy_config.yaml（如测试需要）

标记 pytest.mark.real_network 的测试默认跳过；明确启用真实网络后才绕过网络 mock。

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
    - 触发真实网络: 加 @pytest.mark.real_network 并通过测试入口显式启用;
      默认和单模块运行都不会访问真实网络
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

    使用 @pytest.mark.real_network 标记的测试仅在显式设置
    REAL_NETWORK=1 或 CI_RUN_REAL_NETWORK=1 时跳过此 mock；其他情况下总是跳过测试。
    """
    if request.node.get_closest_marker("real_network"):
        # 真实网络测试必须由调用方明确启用，本地和 CI 默认一律跳过。
        real_network_enabled = os.environ.get("REAL_NETWORK") == "1"
        ci_real_network_enabled = os.environ.get("CI_RUN_REAL_NETWORK") == "1"
        if not (real_network_enabled or ci_real_network_enabled):
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
        # V17.0 (2026-08-13): 补拦 requests.Session.get/post——sc_network 若走 Session 则此前
        # 真实网络泄漏(测试隔离被污染: canonical 补取缓存真实数据 → 后续 patch 测试假绿/假红)
        import requests as _requests

        monkeypatch.setattr(_requests.Session, "get", fake_get)
        monkeypatch.setattr(_requests.Session, "post", fake_post)
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


# ── real_network 测试的环境守卫 ───────────────────────────────────
# 目的（公理 A8）：把「环境不具备」与「代码回归」区分开。
# 依赖外部服务的集成测试，在上游不可用时报 FAIL 会污染回归基线——
# 它会让"每次跑测都有 2 个红"成为常态，从而掩盖真正的新增失败。
# 本守卫只判定"能不能测"，不触碰任何业务断言。
def _probe_url(url: str, timeout: float) -> bool:
    """轻量探测外部端点可达性（真实网络调用，不可被 mock）。

    仅对 ``real_network`` 标记的测试有意义：``_no_real_network`` 对这类
    测试会提前 return 而不打桩，因此这里的 urlopen 是真实的。
    """
    import urllib.request

    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return bool(resp.status < 500)
    except Exception:
        return False


@pytest.fixture
def skip_if_upstream_down():
    """工厂 fixture：上游不可用时 skip，可用时原样放行。

    用法::

        def test_x(skip_if_upstream_down):
            skip_if_upstream_down("fuyao", "https://fuyao.aicubes.cn")
            ...                      # 原断言一个都不动

    合规说明（A8）：这不是静默迁就——业务断言全部保留，
    上游可用而断言失败照样 FAIL；仅当外部服务不可达时不做无意义判定。
    """

    def _check(name: str, url: str, timeout: float = 6.0) -> None:
        if not _probe_url(url, timeout):
            pytest.skip(f"上游 {name} 不可达（{url}）——环境性跳过，非代码回归")

    return _check


# ── 临时工作目录：避免污染真实项目根 ───────────────────────────
# ── test_em_rate_limit.py 的 endpoint fixture ──────────────────────
@pytest.fixture(
    params=[
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
            "check": lambda r: r.get("success", False) is not False
            and r.get("result", {}).get("data") is not None,
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
            "check": lambda r: r.get("data", {}).get("diff") is not None
            and len(r["data"]["diff"]) > 0,
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
    ]
)
def endpoint(request):
    """test_em_rate_limit.py 使用的 endpoint fixture，遍历三个东财域名。"""
    return request.param
