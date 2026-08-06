# -*- coding: utf-8 -*-
"""tests/test_api_stability.py — 多数据源接口稳定性 + 字段核实守护测试

背景（2026-08-03 用户反馈）：
  "测试时接口是否稳定也是个大问题，非常有可能因为接口抖动等原因
   就抛弃了后期的核实和印证。"

本测试的目的：
  1. 验证腾讯/新浪/东财 push2 三源接口可访问且字段与字典一致（联网核实守护）
  2. 接口抖动（偶发断连/超时）自动重试 3 次，避免误报
  3. 仅在 REAL_NETWORK=1 时运行（conftest 约定），CI 自动 skip

运行方式：
  $env:REAL_NETWORK=1; .\scripts\run_tests.ps1 -Mode real
"""
from __future__ import annotations

import os
import sys
import time
import urllib3

import pytest

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

pytestmark = pytest.mark.real_network  # 需 REAL_NETWORK=1 才运行

_PROXIES = {"http": None, "https": None}
_HDRS = {"User-Agent": "Mozilla/5.0"}


def _get_with_retry(url, params=None, headers=None, timeout=10, retries=3, wait=1.5):
    """带重试的 GET：接口抖动自动重试，3 次仍失败才报错。"""
    import requests

    last_err = None
    for attempt in range(retries):
        try:
            r = requests.get(
                url, params=params, headers=headers or _HDRS,
                timeout=timeout, proxies=_PROXIES, verify=True,
            )
            if r.status_code == 200:
                return r
            last_err = f"HTTP {r.status_code}"
        except Exception as e:
            last_err = str(e)
        time.sleep(wait * (attempt + 1))
    pytest.fail(f"接口 {url} 重试 {retries} 次仍失败: {last_err}")


class TestTencentStability:
    """腾讯 qt.gtimg.cn 接口稳定性 + 字段核实"""

    def test_tencent_fields_verified(self):
        """核实腾讯关键字段索引与字典一致（[3]价 [32]涨跌幅 [39]PE [44]流通 [45]总 [72]流通股本 [73]总股本）"""
        r = _get_with_retry("https://qt.gtimg.cn/q=sh600519,sz000001,sh601398")
        r.encoding = "gbk"
        rows = {}
        for line in r.text.strip().split(";"):
            if "=" not in line or '"' not in line:
                continue
            vals = line.split('"')[1].split("~")
            if len(vals) < 74:
                continue
            rows[vals[2]] = vals
        assert "600519" in rows, "腾讯返回缺少 600519"
        m = rows["600519"]
        # [3] 当前价 与 [4] 昨收 差应在 ±10% 内（用已知值粗验证）
        price = float(m[3])
        prev = float(m[4])
        assert price > 0 and prev > 0
        chg_calc = (price - prev) / prev * 100
        chg_field = float(m[32])
        assert abs(chg_calc - chg_field) < 1.0, (
            f"腾讯 [32] 涨跌幅({chg_field}) 与 计算值({chg_calc:.2f}) 不一致 → 字段索引可能漂移"
        )
        # [44] 流通市值 < [45] 总市值（工行应成立）
        g = rows["601398"]
        assert float(g[44]) < float(g[45]), "腾讯 [44]流通市值 应 < [45]总市值"
        # [73] 总股本 >= [72] 流通股本
        assert float(g[73]) >= float(g[72]), "腾讯 [73]总股本 应 >= [72]流通股本"
        # [39] PE(TTM) 合理范围（茅台 10-40）
        assert 5 < float(m[39]) < 60, f"茅台 PE-TTM={m[39]} 异常"


class TestSinaStability:
    """新浪 hq.sinajs.cn 接口稳定性 + 字段核实"""

    def test_sina_fields_verified(self):
        """核实新浪字段索引（[0]名称 [3]价 [8]量 [9]额）"""
        r = _get_with_retry(
            "https://hq.sinajs.cn/list=sh600519,sz000001",
            headers={"Referer": "https://finance.sina.com.cn/", ** _HDRS},
        )
        r.encoding = "gbk"
        text = r.text
        assert 'hq_str_sh600519="' in text, "新浪返回缺少茅台"
        vals = text.split('hq_str_sh600519="')[1].split('"')[0].split(",")
        assert len(vals) >= 33, f"新浪字段数异常: {len(vals)}"
        assert vals[0] == "贵州茅台", f"新浪 [0] 名称={vals[0]} 异常"
        price = float(vals[3])
        assert price > 0
        vol = float(vals[8])
        assert vol > 0, "新浪 [8] 成交量=0（停牌或接口异常）"
        assert float(vals[9]) > 0, "新浪 [9] 成交额=0"


