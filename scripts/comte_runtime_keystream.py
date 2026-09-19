#!/usr/bin/env python3
# comte_runtime_keystream.py  (v2 — 已修正对齐)
# ---------------------------------------------------------------------------
# 路径 1（运行时内存捕获 · 降维打击）：从【运行中】的 TdxW.exe 进程内存里定位
# 已经被客户端解密出来的 comte INI 明文，与磁盘上的密文逐字节异或，提取完整
# 【位置式密钥流】keystream.bin，并落盘解密后的 INI。
#
# v2 修正（2026-09-19）：
#   v1 用 [USER]\r\n 作主锚点，但该串在内存中实际为 0 命中；回退到 HostName01= 又
#   落在明文非零偏移处，导致 KS 错位（误把 C[0+i]^P[m+i] 当 KS[i]）。本版改为：
#   1) 取首个 HostName01= 命中的整块可读内存区（VirtualQueryEx 读整 region）；
#   2) 在命中前 payload_len 字节范围内自动探测【明文缓冲真正起点】（首个 [ 段头
#      且前一字节非可打印，或首段可打印率>85%）；
#   3) 从该起点取 payload_len 字节明文 P，KS = C[16:16+N] ^ P（KS 仅与偏移 i 相关）。
#   主族 5 文件共享同一位置式密钥流；nvcomte 独立种子需单独捕获。
#
# 用法: python comte_runtime_keystream.py [comte_dat_path]
# 前置: TdxW.exe 必须正在运行。
# ---------------------------------------------------------------------------
import sys, os, ctypes, ctypes.wintypes

kernel32 = ctypes.windll.kernel32
PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400
MEM_COMMIT = 0x1000
PAGE_READABLE = (0x02, 0x04, 0x20, 0x40)


class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_void_p), ("AllocationBase", ctypes.c_void_p),
                ("AllocationProtect", ctypes.wintypes.DWORD), ("RegionSize", ctypes.c_size_t),
                ("State", ctypes.wintypes.DWORD), ("Protect", ctypes.wintypes.DWORD),
                ("Type", ctypes.wintypes.DWORD)]


class PE32(ctypes.Structure):
    _fields_ = [("dwSize", ctypes.wintypes.DWORD), ("cntUsage", ctypes.wintypes.DWORD),
                ("th32ProcessID", ctypes.wintypes.DWORD), ("th32DefaultHeapID", ctypes.c_void_p),
                ("th32ModuleID", ctypes.wintypes.DWORD), ("cntThreads", ctypes.wintypes.DWORD),
                ("th32ParentProcessID", ctypes.wintypes.DWORD), ("pcPriClassBase", ctypes.c_long),
                ("dwFlags", ctypes.wintypes.DWORD), ("szExeFile", ctypes.c_char * 260)]


def find_pid(name):
    h = kernel32.CreateToolhelp32Snapshot(0x2, 0)
    pe = PE32(); pe.dwSize = ctypes.sizeof(PE32); pid = None
    if kernel32.Process32First(h, ctypes.byref(pe)):
        while True:
            if pe.szExeFile.decode("ascii", "ignore").lower() == name.lower():
                pid = pe.th32ProcessID; break
            if not kernel32.Process32Next(h, ctypes.byref(pe)): break
    kernel32.CloseHandle(h); return pid


def read_region(pid, addr, cap=16 * 1024 * 1024):
    """返回包含 addr 的整个可读 committed 内存区字节（用于定位连续明文缓冲）。"""
    h = kernel32.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, pid)
    if not h:
        raise OSError("OpenProcess 失败（可能需要管理员权限）")
    mbi = MBI()
    if not kernel32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)):
        kernel32.CloseHandle(h); return None, 0
    base = mbi.BaseAddress
    size = min(mbi.RegionSize, cap)
    buf = ctypes.create_string_buffer(size)
    got = ctypes.c_size_t(0)
    ok = kernel32.ReadProcessMemory(h, base, buf, size, ctypes.byref(got))
    kernel32.CloseHandle(h)
    if not ok:
        return None, 0
    return bytes(buf[: got.value]), base


def scan_region(pid, region_buf, marker, max_hits=400):
    """在已读出的 region 字节里找 marker 的相对偏移列表。"""
    offs = []
    i = region_buf.find(marker)
    while i != -1 and len(offs) < max_hits:
        offs.append(i)
        i = region_buf.find(marker, i + 1)
    return offs


