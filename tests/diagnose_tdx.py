# -*- coding: utf-8 -*-
"""TDX 连接诊断脚本 — 区分『连接抖动』还是『被服务器拉黑』"""
import sys
import time
import traceback

print("=" * 70)
print(" TDX 连接诊断 — 开始测试")
print("=" * 70)

# 测试 1: 检查 easy_tdx 是否可用
try:
    from easy_tdx import TdxClient, MacClient
    print("\n[1/5] ✅ easy_tdx 模块已安装")
except ImportError as e:
    print(f"\n[1/5] ❌ easy_tdx 未安装: {e}")
    sys.exit(1)

# 测试 2: TdxClient 首次连接（检查是否能建立TCP连接）
print("\n[2/5] TdxClient 连接测试...")
client = None
try:
    client = TdxClient()
    t0 = time.time()
    client.connect()
    dt = time.time() - t0
    print(f"  ✅ 连接成功（耗时 {dt:.2f}s）")

    # 做一次简单请求测试
    try:
        quotes = client.get_security_quotes([(1, "600519")])
        if quotes and len(quotes) > 0:
            q = quotes[0]
            print(f"  ✅ 行情查询成功: 600519 价格={q.price}")
        else:
            print(f"  ⚠️  行情查询返回空")
    except Exception as e:
        print(f"  ❌ 行情查询失败: {type(e).__name__}: {e}")

    # 测试 K 线
    try:
        from easy_tdx import KlineCategory
        bars = client.get_security_bars(1, "600519", KlineCategory.DAY, 0, 5)
        bar_count = len(bars) if bars and not hasattr(bars, 'empty') else (len(bars) if not hasattr(bars, 'empty') else 0)
        if hasattr(bars, 'empty'):
            bar_count = 0 if bars.empty else len(bars)
        print(f"  ✅ K线查询成功: {bar_count} 根")
    except Exception as e:
        print(f"  ❌ K线查询失败: {type(e).__name__}: {e}")

    client.close()
    print("  ✅ 正常断开")

except Exception as e:
    print(f"  ❌ 连接失败: {type(e).__name__}: {e}")
    print(f"     异常详情: {traceback.format_exc().strip().split(chr(10))[0]}")
    if "10061" in str(e) or "WSAECONNREFUSED" in str(e) or "refused" in str(e).lower():
        print(f"  👉 诊断: 连接被拒绝 — 可能是 IP 被拉黑或服务器暂时不可用")
    elif "10060" in str(e) or "timed out" in str(e).lower():
        print(f"  👉 诊断: 连接超时 — 网络问题或服务器无响应")
    elif "10053" in str(e) or "Software caused connection abort" in str(e):
        print(f"  👉 诊断: 软件导致连接中止 — 对端主动关闭，可能是频率限制")
    else:
        print(f"  👉 诊断: 未知错误，请查看上方异常")

# 测试 3: MacClient 连接（全市场行情用这个）
print("\n[3/5] MacClient 连接测试...")
mac_client = None
try:
    mac_client = MacClient.from_best_host()
    t0 = time.time()
    mac_client.connect()
    dt = time.time() - t0
    print(f"  ✅ 连接成功（耗时 {dt:.2f}s）")

    # 测试获取股票列表
    try:
        from easy_tdx.mac.enums import Category
        df = mac_client.get_stock_quotes_list(Category.A, 0, 5)
        if df is not None and not df.empty:
            print(f"  ✅ 全市场列表查询成功: 第1页 {len(df)} 条")
            for _, row in df.head(3).iterrows():
                print(f"     - {row.get('code', '')} {row.get('name', '')} 价格={row.get('close', '')}")
        else:
            print(f"  ⚠️  全市场列表查询返回空")
    except Exception as e:
        print(f"  ❌ 全市场列表查询失败: {type(e).__name__}: {e}")

    mac_client.close()
    print("  ✅ 正常断开")

except Exception as e:
    print(f"  ❌ 连接失败: {type(e).__name__}: {e}")

