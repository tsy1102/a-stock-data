# -*- coding: utf-8 -*-
"""捕获 TDX 响应的 header 和 body，确认解码错误的根因"""
import sys
import struct

sys.path.insert(0, '.')

from easy_tdx import TdxClient, KlineCategory, Market
from easy_tdx.transport.sync import TdxConnection

if __name__ == "__main__":
    # monkey-patch TdxConnection.execute
    original_conn_execute = TdxConnection.execute

    def patched_conn_execute(self, cmd):
        from easy_tdx.codec.frame import HEADER_SIZE, parse_header, decompress_body
        
        with self._lock:
            import time
            self._last_active = time.monotonic()
            self._consecutive_heartbeats = 0
            if self._sock is None:
                raise RuntimeError("未连接")
            request = cmd.build_request()
            self._sock.sendall(request)
            
            header_buf = self._recv_exact(HEADER_SIZE)
            header = parse_header(header_buf)
            
            print(f"\n  [响应详情] {type(cmd).__name__}")
            print(f"    header: {header}")
            print(f"    header.zipsize = {header.zipsize}")
            print(f"    header.length  = {getattr(header, 'length', '?')}")
            
            raw_body = self._recv_exact(header.zipsize)
            print(f"    raw_body 长度: {len(raw_body)} 字节")
            print(f"    raw_body 前20字节(hex): {raw_body[:20].hex() if len(raw_body) >= 20 else raw_body.hex()}")
            
            body = decompress_body(header, raw_body)
            print(f"    解压后 body 长度: {len(body)} 字节")
            print(f"    body 前20字节(hex): {body[:20].hex() if len(body) >= 20 else body.hex()}")
            
            if len(body) >= 2:
                ret_count = struct.unpack_from("<H", body, 0)[0]
                print(f"    ret_count = {ret_count}")
                actual_data = body[2:]
                print(f"    实际数据长度: {len(actual_data)} 字节")
                if ret_count > 0:
                    expected_min = ret_count * 8  # 日期4字节 + 至少4字节价格
                    print(f"    预期至少 {expected_min} 字节（{ret_count}条 × 最小8字节/条）")
                    if len(actual_data) < 4:
                        print(f"    ⚠️  严重不匹配！ret_count={ret_count} 但数据只有 {len(actual_data)} 字节")
            
            return cmd.parse_response(body)

    TdxConnection.execute = patched_conn_execute

    print("=" * 70)
    print(" TDX K线解码错误 — 最终根因定位")
    print("=" * 70)

    # 测试
    client = TdxClient()
    print("\n[1/3] 连接...")
    client.connect()

    print("\n[2/3] 调用 get_security_bars (日线)...")
    try:
        bars = client.get_security_bars(Market.SH, "600519", KlineCategory.DAY, 0, 5)
        print(f"\n  ✅ 成功: {len(bars)} 根")
    except Exception as e:
        print(f"\n  ❌ 失败: {type(e).__name__}: {e}")

    print("\n[3/3] 调用 get_index_bars (指数日线)...")
    try:
        idx_bars = client.get_index_bars(Market.SH, "000001", KlineCategory.DAY, 0, 5)
        print(f"\n  ✅ 成功: {len(idx_bars)} 根")
    except Exception as e:
        print(f"\n  ❌ 失败: {type(e).__name__}: {e}")

    client.close()

    # 恢复
    TdxConnection.execute = original_conn_execute

    print("\n" + "=" * 70)
    print(" 诊断完成")
    print("=" * 70)
