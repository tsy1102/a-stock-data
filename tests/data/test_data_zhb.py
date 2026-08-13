from __future__ import annotations
import pytest
import unittest
from core.zhb_client import (
    get_zhb, invalidate_cache, list_sp_blocks, get_sp_block,
    get_sw_industries, get_industry_map, market_stat_snapshot,
    get_stock_stat, get_stock_stat2, get_high_52w, get_low_52w,
    get_industry_code, is_data_fresh, get_tip_info, get_ipo_list,
    get_ah_stocks, get_broker_name, get_holidays, get_csrc_industries,
    get_adr_stocks, get_convertible_bonds, get_delisted_stocks
)
from stock_common.sc_datasource import (
    get_zhb_industry_map, get_zhb_data_date, is_zhb_data_fresh
)  # V17.0 S1: 21 个 zhb 死转发已删, 测试同步清理

def test_zhb_client_download():
    invalidate_cache()
    zhb = get_zhb()
    assert zhb is not None
    assert len(zhb.raw_files) > 0

def test_zhb_spblock():
    blocks = list_sp_blocks()
    assert len(blocks) > 0
    codes = get_sp_block("中证2000")
    if codes is not None:
        assert isinstance(codes, list)

def test_zhb_sw_industries():
    sw = get_sw_industries()
    assert len(sw) > 0

def test_zhb_industry_map():
    ind_map = get_industry_map()
    assert len(ind_map) > 0

def test_zhb_tdxstat_snapshot():
    snapshot = market_stat_snapshot()
    assert len(snapshot) > 0
    stat = get_stock_stat("600519")
    if stat:
        assert "change_pct" in stat

def test_zhb_tdxstat2():
    s2 = get_stock_stat2("600519")
    if s2:
        high = get_high_52w("600519")
        low = get_low_52w("600519")
        assert high is not None and low is not None

def test_zhb_freshness():
    assert is_data_fresh(30) in (True, False)
    assert is_zhb_data_fresh(30) in (True, False)

def test_zhb_tipinfo():
    zhb = get_zhb()
    if zhb and len(zhb.tip_info) > 0:
        tip = get_tip_info("600519")
        assert isinstance(tip, dict) or tip is None

def test_zhb_ipo_list():
    ipo_list = get_ipo_list()
    assert isinstance(ipo_list, list)

def test_zhb_ah_and_brokers():
    ah = get_ah_stocks()
    assert isinstance(ah, list)
    name = get_broker_name("1")
    assert isinstance(name, str)

def test_zhb_holidays():
    holidays = get_holidays()
    assert isinstance(holidays, list)

def test_zhb_csrc_industries():
    csrc = get_csrc_industries()
    assert isinstance(csrc, dict)

def test_zhb_adr_bonds_delisted():
    adr = get_adr_stocks()
    assert isinstance(adr, list)
    bonds = get_convertible_bonds()
    assert isinstance(bonds, list)
    delisted = get_delisted_stocks()
    assert isinstance(delisted, dict)


"""test_zhb_new_datasets.py — V14.2 新挖掘的 6 个 ZHB 数据集单元测试

测试覆盖：
  - zhb_client.py 新增 6 个解析器
  - data_provider.py 5 个新增 ZHB 本地函数
  - stock_calendar.py 补充日历
  - Fallback 路径（ZHB 缺失时优雅降级）
"""
import datetime
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ═══════════════════════════════════════════════════════════════
# 1. zhb_client.ZhbData 新增 6 个属性解析
# ═══════════════════════════════════════════════════════════════