# 测试 4: 使用 tdx_client.py 的公共函数（带自动重连）
print("\n[4/5] tdx_client.py 公共函数测试...")
sys.path.insert(0, '.')
from tdx_client import (
    _get_tdx_client, _get_mac_client, _check_tdx,
    tdx_get_security_bars, tdx_get_quote_full, tdx_get_all_stocks,
    cleanup_tdx
)

print(f"  _check_tdx() = {_check_tdx()}")

client4 = _get_tdx_client()
print(f"  _get_tdx_client() = {'✅ 成功' if client4 else '❌ 失败'}")

mac_client4 = _get_mac_client()
print(f"  _get_mac_client() = {'✅ 成功' if mac_client4 else '❌ 失败'}")

# 测试行情
try:
    q = tdx_get_quote_full("600519")
    if q and q.get('price'):
        print(f"  ✅ tdx_get_quote_full('600519'): 价格={q.get('price')}, 涨跌={q.get('change_pct')}%")
    else:
        print(f"  ⚠️  tdx_get_quote_full('600519'): 返回空")
except Exception as e:
    print(f"  ❌ tdx_get_quote_full 失败: {e}")

# 测试 K 线
try:
    keys, rows = tdx_get_security_bars("600519", count=5)
    print(f"  ✅ tdx_get_security_bars('600519'): {len(rows)} 根K线 (数据源={'百度fallback' if not keys else 'TDX'})")
except Exception as e:
    print(f"  ❌ tdx_get_security_bars 失败: {e}")

# 测试全市场（简短版本，只看前 2 页）
print("  tdx_get_all_stocks() 测试...")
t0 = time.time()
all_stocks = tdx_get_all_stocks()
dt = time.time() - t0
if all_stocks:
    print(f"  ✅ tdx_get_all_stocks(): {len(all_stocks)} 只股票 (耗时 {dt:.1f}s)")
    print(f"     样例: {all_stocks[0]}")
else:
    print(f"  ❌ tdx_get_all_stocks(): 空列表！")

cleanup_tdx()

# 测试 5: 连续请求压力测试（模拟脚本中的高频调用）
print("\n[5/5] 压力测试 — 连续 20 次 K 线查询，观察是否被踢下线...")
from tdx_client import tdx_get_security_bars, _get_tdx_client

success = 0
fails = 0
test_codes = ["600519", "000001", "600036", "000858", "601318"]

t0 = time.time()
for i in range(20):
    code = test_codes[i % len(test_codes)]
    try:
        keys, rows = tdx_get_security_bars(code, count=10)
        if rows:
            success += 1
        else:
            fails += 1
            print(f"     [{i+1}/20] {code}: ⚠️  返回空")
    except Exception as e:
        fails += 1
        print(f"     [{i+1}/20] {code}: ❌ {type(e).__name__}")

dt = time.time() - t0
print(f"  结果: 成功 {success}/20, 失败 {fails}/20, 总耗时 {dt:.1f}s")

if success == 20 and fails == 0:
    print("  ✅ 压力测试通过 — TDX 服务器未拒绝请求")
elif success > 15 and fails < 5:
    print("  ⚠️  少量失败 — 可能是偶发网络抖动")
elif fails > 10:
    print("  ❌ 大量失败 — 可能被 TDX 服务器频率限制或 IP 被临时拉黑")

cleanup_tdx()

print("\n" + "=" * 70)
print(" 诊断结论")
print("=" * 70)

# 总结判断
check_ok = _check_tdx()
if check_ok:
    print("  ✅ TDX 服务整体可用 — 不是『被拉黑』")
    print("     之前的异常更可能是：")
    print("     1. 网络连接抖动（TCP心跳超时）")
    print("     2. 长连接空闲时间过长被服务器主动清理")
    print("     3. 高频请求触发服务器临时限流（几秒后自动恢复）")
    print("")
    print("  💡 我们新增的自动重连机制应该能覆盖这些情况")
else:
    print("  ❌ TDX _check_tdx() 返回 False — 可能被拉黑")
    print("     尝试: 切换网络 / 等待几分钟 / 检查通达信官方行情是否可用")

print()
print(" 如果以上测试全部通过，之前的连接异常就是偶发抖动，")
print(" 新的自动重连机制会在下次运行中默默修复，不需要额外操作。")
print()
