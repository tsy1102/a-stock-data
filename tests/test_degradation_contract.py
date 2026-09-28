"""P2-B：降级等价性契约断言（采纳 Ashare 理念 2）。

针对 `stock_common.sc_datasource.get_index_kline_closes` 的四源降级链
（L1 TDX 指数K线 → L2 腾讯 ifzq 前复权日K → L3 新浪纯 JSON → L3b 新浪 jsonp 兜底
→ L4 腾讯实时 2 值），把「降级不改变语义」从人肉约定升级为**可断言的不变式**：

  - 等价契约：L1/L2/L3 任一主导时，返回结构等价（同序列收盘价、升序、全正浮点）。
  - 结构契约：返回值为 `List[float]`，元素 > 0 且非降序；L4 为**显式声明**的缩减契约
    （仅 `[昨收, 今收]` 两值，非序列），差异须显式标注。
  - 变异检验：逐层强制单独生效，断言产出与契约/等价基准一致；若生产层解析错位
    （如列序错乱）导致产出偏离，本测试即转红（详见 `test_contract_checker_is_not_vacuous`）。

仅新增测试，不改动任何生产逻辑。
"""

from __future__ import annotations

from unittest import mock

import pytest

from stock_common.sc_datasource import get_index_kline_closes, _eastmoney
import stock_common.sc_datasource as sd

# V17.2.18 重构后片段为独立模块: get_index_kline_closes 定义在 _eastmoney, _quick_request 由其
# 自身命名空间解析; 故补丁须打在 _eastmoney._quick_request (而非包级 re-export 副本) 才能穿透。


EXPECTED = [10.0, 11.0, 12.0]  # 等价基准：L1/L2/L3 应产出完全一致


class _FakeResp:
    """模拟 requests.Response：支持 .text / .json() / .encoding。"""

    def __init__(self, text: str = "", json_data=None):
        self.text = text
        self._json = json_data
        self.encoding = None

    def json(self):
        if self._json is None:
            raise ValueError("no json payload")
        return self._json


def _assert_full_contract(closes) -> bool:
    """L1/L2/L3 完整序列契约：List[float]，全正、非降序、≥2 点。"""
    assert isinstance(closes, list), "返回值必须是 list"
    assert all(isinstance(x, float) and x > 0 for x in closes), "每个元素为正浮点"
    assert closes == sorted(closes), "须按日期升序（非降序）"
    assert len(closes) >= 2, "完整序列应 ≥ 2 个数据点"
    return True


def _url_aware(responses: dict):
    """按 URL 子串返回预置响应；未命中返回 None（该层视为失败）。"""

    def _m(url, **kwargs):
        for sub, resp in responses.items():
            if sub in url:
                return resp
        return None

    return _m


# ───────────────────────── L1：TDX 指数K线（TCP） ─────────────────────────


def test_layer_l1_tdx_contract():
    keys = ["date", "open", "close"]
    rows = [["2026-09-01", 1.0, 10.0], ["2026-09-02", 1.0, 11.0], ["2026-09-03", 1.0, 12.0]]
    with (
        mock.patch("core.tdx_client.tdx_get_index_bars", return_value=(keys, rows)),
        mock.patch.object(_eastmoney, "_quick_request", mock.Mock(return_value=None)),
    ):
        out = get_index_kline_closes("sh000001", days=3)
    _assert_full_contract(out)
    assert out == EXPECTED


# ─────────────────── L2：腾讯 ifzq 前复权日K（完整序列） ───────────────────


def test_layer_l2_tencent_fqkline_contract():
    payload = {
        "data": {
            "sh000001": {
                "qfqday": [
                    ["2026-09-01", 1.0, 10.0],
                    ["2026-09-02", 1.0, 11.0],
                    ["2026-09-03", 1.0, 12.0],
                ]
            }
        }
    }
    with (
        mock.patch("core.tdx_client.tdx_get_index_bars", side_effect=Exception("no tdx")),
        mock.patch.object(
            _eastmoney, "_quick_request", mock.Mock(return_value=_FakeResp(json_data=payload))
        ),
    ):
        out = get_index_kline_closes("sh000001", days=3)
    _assert_full_contract(out)
    assert out == EXPECTED


# ─────────────────────── L3：新浪纯 JSON host ───────────────────────


def test_layer_l3_sina_json_contract():
    resp = _FakeResp(text='[{"close":"10.0"},{"close":"11.0"},{"close":"12.0"}]')
    with (
        mock.patch("core.tdx_client.tdx_get_index_bars", side_effect=Exception("no tdx")),
        mock.patch.object(_eastmoney, "_quick_request", _url_aware({"json_v2.php": resp})),
    ):
        out = get_index_kline_closes("sh000001", days=3)
    _assert_full_contract(out)
    assert out == EXPECTED