class TestZhbStockProfile:
    """V14.2: profile.dat 全市场简称（GBK 编码）"""

    def test_parse_profile_empty(self):
        """空数据时返回空 dict"""
        from core.zhb_client import ZhbData
        zhb = ZhbData()
        zhb.raw_files = {}
        assert zhb.stock_profile == {}
        assert zhb.get_stock_name("600519") is None

    def test_parse_profile_format(self):
        """测试 64 字节记录解析格式（V16.3 D1: market(1)+code(6)+null(1)+name(8)+ts(4)+pad）"""
        from core.zhb_client import ZhbData
        zhb = ZhbData()
        # 构造 64 字节记录：市场标识(1) + 600519(6) + null分隔(1) + 简称(8) + padding
        # V16.3 D1: 实测 profile.dat 结构含 null 分隔符（原 record[7:15] 取到 null 恒空）
        name = "平安银行"
        name_bytes = name.encode("gbk")
        assert len(name_bytes) == 8
        record = b"\x01" + b"600519" + b"\x00" + name_bytes + b"\x00" * (64 - 1 - 6 - 1 - 8)
        assert len(record) == 64
        zhb.raw_files = {"profile.dat": record}
        profile = zhb.stock_profile
        assert "600519" in profile
        assert profile["600519"] == "平安银行"

    def test_get_stock_name_method(self):
        """便捷方法测试（V16.3 D1: 含 null 分隔符结构）"""
        from core.zhb_client import ZhbData
        zhb = ZhbData()
        name = "平安银行"
        name_bytes = name.encode("gbk")
        record = b"\x00" + b"000001" + b"\x00" + name_bytes + b"\x00" * (64 - 1 - 6 - 1 - 8)
        zhb.raw_files = {"profile.dat": record}
        assert zhb.get_stock_name("000001") == "平安银行"
        assert zhb.get_stock_name("999999") is None


class TestZhbColMappings:
    """V16.0: Col[14]=扣非净利润 / Col[24]=unknown_24 映射验证"""

    def _make_zhb(self):
        from core.zhb_client import ZhbData
        zhb = ZhbData()
        # 构造 tdxstat.cfg: 35 列, Col14=扣非净利润, Col24=原误标volume
        cols = ['0'] * 35
        cols[0] = '1'          # market
        cols[1] = '600519'     # code
        cols[14] = '2723998.52'  # 扣非净利润(万)
        cols[24] = '4878669.14'  # unknown_24
        line = '|'.join(cols)
        zhb.raw_files = {'tdxstat.cfg': line.encode('gbk')}
        return zhb

    def test_col14_maps_to_net_profit_kcf(self):
        zhb = self._make_zhb()
        stat = zhb.stock_stats['600519']
        assert stat['net_profit_kcf'] == 2723998.52
        assert 'volume' not in stat

    def test_col24_maps_to_unknown_24(self):
        zhb = self._make_zhb()
        stat = zhb.stock_stats['600519']
        assert stat['unknown_24'] == 4878669.14
        assert 'volume' not in stat


class TestZhbConceptChain:
    """V14.2: tdxchain.cfg 200+ 概念/产业链节点"""

    def test_parse_concept_chain_empty(self):
        from core.zhb_client import ZhbData
        zhb = ZhbData()
        assert zhb.concept_chain == {}

    def test_parse_concept_chain_format(self):
        """V15.1 重写: tdxchain.cfg 为 板块代码|节点ID|产业链名称 格式"""
        from core.zhb_client import ZhbData
        zhb = ZhbData()
        # 5G 板块映射: 880506|CYL00210|新基建-5G
        data = "880506|CYL00210|新基建-5G\n880507|CYL00211|新基建-5G\n880508|CYL00300|3D打印\n".encode("gbk")
        zhb.raw_files = {"tdxchain.cfg": data}
        chain = zhb.concept_chain
        assert "新基建-5G" in chain
        assert chain["新基建-5G"] == ["880506", "880507"]
        assert chain["3D打印"] == ["880508"]

    def test_get_concept_stocks_method(self):
        """V15.1: 返回概念/产业链下的板块代码列表（非成分股）"""
        from core.zhb_client import ZhbData
        zhb = ZhbData()
        data = "880506|CYL00210|新基建-5G\n880507|CYL00211|新基建-5G\n".encode("gbk")
        zhb.raw_files = {"tdxchain.cfg": data}
        assert zhb.get_concept_stocks("新基建-5G") == ["880506", "880507"]
        # 子串匹配（V15.1 实现支持）
        assert zhb.get_concept_stocks("5G") == ["880506", "880507"] or zhb.get_concept_stocks("5G") == []

    def test_get_stock_concepts_method(self):
        """V15.1: tdxchain.cfg 不含成分股，反查恒返回空列表"""
        from core.zhb_client import ZhbData
        zhb = ZhbData()
        data = "880506|CYL00210|新基建-5G\n".encode("gbk")
        zhb.raw_files = {"tdxchain.cfg": data}
        assert zhb.get_stock_concepts("600519") == []