def full_scan(pid, marker, chunk_cap=4 * 1024 * 1024, max_hits=400):
    """遍历进程可读 committed 区，返回 marker 出现的【进程内虚拟地址】列表。"""
    h = kernel32.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, pid)
    if not h:
        raise OSError("OpenProcess 失败（可能需要管理员权限）")
    hits = []
    addr = 0
    mbi = MBI()
    while addr < 0x7FFFFFFFFFFF:
        if not kernel32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)):
            break
        if mbi.RegionSize == 0:
            addr += 0x1000; continue
        if mbi.State == MEM_COMMIT and mbi.Protect in PAGE_READABLE:
            base = addr; rem = mbi.RegionSize
            while rem > 0 and len(hits) < max_hits:
                n = min(rem, chunk_cap)
                buf = ctypes.create_string_buffer(n)
                got = ctypes.c_size_t(0)
                if kernel32.ReadProcessMemory(h, ctypes.c_void_p(base), buf, n, ctypes.byref(got)):
                    data = bytes(buf[: got.value])
                    i = data.find(marker)
                    while i != -1 and len(hits) < max_hits:
                        hits.append(base + i)
                        i = data.find(marker, i + 1)
                base += n; rem -= n
        addr = addr + mbi.RegionSize
    kernel32.CloseHandle(h)
    return hits


def detect_buffer_start(region_buf, hit_off, back):
    """在 [hit_off-back, hit_off] 内探测明文缓冲真正起点（返回相对 region 的偏移）。"""
    lo = max(0, hit_off - back)
    # 优先：首个 '[' 段头且前一字节非可打印（强信号：INI 段起始 / 缓冲起始）
    for s in range(lo, hit_off + 1):
        if region_buf[s] == 0x5b:  # '['
            if s == 0 or region_buf[s - 1] < 0x20:
                # 段名可打印性粗检
                seg = region_buf[s + 1: s + 12]
                if sum(1 for b in seg if 32 <= b < 127) >= len(seg) - 2:
                    return s
    # 回退：首段可打印率 > 85%
    for s in range(lo, hit_off + 1):
        seg = region_buf[s: s + 200]
        if len(seg) < 200:
            continue
        pr = sum(1 for b in seg if 32 <= b < 127 or b in (9, 10, 13))
        if pr > 170:
            return s
    return lo


def main():
    comte_path = sys.argv[1] if len(sys.argv) > 1 else r"C:\new_tdx64\nacomte.dat"
    if not os.path.exists(comte_path):
        print(f"找不到 comte 文件: {comte_path}"); return
    with open(comte_path, "rb") as f:
        C = f.read()
    payload_len = len(C) - 16

    pid = find_pid("TdxW.exe")
    if not pid:
        print("未找到运行中的 TdxW.exe。请先启动通达信行情客户端。"); return
    print(f"[+] TdxW.exe PID = {pid}")

    # 全内存扫描拿到 HostName01= 的首个绝对虚拟地址，再读其所属整 region
    abs_hits = full_scan(pid, b"HostName01=")
    print(f"[+] 全内存 HostName01= 命中 {len(abs_hits)} 处")
    if not abs_hits:
        print("[-] 未定位到解密 INI 明文（客户端可能尚未加载 comte 配置）。"); return

    M_abs = abs_hits[0]
    region, base = read_region(pid, M_abs)
    if not region:
        print("[-] 读取命中所属内存区失败。"); return
    M_rel = M_abs - base
    print(f"[+] 命中所属 region base={hex(base)}，M_rel={M_rel}")

    start_rel = detect_buffer_start(region, M_rel, payload_len)
    print(f"[+] 明文缓冲起点(rel)={start_rel}（命中 rel={M_rel}，回退量={payload_len}，"
          f"缓冲起点距命中 {M_rel - start_rel} 字节）")

    P = region[start_rel: start_rel + payload_len]
    if len(P) < payload_len:
        print(f"[!] 明文长度 {len(P)} < 载荷 {payload_len}，可能未完整捕获（回退/region 边界）。")
    n = min(len(P), payload_len)
    KS = bytes(C[16 + i] ^ P[i] for i in range(n))

    out_ks = comte_path + ".keystream.bin"
    out_ini = comte_path + ".decrypted.ini"
    with open(out_ks, "wb") as f:
        f.write(KS)
    with open(out_ini, "wb") as f:
        f.write(P[:n])
    print(f"[+] 密钥流长度 = {n}，已写出: {out_ks}")
    print(f"[+] 解密 INI 已写出: {out_ini}")
    print(f"[+] 真实 KS[0:16] = {KS[:16].hex()}（此前基于错误 [USER] 假设的 f96b49.. 已作废）")
    print("----- 解密 INI 前 320 字节预览（GBK）-----")
    print(P[:320].decode("gbk", "replace"))


if __name__ == "__main__":
    main()
