# -*- coding: utf-8 -*-
"""测试 easy_tdx 内置的所有 fallback hosts，看哪些K线正常"""
import sys
import struct

sys.path.insert(0, '.')

from easy_tdx import TdxClient, KlineCategory, Market
from easy_tdx.config import _FALLBACK_HOSTS, get_port

if __name__ == "__main__":
    port = get_port()
    print("=" * 70)
    print(" easy_tdx 内置服务器 K线可用性测试")
    print("=" * 70)
    print(f"  共 {len(_FALLBACK_HOSTS)} 个内置服务器，端口 {port}")
    print("  测试内容: get_security_bars(SH, 600519, DAY, 0, 3)")
    print("-" * 70)
    print(f"  {'#':<3} {'IP':<18} {'状态':<10} {'详情'}")
    print("-" * 70)

    ok_hosts = []
    bad_hosts = []

    for i, host in enumerate(_FALLBACK_HOSTS):
        try:
            client = TdxClient(host=host, port=port, timeout=3)
            client.connect()
            try:
                bars = client.get_security_bars(Market.SH, "600519", KlineCategory.DAY, 0, 3)
                cnt = len(bars)
                print(f"  {i+1:<3} {host:<18} ✅正常      {cnt}根K线")
                ok_hosts.append((host, port))
            except Exception as e:
                err_str = str(e)
                if "数据不足" in err_str:
                    print(f"  {i+1:<3} {host:<18} ❌假数据    ret_count=800但无数据")
                    bad_hosts.append((host, "假数据"))
                else:
                    print(f"  {i+1:<3} {host:<18} ❌其他      {err_str[:40]}")
                    bad_hosts.append((host, "其他错误"))
            client.close()
        except Exception as e:
            print(f"  {i+1:<3} {host:<18} ❌连不上    {str(e)[:40]}")
            bad_hosts.append((host, "连不上"))

    print("-" * 70)
    print(f"  结果: ✅正常 {len(ok_hosts)} 个 | ❌异常 {len(bad_hosts)} 个")
    if ok_hosts:
        print(f"  可用IP: {[h[0] for h in ok_hosts]}")

    print("\n" + "=" * 70)
    print(" 测试完成")
    print("=" * 70)