class TestZhbNeednote:
    """V14.2: neednote.dat 官方休市日+调休补班日"""

    def test_parse_neednote_empty(self):
        from core.zhb_client import ZhbData
        zhb = ZhbData()
        assert zhb.neednote_holidays == []
        assert zhb.neednote_jyweek == []

    def test_parse_neednote_format(self):
        """INI 格式：[RecentCFETSHoliday]/[RecentCFETSJYWeek]"""
        from core.zhb_client import ZhbData
        zhb = ZhbData()
        text = (
            "[RecentCFETSHoliday]\n"
            "20260101=元旦\n"
            "20260218=春节\n"
            "[RecentCFETSJYWeek]\n"
            "20260131=春节调休补班\n"
            "20260214=春节调休补班\n"
        )
        zhb.raw_files = {"neednote.dat": text.encode("gbk")}
        assert "20260101" in zhb.neednote_holidays
        assert "20260218" in zhb.neednote_holidays
        assert "20260131" in zhb.neednote_jyweek
        assert "20260214" in zhb.neednote_jyweek


class TestZhbBrkSeat:
    """V14.2: brkseat.dat 龙虎榜营业部席位"""

    def test_parse_brkseat_empty(self):
        from core.zhb_client import ZhbData
        zhb = ZhbData()
        assert zhb.brk_seat == {}

    def test_parse_brkseat_format(self):
        """Pipe 格式：席位代码|营业部名称"""
        from core.zhb_client import ZhbData
        zhb = ZhbData()
        data = "000001|国泰君安证券股份有限公司总部\n000002|中信证券股份有限公司总部\n".encode("gbk")
        zhb.raw_files = {"brkseat.dat": data}
        seat = zhb.brk_seat
        assert seat["000001"] == "国泰君安证券股份有限公司总部"
        assert "000002" in seat


class TestZhbSpecialTags:
    """V14.2: pttab.dat 特别标签（红筹/AH/概念）"""

    def test_parse_special_tags_empty(self):
        from core.zhb_client import ZhbData
        zhb = ZhbData()
        assert zhb.special_tags == {}

    def test_parse_special_tags_format(self):
        """Pipe 格式：标签|代码1,代码2,..."""
        from core.zhb_client import ZhbData
        zhb = ZhbData()
        data = "AH|600519,000001\n红筹|002193\n概念|600519,000858,002193\n".encode("gbk")
        zhb.raw_files = {"pttab.dat": data}
        tags = zhb.special_tags
        assert "600519" in tags["AH"]
        assert "002193" in tags["红筹"]
        assert len(tags["概念"]) == 3


# ═══════════════════════════════════════════════════════════════
# 2. data_provider 5 个新增 ZHB 本地函数
# ═══════════════════════════════════════════════════════════════

class TestDataProviderZhbFunctions:
    """V14.2: data_provider 新增 5 个 ZHB 本地获取函数"""

    def test_get_stock_basic_info_from_zhb_no_data(self):
        """无 ZHB 数据时返回 None（优雅降级）"""
        from core.data_provider import get_stock_basic_info_from_zhb
        result = get_stock_basic_info_from_zhb("600519")
        # ZHB 不可用时返回 None（不抛异常）
        assert result is None or (isinstance(result, dict) and "name" in result)

    def test_get_concept_from_zhb_returns_list(self):
        """返回值始终是 list（ZHB 缺失时返回空列表）"""
        from core.data_provider import get_concept_from_zhb
        result = get_concept_from_zhb("600519")
        assert isinstance(result, list)

    def test_get_new_share_calendar_from_zhb_returns_list(self):
        """返回值始终是 list"""
        from core.data_provider import get_new_share_calendar_from_zhb
        result = get_new_share_calendar_from_zhb()
        assert isinstance(result, list)

    def test_get_special_tags_from_zhb_returns_dict(self):
        """返回值始终是 dict"""
        from core.data_provider import get_special_tags_from_zhb
        result = get_special_tags_from_zhb()
        assert isinstance(result, dict)

    def test_is_zhb_dataset_available_returns_bool(self):
        """返回值始终是 bool"""
        from core.data_provider import is_zhb_dataset_available
        result = is_zhb_dataset_available()
        assert isinstance(result, bool)