class TestEastMoneyStability:
    """东财 push2 接口稳定性（注意：此接口有风控，测试间隔需 ≥1.5s）

    风控说明（2026-08-03 实测）：东财系接口有 IP 级临时风控，
    密集请求会触发 RemoteDisconnected（连接被拒）。此时**不是代码 bug**，
    停止 30-60 分钟自动解除（参考仓库 FAQ）。
    因此本测试在检测到"连接被拒"时跳过（pytest.skip）而非失败，
    避免把接口抖动误报为代码回归。
    """

    def test_push2_batch_fields_verified(self):
        """核实 push2 ulist.np/get 行业/概念字段（f100 行业 f103 概念）"""
        import requests

        last_err = None
        for attempt in range(2):
            try:
                r = requests.get(
                    "https://push2.eastmoney.com/api/qt/ulist.np/get",
                    params={
                        "fltt": "2", "invt": "2",
                        "secids": "1.600519",
                        "fields": "f12,f14,f100,f102,f103,f112,f113",
                        "ut": "f057cbcbce2a86e2866ab8877db1d059",
                    },
                    headers={"Referer": "https://quote.eastmoney.com/", **_HDRS},
                    timeout=15, proxies=_PROXIES, verify=True,
                )
                if r.status_code == 200:
                    break
                last_err = f"HTTP {r.status_code}"
            except Exception as e:
                last_err = str(e)
            time.sleep(5)
        else:
            # 连接被拒 = IP 级临时风控（非代码 bug），跳过而非失败
            if last_err and "RemoteDisconnected" in last_err:
                pytest.skip(
                    "push2 IP 级临时风控（RemoteDisconnected）——停止 30-60 分钟自动解除，"
                    "非代码回归。验证字段请稍后重跑。"
                )
            pytest.fail(f"push2 接口失败: {last_err}")

        d = r.json()
        diff = (d.get("data") or {}).get("diff") or []
        assert diff, f"push2 返回无数据: {d.get('message', '')}"
        item = diff[0] if isinstance(diff, list) else diff.get("600519", {})
        assert str(item.get("f12")) == "600519", "push2 f12 代码不符"
        assert item.get("f100"), "push2 f100 行业为空"
        assert item.get("f103"), "push2 f103 概念为空"
        assert float(item.get("f112", 0)) > 0, "push2 f112 EPS 异常"


class TestV16NewApis:
    """V16.0 新增接口稳定性（重点监控池/板块资金流）"""

    def test_em_stock_monitor_verified(self):
        """重点监控池：mobappconfig 接口（无 push2 风控面，应稳定可用）"""
        import requests

        r = _get_with_retry(
            "https://mobappconfig.securities.eastmoney.com/emcfg/stock_monitor.json",
            headers={"Referer": "https://vipmoney.eastmoney.com/", **_HDRS},
            timeout=15, retries=2, wait=2.0,
        )
        rows = r.json()
        assert isinstance(rows, list) and len(rows) > 0, "重点监控池为空"
        first = rows[0]
        for k in ("STKCODE", "STKNAME", "MARKET", "VALIDATESTARTDATE", "VALIDATEENDDATE"):
            assert k in first, f"重点监控池缺字段 {k}"

    def test_board_fund_flow_verified(self):
        """板块资金流：push2 clist（有风控容忍——RemoteDisconnected 跳过）"""
        import requests

        last_err = None
        r = None
        for attempt in range(2):
            try:
                r = requests.get(
                    "http://83.push2.eastmoney.com/api/qt/clist/get",
                    params={
                        "pn": "1", "pz": "5", "po": "1", "np": "1",
                        "fltt": "2", "invt": "2", "fs": "m:90+t:2+f:!50",
                        "fields": "f12,f14,f2,f3,f62",
                        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
                    },
                    headers={"Referer": "https://quote.eastmoney.com/", **_HDRS},
                    timeout=15, proxies=_PROXIES, verify=True,
                )
                if r.status_code == 200:
                    break
                last_err = f"HTTP {r.status_code}"
            except Exception as e:
                last_err = str(e)
            time.sleep(5)
        else:
            if last_err and "RemoteDisconnected" in last_err:
                pytest.skip("push2 IP 风控，非代码回归")
            pytest.fail(f"板块资金流失败: {last_err}")

        d = r.json()
        diff = (d.get("data") or {}).get("diff") or []
        assert diff, "板块资金流无数据"
        first = diff[0]
        assert first.get("f12", "").startswith("BK"), "板块代码应为 BK 前缀"
        assert first.get("f14"), "板块名称为空"
        assert first.get("f62") is not None, "主力净流入为空"
