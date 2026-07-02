#!/usr/bin/env python3
"""TDX 数据接口诊断脚本 — 检查 tdx_client 各接口是否正常返回数据

用法:
    python tests/diag_tdx_data.py                    # 测试默认股票列表
    python tests/diag_tdx_data.py 600519 000858      # 测试指定股票
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
from datetime import datetime

# 测试股票（A股各板块代表）
DEFAULT_CODES = [
    "600519",  # 上证主板 — 贵州茅台
    "000858",  # 深证主板 — 五粮液
    "300750",  # 创业板   — 宁德时代
    "688981",  # 科创板   — 中芯国际
    "601016",  # 用户报错 — 节能风电
    "000551",  # 用户报错 — 创元科技
    "002409",  # 用户报错 — 雅克科技
]

# ============================================================
# 测试结果收集
# ============================================================
results = []
def test(name, ok, detail=""):
    status = "✅" if ok else "❌"
    results.append((status, name, detail))
    print(f"  {status} {name}: {detail}")

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

# ============================================================
# 测试 1: TDX 客户端连接
# ============================================================
section("一、TDX 客户端连接测试")

from tdx_client import _get_tdx_client, _TDX_AVAILABLE, cleanup_tdx

t0 = time.time()
client = _get_tdx_client()
t1 = time.time()
test("_get_tdx_client() 连接", client is not None,
     f"耗时 {t1-t0:.2f}s, client={'可用' if client else 'None'}")

if client is None:
    print("\n⚠️  TDX 客户端不可用，后续测试可能全部失败")
    print("    可能原因: 通达信服务器连接超时 / IP 被封 / 网络问题")
    print("    不影响 get_stock_info 的腾讯行情部分(名称/价格/市值)")
    print("    影响: 财务数据(ROE/现金流/ipo_date)、资金流、K线数据\n")

# ============================================================
# 测试 2: get_finance_info — 核心数据字段检查
# ============================================================
section("二、get_finance_info 字段完整性测试")

from tdx_client import _market_from_code as _mkt

FINANCE_FIELDS_EXPECTED = [
    "ipo_date",           # 上市日期 — 当前问题
    "zong_guben",         # 总股本
    "liutong_guben",      # 流通股本
    "jingying_xianjinliu",# 经营现金流
    "jing_lirun",         # 净利润
    "gudong_renshu",      # 股东人数
    "updated_date",       # 更新日期
]

for code in DEFAULT_CODES[:4]:  # 每个板块测一只
    print(f"\n  --- {code} ---")
    if client is None:
        test(f"get_finance_info({code})", False, "TDX 客户端不可用，跳过")
        continue
    try:
        info = client.get_finance_info(_mkt(code), code) if client else None
        if info is None or info.empty:
            test(f"get_finance_info({code})", False, "返回 None 或空 DataFrame")
            continue
        
        cols = list(info.columns)
        test(f"get_finance_info({code}) 有数据", True, f"返回 {len(info)} 行, {len(cols)} 列")
        
        # 逐字段检查
        for field in FINANCE_FIELDS_EXPECTED:
            if field in cols:
                val = info.iloc[0].get(field, None)
                is_valid = val is not None and val != 0 and str(val) != '0'
                if field == "ipo_date":
                    detail = f"ipo_date={val} ({'有效' if is_valid else '为空/0'})"
                elif field == "jingying_xianjinliu":
                    detail = f"经营现金流={val} ({'有效' if is_valid else '为空/0'})"
                else:
                    detail = f"{field}={val}"
                test(f"  {field}", is_valid, detail)
            else:
                test(f"  {field}", False, "字段不存在于 DataFrame")
    except Exception as e:
        test(f"get_finance_info({code})", False, f"异常: {e}")

# ============================================================
# 测试 3: get_stock_info — 上市日期
# ============================================================
section("三、get_stock_info 上市日期测试")

from stock_common import get_stock_info

for code in DEFAULT_CODES:
    info = get_stock_info(code)
    name = info.get("name", "N/A")
    list_date = info.get("list_date", "")
    has_date = len(list_date) >= 8
    source = "(缓存)" if has_date else "(TDX失败或空)"
    test(f"get_stock_info({code}) {name}", has_date,
         f"list_date={repr(list_date)} {source}")

# ============================================================
# 测试 4: 替代方案 — 腾讯行情是否有 list_date
# ============================================================
section("四、腾讯行情是否有上市日期替代来源")

from stock_common import get_tencent_quote

for code in DEFAULT_CODES[:3]:
    q = get_tencent_quote(code)
    if q:
        # 腾讯行情返回的字段中排查是否有上市相关字段
        date_fields = [k for k in q.keys() if 'date' in k.lower() or 'list' in k.lower() or 'ipo' in k.lower()]
        test(f"腾讯行情({code})", len(date_fields) > 0,
             f"查到 {len(date_fields)} 个日期字段: {date_fields[:3]}" if date_fields else "无日期相关字段")
    else:
        test(f"腾讯行情({code})", False, "返回 None")

# ============================================================
# 测试 5: tdx_get_quote_full — 另一个可能的上市日期来源
# ============================================================
section("五、tdx_get_quote_full 字段检查")

from tdx_client import tdx_get_quote_full

if client:
    for code in DEFAULT_CODES[:3]:
        try:
            qf = tdx_get_quote_full(code)
            if qf:
                # 检查是否有日期相关字段
                date_keys = [k for k in qf.keys() if any(x in k.lower() for x in ['date','list','ipo','time','day'])]
                test(f"tdx_get_quote_full({code})", bool(date_keys),
                     f"日期字段: {date_keys[:5]}" if date_keys else "无日期相关字段")
            else:
                test(f"tdx_get_quote_full({code})", False, "返回空")
        except Exception as e:
            test(f"tdx_get_quote_full({code})", False, f"异常: {e}")
else:
    print("  ⏭  TDX 客户端不可用，跳过")

# ============================================================
# 测试 6: 数据缓存是否过期 — basic_info 缓存检查
# ============================================================
section("六、basic_info 缓存状态检查")

from stock_cache import cache_stats

stats = cache_stats()
basic_info = stats.get("by_category", {}).get("basic_info", {})
test("basic_info 缓存条目", basic_info.get("count", 0) > 0,
     f"{basic_info.get('count', 0)} 条, {basic_info.get('hits', 0)} 次命中")

# ============================================================
# 汇总
# ============================================================
section("诊断汇总")
passed = sum(1 for s, _, _ in results if s == "✅")
failed = sum(1 for s, _, _ in results if s == "❌")
print(f"  通过: {passed}  |  失败: {failed}  |  共计: {len(results)}")
print()

# 输出有问题的项
if failed > 0:
    print("  ❌ 失败项清单:")
    for s, name, detail in results:
        if s == "❌":
            print(f"    {name}: {detail}")

print(f"\n  诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
cleanup_tdx()
