import sys
sys.path.append(r"d:\GitHub\test")
from tdx_client import _tencent_batch_fallback

res = _tencent_batch_fallback(["600519", "000001", "300750"])
for k, v in res.items():
    print(k, v)
