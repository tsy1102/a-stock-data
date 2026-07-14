#!/usr/bin/env python3
"""diag_zhb.py — zhb 全局配置总包功能验证脚本。

验证内容:
    1. zhb_client 下载与解析
    2. spblock 大板块成分（中证2000等突破400只限制）
    3. 申万行业分类（467个四级分类）
    4. 行业代码映射
    5. 缓存机制（内存+文件）
    6. sc_datasource 集成接口
    7. tdxstat 全市场统计快照（阶段二-2.1）
    8. tdxstat2 资金流向+板块归属（阶段二-2.2）
    9. 数据新鲜度检查（阶段二-2.6 降级策略）
    10. tipinfo 财报日历（阶段三-3.1）
    11. 新股申购日历（阶段三-3.2）
    12. A+H股 + 券商名称表（阶段三-3.3/3.4）
    13. 节假日数据（V10.0）
    14. 证监会行业分类（V10.0）
    15. 中概股ADR/可转债/退市股（V10.0）
    16. V10.0 sc_datasource导出接口验证

版本信息:
    V10.0  2026-07-14 - 新增节假日/证监会行业/ADR/可转债/退市股测试

使用方法:
    python tests/diag_zhb.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_1_zhb_client_download():
    """测试1: zhb_client 下载与解析"""
    print("\n" + "=" * 60)
    print("测试 1: zhb_client 下载与解析")
    print("=" * 60)

    try:
        from zhb_client import get_zhb, invalidate_cache

        # 清缓存确保走下载/文件路径
        invalidate_cache()

        zhb = get_zhb()
        if zhb is None:
            print("❌ 获取失败")
            return False

        print(f"✅ 数据日期: {zhb.date}")
        print(f"✅ 原始文件数: {len(zhb.raw_files)}")

        # 检查关键文件是否存在
        key_files = [
            "spblock.dat", "tdxzs3.cfg", "tdxzs.cfg",
            "tdxbk.cfg", "tdxstat.cfg", "tdxstat2.cfg",
            "needini.dat", "incon.dat", "tipinfo.dat",
        ]
        found = [f for f in key_files if f in zhb.raw_files]
        missing = [f for f in key_files if f not in zhb.raw_files]
        print(f"✅ 关键文件: {len(found)}/{len(key_files)} 个存在")
        if missing:
            print(f"⚠️  缺失文件: {missing}")

        return True
    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_2_spblock():
    """测试2: spblock 大板块成分"""
    print("\n" + "=" * 60)
    print("测试 2: spblock 大板块成分")
    print("=" * 60)

    try:
        from zhb_client import list_sp_blocks, get_sp_block

        blocks = list_sp_blocks()
        print(f"✅ 大板块总数: {len(blocks)}")
        print()

        # 重点验证几个关键板块
        key_blocks = ["中证2000", "中证1000", "中证500", "融资融券", "沪深港通", "专精特新"]
        for name in key_blocks:
            codes = get_sp_block(name)
            if codes:
                print(f"  {name:15s}: {len(codes):5d} 只  [前3只: {', '.join(codes[:3])}]")
            else:
                print(f"  {name:15s}: 未找到")

        print()

        # 验证突破 400 只限制
        big_blocks = [(n, c) for n, c in blocks if c > 400]
        print(f"✅ 成分股 > 400 的板块数: {len(big_blocks)}")
        for name, count in big_blocks[:10]:
            print(f"    {name:20s}  {count:5d} 只")

        return True
    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_3_sw_industries():
    """测试3: 申万行业分类"""
    print("\n" + "=" * 60)
    print("测试 3: 申万行业分类")
    print("=" * 60)

    try:
        from zhb_client import get_sw_industries

        sw = get_sw_industries()
        print(f"✅ 申万行业总数: {len(sw)}")

        # 按代码前缀分类（一级行业）
        level1 = set()
        for code in sw:
            if len(code) >= 6:
                level1.add(code[:6])  # 881001 是一级

        print(f"✅ 一级行业数量 (881xxx): {len([c for c in sw if len(c)==6])}")
        print(f"✅ 二级行业数量 (881xxx 4位): {len([c for c in sw if len(c)==7])}")
        print(f"✅ 三级行业数量 (881xxx 6位): {len([c for c in sw if len(c)==8])}")

        print()
        print("煤炭行业四级分类示例:")
        coal = [(c, n) for c, n in sw.items() if n.startswith("煤") or n.startswith("焦炭")]
        for code, name in sorted(coal)[:10]:
            print(f"  {code}  {name}")

        return True
    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_4_industry_map():
    """测试4: 行业代码映射"""
    print("\n" + "=" * 60)
    print("测试 4: 行业代码→名称映射")
    print("=" * 60)

    try:
        from zhb_client import get_industry_map

        ind_map = get_industry_map()
        print(f"✅ 映射总数: {len(ind_map)}")

        # 测试几个已知代码
        test_codes = ["880826", "880365", "880471", "880001"]
        for code in test_codes:
            name = ind_map.get(code, "未知")
            print(f"  {code} → {name}")

        return True
    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_5_cache():
    """测试5: 缓存机制"""
    print("\n" + "=" * 60)
    print("测试 5: 缓存机制")
    print("=" * 60)

    try:
        import time
        from zhb_client import get_zhb, invalidate_cache, _ZHB_CACHE_DIR

        # 第一次调用
        t0 = time.time()
        zhb1 = get_zhb()
        t1 = time.time()
        print(f"✅ 首次调用: {(t1-t0)*1000:.1f} ms")

        # 第二次调用（应走内存缓存）
        t0 = time.time()
        zhb2 = get_zhb()
        t1 = time.time()
        print(f"✅ 二次调用(内存缓存): {(t1-t0)*1000:.1f} ms")

        # 验证是同一个对象
        if zhb1 is zhb2:
            print("✅ 内存缓存生效（同一对象）")
        else:
            print("⚠️  内存缓存未生效（不同对象）")

        # 检查文件缓存
        import os
        if os.path.exists(_ZHB_CACHE_DIR):
            files = [f for f in os.listdir(_ZHB_CACHE_DIR) if f.endswith(".zip")]
            print(f"✅ 文件缓存: {len(files)} 个 zip 文件")
            for f in sorted(files)[-5:]:
                size = os.path.getsize(os.path.join(_ZHB_CACHE_DIR, f))
                print(f"    {f}  ({size/1024:.1f} KB)")

        return True
    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_6_sc_datasource():
    """测试6: sc_datasource 集成接口"""
    print("\n" + "=" * 60)
    print("测试 6: sc_datasource 集成接口")
    print("=" * 60)

    try:
        from stock_common.sc_datasource import (
            get_zhb_sp_block,
            get_zhb_sp_block_list,
            get_zhb_sw_industries,
            get_zhb_industry_map,
            get_zhb_data_date,
        )

        # 大板块列表
        blocks = get_zhb_sp_block_list()
        print(f"✅ get_zhb_sp_block_list(): {len(blocks)} 个板块")

        # 中证2000
        zz2000 = get_zhb_sp_block("中证2000")
        print(f"✅ get_zhb_sp_block('中证2000'): {len(zz2000)} 只")

        # 申万行业
        sw = get_zhb_sw_industries()
        print(f"✅ get_zhb_sw_industries(): {len(sw)} 个行业")

        # 行业映射
        ind_map = get_zhb_industry_map()
        print(f"✅ get_zhb_industry_map(): {len(ind_map)} 条映射")

        # 数据日期
        date = get_zhb_data_date()
        print(f"✅ get_zhb_data_date(): {date}")

        return True
    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_7_tdxstat():
    """测试7: tdxstat 全市场统计快照（阶段二）"""
    print("\n" + "=" * 60)
    print("测试 7: tdxstat 全市场统计快照（阶段二-2.1）")
    print("=" * 60)

    try:
        from zhb_client import market_stat_snapshot, get_stock_stat

        snapshot = market_stat_snapshot()
        print(f"✅ 全市场快照: {len(snapshot)} 只股票")

        # 抽样验证字段完整性
        sample_codes = ["000001", "600519", "000858", "300750"]
        for code in sample_codes:
            stat = get_stock_stat(code)
            if stat:
                print(f"  {code}: 涨跌幅={stat.get('change_pct')}% "
                      f"PE_TTM={stat.get('pe_ttm')} "
                      f"5日={stat.get('change_5d')}% "
                      f"20日={stat.get('change_20d')}%")
            else:
                print(f"  {code}: 未找到")

        # 验证字段分布
        has_pe = sum(1 for s in snapshot.values() if s.get("pe_ttm") is not None)
        has_change = sum(1 for s in snapshot.values() if s.get("change_pct") is not None)
        print(f"✅ PE_TTM 覆盖率: {has_pe}/{len(snapshot)}")
        print(f"✅ 涨跌幅 覆盖率: {has_change}/{len(snapshot)}")

        return True
    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_8_tdxstat2():
    """测试8: tdxstat2 资金流向+板块归属（阶段二）"""
    print("\n" + "=" * 60)
    print("测试 8: tdxstat2 资金流向+板块归属（阶段二-2.2）")
    print("=" * 60)

    try:
        from zhb_client import get_stock_stat2, get_high_52w, get_low_52w, get_industry_code

        sample_codes = ["000001", "600519", "000858", "300750"]
        for code in sample_codes:
            s2 = get_stock_stat2(code)
            if s2:
                high52 = get_high_52w(code)
                low52 = get_low_52w(code)
                ind = get_industry_code(code)
                print(f"  {code}: 行业={ind} "
                      f"52周高={high52} 52周低={low52} "
                      f"主力流入={s2.get('main_inflow')}")
            else:
                print(f"  {code}: 未找到")

        return True
    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_9_freshness():
    """测试9: 数据新鲜度检查（阶段二-2.6 降级策略）"""
    print("\n" + "=" * 60)
    print("测试 9: 数据新鲜度检查（阶段二-2.6）")
    print("=" * 60)

    try:
        from zhb_client import get_zhb, is_data_fresh
        from stock_common.sc_datasource import is_zhb_data_fresh, get_zhb_data_date

        zhb = get_zhb()
        if zhb is None:
            print("❌ zhb 不可用")
            return False

        print(f"✅ 数据日期: {zhb.date}")
        print(f"✅ is_data_fresh(3): {is_data_fresh(3)}")
        print(f"✅ is_data_fresh(30): {is_data_fresh(30)}")

        # 通过 sc_datasource 调用
        print(f"✅ is_zhb_data_fresh(3): {is_zhb_data_fresh(3)}")
        print(f"✅ get_zhb_data_date(): {get_zhb_data_date()}")

        return True
    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_10_tipinfo():
    """测试10: tipinfo 财报日历（阶段三-3.1）"""
    print("\n" + "=" * 60)
    print("测试 10: tipinfo 财报日历（阶段三-3.1）")
    print("=" * 60)

    try:
        from zhb_client import get_tip_info, get_zhb

        zhb = get_zhb()
        if zhb is None:
            print("❌ zhb 不可用")
            return False

        tip_count = len(zhb.tip_info)
        print(f"✅ 财报日历总数: {tip_count}")

        # 抽样
        sample_codes = ["000001", "600519", "000858"]
        for code in sample_codes:
            tip = get_tip_info(code)
            if tip:
                print(f"  {code}: 财报期={tip.get('report_period')} "
                      f"EPS={tip.get('eps')} "
                      f"披露日={tip.get('disclose_date')}")
            else:
                print(f"  {code}: 无财报日历")

        return True
    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_11_ipo():
    """测试11: 新股申购日历（阶段三-3.2）"""
    print("\n" + "=" * 60)
    print("测试 11: 新股申购日历（阶段三-3.2）")
    print("=" * 60)

    try:
        from zhb_client import get_ipo_list

        ipo_list = get_ipo_list()
        print(f"✅ 新股申购日历: {len(ipo_list)} 条")

        for item in ipo_list[:5]:
            print(f"  {item.get('code', '')} {item.get('name', '')} "
                  f"日期={item.get('date')} 发行价={item.get('issue_price')}")

        return True
    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_12_ah_brokers():
    """测试12: A+H股 + 券商名称表（阶段三-3.3/3.4）"""
    print("\n" + "=" * 60)
    print("测试 12: A+H股 + 券商名称表（阶段三-3.3/3.4）")
    print("=" * 60)

    try:
        from zhb_client import get_ah_stocks, get_broker_name, get_zhb

        ah = get_ah_stocks()
        print(f"✅ A+H股: {len(ah)} 只")
        for item in ah[:3]:
            print(f"  {item}")

        # 券商名称表
        zhb = get_zhb()
        broker_count = len(zhb.brokers) if zhb else 0
        print(f"✅ 券商名称表: {broker_count} 家")

        # 测试几个已知券商ID
        test_ids = ["1", "2", "3", "10", "100"]
        for bid in test_ids:
            name = get_broker_name(bid)
            print(f"  券商ID {bid}: {name}")

        return True
    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_13_holidays():
    """测试13: 节假日数据（V10.0）"""
    print("\n" + "=" * 60)
    print("测试 13: 节假日数据（V10.0）")
    print("=" * 60)

    try:
        from zhb_client import get_holidays

        holidays = get_holidays()
        print(f"✅ 节假日总数: {len(holidays)}")
        print(f"✅ 时间范围: {holidays[0] if holidays else '无'} ~ {holidays[-1] if holidays else '无'}")

        # 验证包含2025年后的数据
        future = [h for h in holidays if int(h[:4]) >= 2025]
        print(f"✅ 2025年后节假日: {len(future)} 条")

        return True
    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_14_csrc_industries():
    """测试14: 证监会行业分类（V10.0）"""
    print("\n" + "=" * 60)
    print("测试 14: 证监会行业分类（V10.0）")
    print("=" * 60)

    try:
        from zhb_client import get_csrc_industries

        csrc = get_csrc_industries()
        print(f"✅ 证监会行业总数: {len(csrc)}")

        # 按门类统计
        categories = {}
        for code in csrc:
            cat = code[0] if code else "?"
            categories[cat] = categories.get(cat, 0) + 1

        print("✅ 门类分布:")
        for cat in sorted(categories.keys())[:10]:
            print(f"  {cat}: {categories[cat]} 个行业")

        return True
    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_15_adr_bonds_delisted():
    """测试15: 中概股ADR/可转债/退市股（V10.0）"""
    print("\n" + "=" * 60)
    print("测试 15: 中概股ADR/可转债/退市股（V10.0）")
    print("=" * 60)

    try:
        from zhb_client import get_adr_stocks, get_convertible_bonds, get_delisted_stocks

        adr = get_adr_stocks()
        print(f"✅ 中概股ADR: {len(adr)} 只")
        for item in adr[:3]:
            print(f"  {item.get('a_code')} {item.get('a_name')} → {item.get('adr_code')}")

        bonds = get_convertible_bonds()
        print(f"✅ 可转债: {len(bonds)} 只")

        delisted = get_delisted_stocks()
        print(f"✅ 退市股票对照表: {len(delisted)} 只")

        return True
    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_16_v10_exports():
    """测试16: V10.0 sc_datasource 导出接口"""
    print("\n" + "=" * 60)
    print("测试 16: V10.0 sc_datasource 导出接口")
    print("=" * 60)

    try:
        from stock_common import (
            get_zhb_holidays, get_zhb_csrc_industries, get_zhb_adr_stocks,
            get_zhb_convertible_bonds, get_zhb_delisted_stocks,
        )

        holidays = get_zhb_holidays()
        print(f"✅ get_zhb_holidays(): {len(holidays)} 条")

        csrc = get_zhb_csrc_industries()
        print(f"✅ get_zhb_csrc_industries(): {len(csrc)} 个行业")

        adr = get_zhb_adr_stocks()
        print(f"✅ get_zhb_adr_stocks(): {len(adr)} 只")

        bonds = get_zhb_convertible_bonds()
        print(f"✅ get_zhb_convertible_bonds(): {len(bonds)} 只")

        delisted = get_zhb_delisted_stocks()
        print(f"✅ get_zhb_delisted_stocks(): {len(delisted)} 只")

        return True
    except Exception as e:
        print(f"❌ 异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("╔" + "═" * 58 + "╗")
    print("║           zhb 全局配置总包功能验证脚本                 ║")
    print("╚" + "═" * 58 + "╝")

    results = []

    tests = [
        ("zhb_client 下载与解析", test_1_zhb_client_download),
        ("spblock 大板块成分", test_2_spblock),
        ("申万行业分类", test_3_sw_industries),
        ("行业代码映射", test_4_industry_map),
        ("缓存机制", test_5_cache),
        ("sc_datasource 集成", test_6_sc_datasource),
        ("tdxstat 全市场统计快照", test_7_tdxstat),
        ("tdxstat2 资金流向+板块归属", test_8_tdxstat2),
        ("数据新鲜度检查", test_9_freshness),
        ("tipinfo 财报日历", test_10_tipinfo),
        ("新股申购日历", test_11_ipo),
        ("A+H股 + 券商名称表", test_12_ah_brokers),
        ("节假日数据", test_13_holidays),
        ("证监会行业分类", test_14_csrc_industries),
        ("中概股ADR/可转债/退市股", test_15_adr_bonds_delisted),
        ("V10.0 sc_datasource导出", test_16_v10_exports),
    ]

    for name, func in tests:
        ok = func()
        results.append((name, ok))

    # 汇总
    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    for name, ok in results:
        status = "✅ 通过" if ok else "❌ 失败"
        print(f"  {status}  {name}")

    print()
    print(f"总计: {passed}/{total} 通过")

    if passed == total:
        print("\n🎉 全部测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
