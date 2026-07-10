"""
最终验证：
1. 追踪 _get_tdx_client() 失败的完整过程
2. 验证我们的假设：from_best_host 选到坏服务器 -> 健康检查失败 -> 标记坏主机 -> 重试 -> 又选到坏的 -> 耗尽重试次数
3. 用 _check_tdx 里的13个"经过验证"的IP来连接，看看能不能成功
"""
import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print(f"=== 最终验证 {datetime.now().strftime('%H:%M:%S')} ===")

# ============================================================
# 验证1：_get_tdx_client 失败的过程
# ============================================================
print(f"\n--- 验证1: 追踪 _get_tdx_client 失败过程 ---")

from tdx_client import (_get_tdx_client, _TDX_CLIENT, _TDX_AVAILABLE, 
                         _TDX_BAD_HOSTS, _TDX_RECONNECT_ATTEMPTS,
                         cleanup_tdx, _tdx_health_check)

# 重置状态
cleanup_tdx()
_TDX_BAD_HOSTS.clear()
print(f"初始状态: _TDX_AVAILABLE={_TDX_AVAILABLE}, _TDX_BAD_HOSTS={len(_TDX_BAD_HOSTS)}个")

# 手动模拟 _get_tdx_client 的流程
from easy_tdx import TdxClient
from easy_tdx.config import get_known_hosts
from tdx_client import _TDX_CALL_LOCK

_all_hosts = get_known_hosts()
print(f"总主机数: {len(_all_hosts)}")

for attempt in range(5):  # 多试几次看坏主机累积
    _good_hosts = [h for h in _all_hosts if h not in _TDX_BAD_HOSTS]
    print(f"\n第{attempt+1}次尝试: 可用主机 {len(_good_hosts)}/{len(_all_hosts)}, 坏主机 {len(_TDX_BAD_HOSTS)}个")
    
    if not _good_hosts:
        print(f"  所有主机都被标记为坏，重置黑名单")
        _TDX_BAD_HOSTS.clear()
        _good_hosts = _all_hosts
    
    try:
        client = TdxClient.from_best_host(hosts=_good_hosts, ping_timeout=2.0)
        print(f"  选中主机: {client._host}")
        client.connect()
        print(f"  连接成功")
        
        # 健康检查
        try:
            _tdx_health_check(client)
            print(f"  健康检查通过 ✅")
            client.close()
            break
        except RuntimeError as e:
            print(f"  健康检查失败 ❌: {e}")
            print(f"  标记 {client._host} 为坏主机")
            try:
                client.close()
            except Exception:
                pass
    except Exception as e:
        print(f"  连接失败: {type(e).__name__}: {e}")

print(f"\n最终坏主机数: {len(_TDX_BAD_HOSTS)}")
print(f"坏主机列表: {sorted(list(_TDX_BAD_HOSTS))[:10]}...")

# ============================================================
# 验证2：用 _check_tdx 里的13个"经过验证"的IP
# ============================================================
print(f"\n--- 验证2: 用 _check_tdx 里的13个IP ---")

# 从 _check_tdx 源码提取的IP
verified_ips = [
    '124.71.187.122', '123.60.73.44', '124.70.133.119', '124.71.187.72',
    '123.60.84.66', '101.35.121.35', '111.231.113.208',
    '111.230.186.52', '175.178.112.197', '175.178.128.227', '43.139.95.83',
    '129.204.230.128',
    '119.97.185.59',
]
print(f"验证过的13个IP:")
for ip in verified_ips:
    try:
        client = TdxClient(host=ip, port=7709)
        client.connect()
        
        # K线
        try:
            from easy_tdx import KlineCategory, Market
            bars = client.get_security_bars(Market.SH, "600519", KlineCategory.DAY, 0, 3)
            kline_ok = bars is not None and not bars.empty and len(bars) >= 2
        except Exception:
            kline_ok = False
        
        # 历史资金流
        try:
            df = client.get_history_fund_flow(1, "600519", 0, 30)
            hff_ok = df is not None and not df.empty and len(df) >= 20
            hff_count = len(df) if df is not None and not df.empty else 0
        except Exception:
            hff_ok = False
            hff_count = 0
        
        k_status = "✅K线" if kline_ok else "❌K线"
        f_status = f"✅FF({hff_count})" if hff_ok else "❌FF"
        print(f"  {ip:18s} {k_status} {f_status}")
        
        client.close()
    except Exception as e:
        print(f"  {ip:18s} ❌连接失败 ({type(e).__name__})")
    time.sleep(0.1)


print(f"\n=== 验证结束 ===")
