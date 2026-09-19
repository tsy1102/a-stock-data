#!/usr/bin/env python3
# comte_decrypt_offline.py
# ---------------------------------------------------------------------------
# 用运行时捕获的位置式密钥流，离线解密全部 comte 文件并校验可读性。
# 主族 5 文件（nacomte/nbcomte/nscomte/nscomte_std/nzcomte）共享同一条密钥流；
# nvcomte 独立种子，需从 TdxW 内存再捕获一次（本脚本自动尝试）。
#
# 前置: 须先运行 comte_runtime_keystream.py 生成 nacomte.dat.keystream.bin；
#       且 TdxW.exe 正在运行（用于 nvcomte 自动捕获）。
# ---------------------------------------------------------------------------
import os, ctypes, ctypes.wintypes
import comte_runtime_keystream as cs

BASE = r"C:\new_tdx64"
CACHE = os.path.join(BASE, "T0002", "hq_cache")

MAIN = {
    "nacomte.dat":      os.path.join(BASE, "nacomte.dat"),
    "nbcomte.dat":      os.path.join(BASE, "nbcomte.dat"),
    "nscomte.dat":      os.path.join(CACHE, "nscomte.dat"),
    "nscomte_std.dat":  os.path.join(CACHE, "nscomte_std.dat"),
    "nzcomte.dat":      os.path.join(CACHE, "nzcomte.dat"),
}
NV = {"nvcomte.dat": os.path.join(CACHE, "nvcomte.dat")}


def readability(b):
    if not b:
        return 0.0
    # 计入 GBK 高位字节（中文）与 NUL 填充（固定宽度券商名字段），否则会被误判不可读
    good = sum(1 for x in b if (32 <= x < 127) or x in (9, 10, 13) or x >= 0x80 or x == 0)
    return good / len(b)


def decrypt_with(cipher_path, ks, out_path):
    with open(cipher_path, "rb") as f:
        C = f.read()
    pl = len(C) - 16
    n = min(pl, len(ks))
    P = bytes(C[16 + i] ^ ks[i] for i in range(n))
    with open(out_path, "wb") as f:
        f.write(P)
    return P, pl


def capture_nv_keystream(nv_path):
    """遍历内存中所有 HostName01= 命中，找出能让 nvcomte 解密为可读明文的缓冲。"""
    with open(nv_path, "rb") as f:
        NV_C = f.read()
    nvl = len(NV_C) - 16
    pid = cs.find_pid("TdxW.exe")
    if not pid:
        return None
    hits = cs.full_scan(pid, b"HostName01=")
    best = None
    for M_abs in hits:
        region, base = cs.read_region(pid, M_abs)
        if not region:
            continue
        M_rel = M_abs - base
        start = cs.detect_buffer_start(region, M_rel, nvl)
        P = region[start: start + nvl]
        if len(P) < nvl * 0.8:
            continue
        KS = bytes(NV_C[16 + i] ^ P[i] for i in range(min(len(P), nvl)))
        test = bytes(NV_C[16 + i] ^ KS[i] for i in range(min(nvl, len(KS))))
        r = readability(test)
        if r > 0.92 and (best is None or r > best[1]):
            best = (KS, r, M_abs)
    return best


def main():
    ks_main = open(MAIN["nacomte.dat"] + ".keystream.bin", "rb").read()
    print(f"[+] 主族密钥流长度 = {len(ks_main)}")

    print("\n=== 主族 5 文件离线解密（共享密钥流）===")
    all_ok = True
    for name, path in MAIN.items():
        P, pl = decrypt_with(path, ks_main, path + ".decrypted.ini")
        r = readability(P)
        ok = r > 0.85
        all_ok = all_ok and ok
        print(f"  {name:16s} payload={pl:5d} readability={r:.3f} {'OK' if ok else 'BAD'}  head={P[:48].decode('gbk','replace')!r}")

    print(f"\n主族跨文件一致性: {'全部可读 -> 密钥流对齐正确 ✅' if all_ok else '存在异常 ❌'}")

    print("\n=== nvcomte（独立种子）自动捕获 ===")
    name, path = next(iter(NV.items()))
    res = capture_nv_keystream(path)
    if res:
        KS, r, addr = res
        P, pl = decrypt_with(path, KS, path + ".decrypted.ini")
        open(path + ".keystream.bin", "wb").write(KS)
        print(f"  nvcomte 命中(addr={hex(addr)}) readability={r:.3f} -> 已写出 keystream.bin + decrypted.ini")
        print(f"  KS[0:16]={KS[:16].hex()}  head={P[:48].decode('gbk','replace')!r}")
    else:
        print("  [-] 未从内存定位到 nvcomte 明文缓冲（需手动确认其 HostName01= 是否载入）。")

    print("\n[+] 全部解密 INI 已落盘至对应 comte 文件旁（*.decrypted.ini）。")


if __name__ == "__main__":
    main()
