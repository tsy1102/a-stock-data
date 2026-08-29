# -*- coding: utf-8 -*-
"""tests/core/test_tencent_volume_unit.py — 腾讯行情成交量单位（科创板 688 = 股）

V17.0.12 (2026-08-29) 修复：腾讯 qt.gtimg.cn 的 [6]成交量 / [7]外盘 / [8]内盘
对**科创板 688 段**返回的是「股」，其余板块返回「手」。修复前腾讯作为行情兜底源时，
科创板 volume_hand 会被放大 100×。

实测依据（20 股横截面，成交额 ÷ (量 × 现价) 反推每手股数）：
  - 主板/创业板/北交所: 99.3 ~ 100.9 → 手
  - 科创板 688:         1.01 ~ 1.02  → 股
  交叉印证: 688327 腾讯[6]=37,403,900 vs push2 f47=374,039 手，恰 100×。

纯 python 单测，不触网。
"""
from __future__ import annotations

import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tdx_client import _tencent_volume_divisor  # noqa: E402


class _FakeResponse:
    """模拟 requests.Response：只需 .text 与可写 .encoding"""

    def __init__(self, text: str):
        self.text = text
        self.encoding = "utf-8"


def _fake_tencent_line(code: str, volume_raw: float, price: str = "10.30") -> str:
    """构造一条腾讯行情响应（字段以 ~ 分隔，长度需 >= _TENCENT_MIN_FIELDS）"""
    f = [""] * 90
    f[1] = "测试股份"          # name
    f[3] = price               # price
    f[4] = "10.20"             # last_close
    f[5] = "10.25"             # open
    f[6] = str(volume_raw)     # volume_hand  <<< 被测字段
    f[10] = "5"                # bid1_vol (手, 全板块一致, 不参与换算)
    f[31] = "0.10"             # change_amt
    f[32] = "0.98"             # change_pct
    f[33] = "10.50"            # high
    f[34] = "10.10"            # low
    f[37] = "39308.3367"       # amount_wan
    f[38] = "0.45"             # turnover_pct
    f[39] = "30.10"            # pe_ttm
    f[43] = "3.92"             # amplitude_pct
    f[44] = "80.50"            # float_mcap_yi
    f[45] = "100.20"           # mcap_yi
    f[46] = "3.20"             # pb
    f[47] = "11.33"            # limit_up
    f[48] = "9.27"             # limit_down_price
    f[49] = "1.10"             # vol_ratio
    f[52] = "31.00"            # pe_dynamic
    f[53] = "32.00"            # pe_static
    f[64] = "1.50"             # dividend_yield
    f[65] = "5.00"             # roe_deduct_ttm
    f[66] = "3.00"             # roa_ttm
    f[67] = "12.00"            # high_52w
    f[68] = "8.00"             # low_52w
    f[85] = "10.29"            # panel_price
    prefix = "sh" if code.startswith("6") else ("bj" if code.startswith(("8", "4", "92")) else "sz")
    return f'v_{prefix}{code}="{"~".join(f)}";'


class TestTencentVolumeDivisor(unittest.TestCase):
    """_tencent_volume_divisor 的板块判定"""

    def test_star_market_688_returns_100(self):
        """科创板 688 段返回 100（需 ÷100 才得到手）"""
        for code in ["688327", "688426", "688500", "688553", "688589", "688981"]:
            self.assertEqual(_tencent_volume_divisor(code), 100.0, f"{code} 应为 100.0")

    def test_other_boards_return_1(self):
        """主板 / 创业板 / 北交所 返回 1（本就是手，不换算）"""
        for code in ["600519", "601288", "000001", "002034",
                     "300031", "300788", "920118", "920508", "430047", "830799", "870508"]:
            self.assertEqual(_tencent_volume_divisor(code), 1.0, f"{code} 应为 1.0")

    def test_empty_and_none_code_safe(self):
        """异常入参不抛异常，返回 1.0（安全默认）"""
        self.assertEqual(_tencent_volume_divisor(""), 1.0)
        self.assertEqual(_tencent_volume_divisor(None), 1.0)


class TestGetTencentQuoteVolumeUnit(unittest.TestCase):
    """get_tencent_quote 端到端：688 的 volume_hand 必须已 ÷100"""

    def _call(self, code: str, volume_raw: float):
        import stock_common
        from stock_common import sc_datasource
        text = _fake_tencent_line(code, volume_raw)
        # ⚠️ get_tencent_quote 内部是 `from stock_common import _quick_request`（运行时从包上取属性），
        #    必须 patch 包级属性；patch sc_datasource 模块属性不会生效 → 会静默走真实网络。
        with patch.object(stock_common, "_quick_request", return_value=_FakeResponse(text)):
            got = sc_datasource.get_tencent_quote(code)
        # 护栏：假数据没生效（返回空）时立刻失败，避免"测试通过但其实打了网络"
        self.assertTrue(got, "假响应未生效——get_tencent_quote 返回空，检查 patch 目标")
        self.assertEqual(got.get("name"), "测试股份", "假响应未生效——name 不是构造值")
        return got

    def test_star_market_volume_converted_to_hand(self):
        """688327: 腾讯给 37,403,900 股 → 应输出 374,039 手"""
        got = self._call("688327", 37403900)
        self.assertAlmostEqual(got.get("volume_hand"), 374039.0, places=2,
                               msg="科创板成交量未 ÷100，单位错误")

    def test_main_board_volume_unchanged(self):
        """600519: 腾讯给 16,126 手 → 应原样输出 16,126 手"""
        got = self._call("600519", 16126)
        self.assertAlmostEqual(got.get("volume_hand"), 16126.0, places=2,
                               msg="主板成交量被误换算")

    def test_bj_market_volume_unchanged(self):
        """920118: 北交所实测为手 → 原样输出"""
        got = self._call("920118", 8654)
        self.assertAlmostEqual(got.get("volume_hand"), 8654.0, places=2,
                               msg="北交所成交量被误换算")

    def test_bid1_vol_not_converted(self):
        """买卖档位量 [10]/[12] 全板块均为手，不参与 ÷100"""
        got = self._call("688327", 37403900)
        # [10]=5 手 → normalize 后若转股则为 500；此处只断言未被 ÷100（即不出现 0.05）
        bv = got.get("bid1_vol")
        if bv is not None:
            self.assertNotAlmostEqual(bv, 0.05, places=4,
                                      msg="买一量被错误 ÷100（[10]/[12] 全板块均为手，不应换算）")

    def test_zero_volume_not_broken_by_division(self):
        """成交量为 0 时换算不产生错误值（僵尸数据检测依赖 ==0 判据）

        ⚠️ 本测试不断言 ==0：`normalize_at_boundary` 将 0 视为缺失并输出 None
        （既有全局行为，与本次 ÷100 无关；实测 normalize({volume_hand:0.0}) -> None）。
        且僵尸检测在 **normalize 之前** 用 raw `_vol_v` 判 ==0（sc_datasource:1035），
        不受 normalize 影响。此处只需保证不会因除法产生 0 以外的错误值 / 异常。
        """
        got = self._call("688327", 0)
        vol = got.get("volume_hand")
        self.assertIn(vol, (0, 0.0, None),
                      msg=f"成交量为 0 时 volume_hand 应为 0 或 None，实际 {vol!r}")


if __name__ == "__main__":
    unittest.main()