# ─────────────────────── L3b：新浪 jsonp 兜底 ───────────────────────


def test_layer_l3b_sina_jsonp_contract():
    resp = _FakeResp(text='var([{"close":"10.0"},{"close":"11.0"},{"close":"12.0"}])')
    with (
        mock.patch("core.tdx_client.tdx_get_index_bars", side_effect=Exception("no tdx")),
        mock.patch.object(_eastmoney, "_quick_request", _url_aware({"jsonp_v2.php": resp})),
    ):
        out = get_index_kline_closes("sh000001", days=3)
    _assert_full_contract(out)
    assert out == EXPECTED


# ───────────────── 等价性：四层任意主导应产出等价 ─────────────────


def test_degradation_equivalence_l1_l2_l3():
    tdx_payload = (
        ["date", "open", "close"],
        [["2026-09-01", 1.0, 10.0], ["2026-09-02", 1.0, 11.0], ["2026-09-03", 1.0, 12.0]],
    )
    tencent_payload = {
        "data": {
            "sh000001": {
                "qfqday": [
                    ["2026-09-01", 1.0, 10.0],
                    ["2026-09-02", 1.0, 11.0],
                    ["2026-09-03", 1.0, 12.0],
                ]
            }
        }
    }
    sina_text = '[{"close":"10.0"},{"close":"11.0"},{"close":"12.0"}]'
    sina_jsonp = 'var([{"close":"10.0"},{"close":"11.0"},{"close":"12.0"}])'
    tdx_ok = mock.Mock(return_value=tdx_payload)
    tdx_fail = mock.Mock(side_effect=Exception("no tdx"))

    def run_with(tdx_patch, url, resp):
        responses = {url: resp} if (url and resp) else {}
        with (
            mock.patch("core.tdx_client.tdx_get_index_bars", tdx_patch),
            mock.patch.object(_eastmoney, "_quick_request", _url_aware(responses)),
        ):
            return get_index_kline_closes("sh000001", days=3)

    # L1 主导
    assert run_with(tdx_ok, None, None) == EXPECTED
    # L2 主导（tdx 失败，L2 走 ifzq）
    assert run_with(tdx_fail, "ifzq.gtimg.cn", _FakeResp(json_data=tencent_payload)) == EXPECTED
    # L3 主导（tdx+L2 失败，L3 json）
    assert run_with(tdx_fail, "json_v2.php", _FakeResp(text=sina_text)) == EXPECTED
    # L3b 主导
    assert run_with(tdx_fail, "jsonp_v2.php", _FakeResp(text=sina_jsonp)) == EXPECTED


# ─────────── L4：显式缩减契约（仅 [昨收, 今收] 两值） ───────────


def test_layer_l4_reduced_contract():
    # 真实 qt.gtimg.cn 响应形如 v_sh000001="1~...~<close>~<pre_close>~"
    # （函数取 v[3]=close、v[4]=pre_close，返回 [pre_close, close]）
    realtime_text = 'v_sh000001="sh000001~name~x~10.5~11.0~"'
    with (
        mock.patch("core.tdx_client.tdx_get_index_bars", side_effect=Exception("no tdx")),
        mock.patch.object(
            _eastmoney, "_quick_request", _url_aware({"qt.gtimg.cn": _FakeResp(text=realtime_text)})
        ),
    ):
        out = get_index_kline_closes("sh000001", days=3)
    # L4 返回 [pre_close, close]，是显式声明的缩减契约，而非完整序列
    assert isinstance(out, list) and len(out) == 2
    assert all(x > 0 for x in out)
    assert out[0] == 11.0 and out[1] == 10.5


# ───────────── 全部失败兜底：返回空序列（不静默造假） ─────────────


def test_all_layers_failed_returns_empty():
    with (
        mock.patch("core.tdx_client.tdx_get_index_bars", side_effect=Exception("no tdx")),
        mock.patch.object(_eastmoney, "_quick_request", mock.Mock(return_value=None)),
    ):
        out = get_index_kline_closes("sh000001", days=3)
    assert out == []


# ───────────── 变异检验：契约检查器本身非空洞 ─────────────


def test_contract_checker_is_not_vacuous():
    # 降序（非升序）应判失败
    with pytest.raises(AssertionError):
        _assert_full_contract([12.0, 11.0, 10.0])
    # 含非正价应判失败
    with pytest.raises(AssertionError):
        _assert_full_contract([10.0, 0.0, 12.0])
    # 非浮点应判失败
    with pytest.raises(AssertionError):
        _assert_full_contract(["10.0", "11.0", "12.0"])
    # 单点序列应判失败（<2）
    with pytest.raises(AssertionError):
        _assert_full_contract([10.0])
