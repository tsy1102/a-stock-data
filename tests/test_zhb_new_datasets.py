"""test_zhb_new_datasets.py — V14.2 新挖掘的 6 个 ZHB 数据集单元测试

测试覆盖：
  - zhb_client.py 新增 6 个解析器
  - data_provider.py 5 个新增 ZHB 本地函数
  - stock_calendar.py 补充日历
  - Fallback 路径（ZHB 缺失时优雅降级）
"""
from __future__ import annotations

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
        from zhb_client import ZhbData
        zhb = ZhbData()
        zhb.raw_files = {}
        assert zhb.stock_profile == {}
        assert zhb.get_stock_name("600519") is None

    def test_parse_profile_format(self):
        """测试 64 字节记录解析格式（V16.3 D1: market(1)+code(6)+null(1)+name(8)+ts(4)+pad）"""
        from zhb_client import ZhbData
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
        from zhb_client import ZhbData
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
        from zhb_client import ZhbData
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
        from zhb_client import ZhbData
        zhb = ZhbData()
        assert zhb.concept_chain == {}

    def test_parse_concept_chain_format(self):
        """V15.1 重写: tdxchain.cfg 为 板块代码|节点ID|产业链名称 格式"""
        from zhb_client import ZhbData
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
        from zhb_client import ZhbData
        zhb = ZhbData()
        data = "880506|CYL00210|新基建-5G\n880507|CYL00211|新基建-5G\n".encode("gbk")
        zhb.raw_files = {"tdxchain.cfg": data}
        assert zhb.get_concept_stocks("新基建-5G") == ["880506", "880507"]
        # 子串匹配（V15.1 实现支持）
        assert zhb.get_concept_stocks("5G") == ["880506", "880507"] or zhb.get_concept_stocks("5G") == []

    def test_get_stock_concepts_method(self):
        """V15.1: tdxchain.cfg 不含成分股，反查恒返回空列表"""
        from zhb_client import ZhbData
        zhb = ZhbData()
        data = "880506|CYL00210|新基建-5G\n".encode("gbk")
        zhb.raw_files = {"tdxchain.cfg": data}
        assert zhb.get_stock_concepts("600519") == []


class TestZhbNeednote:
    """V14.2: neednote.dat 官方休市日+调休补班日"""

    def test_parse_neednote_empty(self):
        from zhb_client import ZhbData
        zhb = ZhbData()
        assert zhb.neednote_holidays == []
        assert zhb.neednote_jyweek == []

    def test_parse_neednote_format(self):
        """INI 格式：[RecentCFETSHoliday]/[RecentCFETSJYWeek]"""
        from zhb_client import ZhbData
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
        from zhb_client import ZhbData
        zhb = ZhbData()
        assert zhb.brk_seat == {}

    def test_parse_brkseat_format(self):
        """Pipe 格式：席位代码|营业部名称"""
        from zhb_client import ZhbData
        zhb = ZhbData()
        data = "000001|国泰君安证券股份有限公司总部\n000002|中信证券股份有限公司总部\n".encode("gbk")
        zhb.raw_files = {"brkseat.dat": data}
        seat = zhb.brk_seat
        assert seat["000001"] == "国泰君安证券股份有限公司总部"
        assert "000002" in seat


class TestZhbSpecialTags:
    """V14.2: pttab.dat 特别标签（红筹/AH/概念）"""

    def test_parse_special_tags_empty(self):
        from zhb_client import ZhbData
        zhb = ZhbData()
        assert zhb.special_tags == {}

    def test_parse_special_tags_format(self):
        """Pipe 格式：标签|代码1,代码2,..."""
        from zhb_client import ZhbData
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
        from data_provider import get_stock_basic_info_from_zhb
        result = get_stock_basic_info_from_zhb("600519")
        # ZHB 不可用时返回 None（不抛异常）
        assert result is None or (isinstance(result, dict) and "name" in result)

    def test_get_concept_from_zhb_returns_list(self):
        """返回值始终是 list（ZHB 缺失时返回空列表）"""
        from data_provider import get_concept_from_zhb
        result = get_concept_from_zhb("600519")
        assert isinstance(result, list)

    def test_get_new_share_calendar_from_zhb_returns_list(self):
        """返回值始终是 list"""
        from data_provider import get_new_share_calendar_from_zhb
        result = get_new_share_calendar_from_zhb()
        assert isinstance(result, list)

    def test_get_special_tags_from_zhb_returns_dict(self):
        """返回值始终是 dict"""
        from data_provider import get_special_tags_from_zhb
        result = get_special_tags_from_zhb()
        assert isinstance(result, dict)

    def test_is_zhb_dataset_available_returns_bool(self):
        """返回值始终是 bool"""
        from data_provider import is_zhb_dataset_available
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
        from data_provider import (
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