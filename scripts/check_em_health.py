"""东财接口健康探测（低频，防封锁）。

用法:
    python scripts/check_em_health.py          # 全量 6 域探测（间隔 5s，~35s）
    python scripts/check_em_health.py --once   # 只测 1 个域（push2 主域，验证恢复用）

退出码: 0=全部 OK / 1=有 FAIL。
注意: 不要高频运行（东财 IP 风控），建议每天最多 1-2 次；失败项会自动跳过等待（20h+ 自然恢复）。
"""
import sys
import time

for _s in (sys.stdout, sys.stderr):
    if _s is not None and hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

import requests

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

PROBES = [
    ("push2", "https://push2.eastmoney.com/api/qt/stock/get?secid=1.600519&fields=f43,f57,f58,f167"),
    ("83.push2", "https://83.push2.eastmoney.com/api/qt/clist/get?pn=1&pz=5&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:1+t:2&fields=f12,f14,f2,f3"),
    ("push2delay", "https://push2delay.eastmoney.com/api/qt/stock/get?secid=1.600519&fields=f43,f57,f58,f167"),
    ("push2his", "https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.600519&fields1=f1,f2,f3&fields2=f51,f52,f53&klt=101&fqt=1&beg=20260801&end=20260811"),
    ("push2ex", "https://push2ex.eastmoney.com/getTopicZTPool?ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt&Pageindex=0&pagesize=1&sort=fbt:asc&date=20260811"),
    ("datacenter-web", "https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_MUTUAL_DEAL_HISTORY&columns=ALL&pageNumber=1&pageSize=1"),
]

ONLY_FIRST = "--once" in sys.argv


def probe(name: str, url: str) -> str:
    try:
        r = requests.get(url, timeout=10,
                         headers={"User-Agent": UA, "Referer": "https://quote.eastmoney.com/"},
                         verify=True)
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
        print("提示: 东财为 IP×子域级风控，20h-48h 自然恢复；系统 fflow 三域轮换已兜底，不影响核心链路")
        return 1
    print("\n全部 OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