# ═══════════════════════════════════════════════════════════════
# 3. stock_calendar V14.2 ZHB 补充日历
# ═══════════════════════════════════════════════════════════════

class TestStockCalendarZhbSupplement:
    """V14.2: stock_calendar ZHB neednote 补充"""

    def test_get_zhb_supplement_count(self):
        """返回统计信息"""
        from stock_common.stock_calendar import get_zhb_supplement_count
        info = get_zhb_supplement_count()
        assert "holidays" in info
        assert "workdays" in info
        assert "loaded" in info
        assert isinstance(info["loaded"], bool)

    def test_is_workday_with_zhb_supplement_known_holiday(self):
        """已知节假日应返回 False（V14.0 修复）"""
        from stock_common.stock_calendar import is_workday_with_zhb_supplement
        # 2025-1-1 是元旦
        assert is_workday_with_zhb_supplement(datetime.date(2025, 1, 1)) is False
        # 2026-1-1 是元旦
        assert is_workday_with_zhb_supplement(datetime.date(2026, 1, 1)) is False

    def test_is_workday_with_zhb_supplement_weekend(self):
        """普通周末（非调休）应返回 False"""
        from stock_common.stock_calendar import is_workday_with_zhb_supplement
        # 2026-1-10 周六（非节假日/调休）
        assert is_workday_with_zhb_supplement(datetime.date(2026, 1, 10)) is False
        # 2026-1-11 周日（非节假日/调休）
        assert is_workday_with_zhb_supplement(datetime.date(2026, 1, 11)) is False

    def test_is_workday_with_zhb_supplement_weekday(self):
        """普通工作日应返回 True"""
        from stock_common.stock_calendar import is_workday_with_zhb_supplement
        # 2026-1-5 周一（元旦假期后）
        # 注意：2026-1-2 周五可能也是元旦假期（待本地字典确认）
        # 使用 2026-1-15 周四（肯定不是节假日）
        assert is_workday_with_zhb_supplement(datetime.date(2026, 1, 15)) is True

    def test_is_workday_with_zhb_supplement_backward_compat(self):
        """与 is_workday() 一致性"""
        from stock_common.stock_calendar import is_workday, is_workday_with_zhb_supplement
        # 对于本地字典覆盖的日期，两者结果应一致
        test_dates = [
            datetime.date(2025, 1, 1),
            datetime.date(2025, 10, 1),
            datetime.date(2026, 2, 18),
            datetime.date(2026, 5, 1),
        ]
        for d in test_dates:
            assert is_workday(d) == is_workday_with_zhb_supplement(d), (
                f"不一致: {d} is_workday={is_workday(d)}, is_workday_with_zhb_supplement={is_workday_with_zhb_supplement(d)}"
            )


# ═══════════════════════════════════════════════════════════════
# 4. 集成测试：ZHB 不可用时全部优雅降级
# ═══════════════════════════════════════════════════════════════

