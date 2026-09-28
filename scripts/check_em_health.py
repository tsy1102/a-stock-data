"""东财接口健康探测（低频，防封锁）。

用法:
    python scripts/check_em_health.py          # 全量 6 域探测（间隔 5s，~35s）
    python scripts/check_em_health.py --once   # 只测 1 个域（push2 主域，验证恢复用）

退出码: 0=全部 OK / 1=有 FAIL。
注意: 不要高频运行（东财 IP 风控），建议每天最多 1-2 次；失败项会自动跳过等待（20h+ 自然恢复）。
"""

import os
import sys
import time
from typing import Any

for _s in (sys.stdout, sys.stderr):
    if _s is not None and hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

import requests
from urllib.parse import urlparse

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"


def _throttled_get(url: str, timeout: int = 10):
    """V17.3.17: 复用 sc_network._quick_request（分域限流 + 跨进程封禁跳过 + 全局 1.0-1.3s 节奏）。

    原实现用裸 requests.get 直打 push2 全族，既无节流也无封禁感知——
    在已封禁状态下仍狂轰会恶化 IP 级封禁。现统一走项目限流通道。
    """
    try:
        import sys as _sys

        _sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from stock_common.sc_network import (
            _quick_request as _quick_request_impl,
            _em_is_banned,
            _normalize_em_domain,
        )

        _quick_request: Any = _quick_request_impl
    except Exception:
        _quick_request = None
    if _quick_request is None:
        # 兜底：仍至少尊重封禁态，避免裸轰
        return requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"},
            verify=True,
        )
    _ft = _normalize_em_domain(urlparse(url).netloc)
    if _em_is_banned(_ft):
        return None  # 已封禁 → 跳过，不浪费请求也不加重封禁
    return _quick_request(
        url, timeout=timeout, headers={"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"}
    )


PROBES = [
    (
        "push2",
        "https://push2.eastmoney.com/api/qt/stock/get?secid=1.600519&fields=f43,f57,f58,f167",
    ),
    (
        "83.push2",
        "https://83.push2.eastmoney.com/api/qt/clist/get?pn=1&pz=5&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:1+t:2&fields=f12,f14,f2,f3",
    ),
    (
        "push2delay",
        "https://push2delay.eastmoney.com/api/qt/stock/get?secid=1.600519&fields=f43,f57,f58,f167",
    ),
    (
        "push2his",
        "https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.600519&fields1=f1,f2,f3&fields2=f51,f52,f53&klt=101&fqt=1&beg=20260801&end=20260811",
    ),
    (
        "push2ex",
        "https://push2ex.eastmoney.com/getTopicZTPool?ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt&Pageindex=0&pagesize=1&sort=fbt:asc&date=20260811",
    ),
    (
        "datacenter-web",
        "https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_MUTUAL_DEAL_HISTORY&columns=ALL&pageNumber=1&pageSize=1",
    ),
]

ONLY_FIRST = "--once" in sys.argv


def probe(name: str, url: str) -> str:
    try:
        r = _throttled_get(url, timeout=10)
        if r is None:
            return "SKIP(banned)"
        if r.status_code == 200:
            return "OK"
        return f"HTTP{r.status_code}"
    except Exception as e:
        return f"FAIL {type(e).__name__}"


def main() -> int:
    probes = PROBES[:1] if ONLY_FIRST else PROBES
    print(f"东财接口健康探测（{len(probes)} 域，间隔 5s）")
    print("=" * 60)
    failed = []
    for i, (name, url) in enumerate(probes):
        st = probe(name, url)
        print(f"  [{name:<14}] {st}")
        if st != "OK":
            failed.append(name)
        if i < len(probes) - 1:
            time.sleep(5)
    if failed:
        print(f"\nFAIL: {failed}")
        print(
            "提示: 东财为 IP×子域级风控，20h-48h 自然恢复；系统 fflow 三域轮换已兜底，不影响核心链路"
        )
        return 1
    print("\n全部 OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