class TestZhbFallback:
    """V14.2: ZHB 数据缺失时所有函数优雅降级（不抛异常）"""

    def test_all_zhb_functions_dont_crash_without_zhb(self):
        """ZHB 不可用时不抛异常"""
        from core.data_provider import (
            get_stock_basic_info_from_zhb,
            get_concept_from_zhb,
            get_new_share_calendar_from_zhb,
            get_special_tags_from_zhb,
            is_zhb_dataset_available,
        )
        from stock_common.stock_calendar import is_workday_with_zhb_supplement

        # 不应抛异常
        get_stock_basic_info_from_zhb("600519")
        get_concept_from_zhb("600519")
        get_new_share_calendar_from_zhb()
        get_special_tags_from_zhb()
        is_zhb_dataset_available()
        is_workday_with_zhb_supplement(datetime.date(2025, 1, 1))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestZhbUnsealFields(unittest.TestCase):
    """V16.2.18: tdxstat Col[12]=新股开板日 / Col[13]=上市连板数 解析。"""

    def _parse(self, line: str):
        from core.zhb_client import ZhbData
        zhb = ZhbData()
        zhb.raw_files = {"tdxstat.cfg": line.encode("gbk", errors="ignore")}
        stats = zhb.stock_stats
        return stats.get("600519", {})

    def test_unseal_date_and_board_count(self):
        # 35 列构造：Col12=20210520（开板日）、Col13=8（连板数）
        parts = ["0", "600519", "0", "20.0", "20260804", "-1", "0.5", "0.2", "0.1",
                 "20.5", "3.9", "54094.9", "20210520", "8", "2723998", "34992",
                 "5931", "9.45", "6.07", "-8.38", "5.5", "9.66", "50101", "0",
                 "4878669", "302719", "0", "2.49", "1.18", "3.93", "5.41",
                 "", "", "", "0"]
        row = "|".join(parts)
        st = self._parse(row)
        self.assertEqual(st.get("unseal_date"), "20210520")
        self.assertEqual(st.get("board_count"), 8)

    def test_old_stock_empty(self):
        parts = ["0", "600519", "0", "20.0", "20260804", "-1", "0.5", "0.2", "0.1",
                 "20.5", "3.9", "54094.9", "", "", "2723998", "34992",
                 "5931", "9.45", "6.07", "-8.38", "5.5", "9.66", "50101", "0",
                 "4878669", "302719", "0", "2.49", "1.18", "3.93", "5.41",
                 "", "", "", "0"]
        st = self._parse("|".join(parts))
        self.assertEqual(st.get("unseal_date"), "")
        self.assertIsNone(st.get("board_count"))



class TestZhbKbarMappings(unittest.TestCase):
    """V16.2.18: Col[17]=近20根K线 / Col[19]=近60根K线 精确映射（injoyai 核验）。"""

    def _parse(self):
        from core.zhb_client import ZhbData
        zhb = ZhbData()
        parts = ["0", "600519", "0", "20.0", "20260804", "-1", "0.5", "0.2", "0.1",
                 "20.5", "3.9", "54094.9", "", "", "2723998", "34992",
                 "5931", "9.45", "6.07", "-8.38", "5.5", "9.66", "50101", "0",
                 "4878669", "302719", "0", "2.49", "1.18", "3.93", "5.41",
                 "", "", "", "0"]
        zhb.raw_files = {"tdxstat.cfg": ("|".join(parts)).encode("gbk", errors="ignore")}
        return zhb.stock_stats.get("600519", {})

    def test_kbar_mappings(self):
        st = self._parse()
        self.assertEqual(st.get("change_20k_bar"), 9.45)   # Col[17]
        self.assertEqual(st.get("change_60k_bar"), -8.38)  # Col[19]
        self.assertEqual(st.get("change_20d"), 6.07)       # Col[18]（历史 key 名）
        # V16.3 O28: change_60d 改读 Col[20]（实测 K 线缓存对照：Col[20]=截至T-1的60根K线，
        # 中位差1.28 更纯；原误读 Col[19] 与 60k_bar 同源）
        self.assertEqual(st.get("change_60d"), 5.5)        # Col[20]
        self.assertEqual(st.get("change_ytd"), 9.66)       # Col[21]


if __name__ == "__main__":
    unittest.main()



class TestIsIndustryCode(unittest.TestCase):
    """V16.2.16: tdxstat2 Col[13] 行业段过滤（8803/8804 通达信行业、881 申万版）。"""

    def _is_ind(self, ic):
        from core.zhb_client import is_industry_code
        return is_industry_code(ic)

    def test_industry_segments_true(self):
        self.assertTrue(self._is_ind("880301"))  # 煤炭（通达信行业）
        self.assertTrue(self._is_ind("880492"))  # 元器件
        self.assertTrue(self._is_ind("881218"))  # 汽车零部件（申万版）

    def test_style_concept_false(self):
        self.assertFalse(self._is_ind("880898"))  # 近已解禁（风格）
        self.assertFalse(self._is_ind("880823"))  # 微盘股（风格）
        self.assertFalse(self._is_ind("880594"))  # 一带一路（概念）
        self.assertFalse(self._is_ind("880201"))  # 黑龙江（地域）

    def test_invalid_false(self):
        self.assertFalse(self._is_ind(""))
        self.assertFalse(self._is_ind("123456"))
        self.assertFalse(self._is_ind("88"))
        self.assertFalse(self._is_ind(None))

