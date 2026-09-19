#!/usr/bin/env python3
# comte_runtime_keystream.py
# ---------------------------------------------------------------------------
# 路径 1（运行时内存捕获 · 降维打击）：从【运行中】的 TdxW.exe 进程内存里定位
# 已经被客户端解密出来的 comte INI 明文，与磁盘上的密文逐字节异或，直接提取
# 完整的【位置式密钥流】keystream.bin，并落盘解密后的 INI。
#
# 为什么这是万能打法：无论底层是「自定义 PRNG 流密码」还是「AES-CTR / AES-OFB
# 流式模式」，可观测行为都是 C[i] = P[i] ^ KS[i]（KS 仅与位置 i 相关）。只要拿
# 到一份解密明文 P，就能反解出整条 KS，离线解密同族全部文件。它不依赖拿到
# 16 字节密钥，因此比"动态断点抓 AES 密钥"更稳健。
#
# 用法:
#   python comte_runtime_keystream.py [comte_dat_path]
#   默认 comte_dat_path = C:\new_tdx64\nacomte.dat（主族，最长 9620 字节载荷）
# 前置: TdxW.exe 必须正在运行（已把 comte 配置解密进内存）。
#
# 注意: 仅需管理员权限读取自身进程内存；本脚本仅做本地数据格式自解析研究，
#       结论不构成任何投资建议。
# ---------------------------------------------------------------------------
import sys, os, ctypes, ctypes.wintypes

kernel32 = ctypes.windll.kernel32

PROCESS_VM_READ = 0x0010
PROCESS_QUERY_INFORMATION = 0x0400

MEM_COMMIT = 0x1000
PAGE_READABLE = (0x02, 0x04, 0x20, 0x40)  # RO / RW / EXEC_READ / EXEC_RW


class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", ctypes.wintypes.DWORD),
        ("RegionSize", ctypes.c_size_t),
        ("State", ctypes.wintypes.DWORD),
        ("Protect", ctypes.wintypes.DWORD),
        ("Type", ctypes.wintypes.DWORD),
    ]


class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize", ctypes.wintypes.DWORD),
        ("cntUsage", ctypes.wintypes.DWORD),
        ("th32ProcessID", ctypes.wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.c_void_p),
        ("th32ModuleID", ctypes.wintypes.DWORD),
        ("cntThreads", ctypes.wintypes.DWORD),
        ("th32ParentProcessID", ctypes.wintypes.DWORD),
        ("pcPriClassBase", ctypes.wintypes.LONG),
        ("dwFlags", ctypes.wintypes.DWORD),
        ("szExeFile", ctypes.c_char * 260),
    ]


def find_pid(name):
    hSnap = kernel32.CreateToolhelp32Snapshot(0x00000002, 0)  # TH32CS_SNAPPROCESS
    if hSnap == -1 or hSnap is None:
        return None
    pe = PROCESSENTRY32()
    pe.dwSize = ctypes.sizeof(PROCESSENTRY32)
    pid = None
    if kernel32.Process32First(hSnap, ctypes.byref(pe)):
        while True:
            if pe.szExeFile.decode("ascii", "ignore").lower() == name.lower():
                pid = pe.th32ProcessID
                break
            if not kernel32.Process32Next(hSnap, ctypes.byref(pe)):
                break
    kernel32.CloseHandle(hSnap)
    return pid


def scan_marker(pid, marker, chunk_cap=4 * 1024 * 1024, max_hits=80):
    """遍历进程可提交可读页，返回所有 marker 出现的进程内虚拟地址。"""
    hProc = kernel32.OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, pid)
    if not hProc:
        raise OSError("OpenProcess 失败（可能需要以管理员身份运行）")
    hits = []
    addr = 0
    mbi = MEMORY_BASIC_INFORMATION()
    while addr < 0x7FFFFFFFFFFF:
        if not kernel32.VirtualQueryEx(
            hProc, ctypes.c_void_p(addr), ctypes.byref(mbi), ctypes.sizeof(mbi)
        ):
            break
        if mbi.RegionSize == 0:
            addr += 0x1000
            continue
        if mbi.State == MEM_COMMIT and mbi.Protect in PAGE_READABLE:
            region_base = addr
            remaining = mbi.RegionSize
            while remaining > 0 and len(hits) < max_hits:
                n = min(remaining, chunk_cap)
                buf = ctypes.create_string_buffer(n)
                got = ctypes.c_size_t(0)
                if kernel32.ReadProcessMemory(
                    hProc, ctypes.c_void_p(region_base), buf, n, ctypes.byref(got)
                ):
                    data = bytes(buf[: got.value])
                    i = data.find(marker)
                    while i != -1 and len(hits) < max_hits:
                        hits.append(region_base + i)
                        i = data.find(marker, i + 1)
                region_base += n
                remaining -= n
        addr = addr + mbi.RegionSize
    kernel32.CloseHandle(hProc)
    return hits


def main():
    comte_path = sys.argv[1] if len(sys.argv) > 1 else r"C:\new_tdx64\nacomte.dat"
    if not os.path.exists(comte_path):
        print(f"找不到 comte 文件: {comte_path}")
        return
    with open(comte_path, "rb") as f:
        C = f.read()
    payload_len = len(C) - 16

    pid = find_pid("TdxW.exe")
    if not pid:
        print("未找到运行中的 TdxW.exe。请先启动通达信行情客户端再运行本脚本。")
        return
    print(f"[+] TdxW.exe PID = {pid}")

    marker = b"[USER]\r\n"
    hits = scan_marker(pid, marker)
    print(f"[+] 内存中以 {marker!r} 命中 {len(hits)} 处")
    if not hits:
        for m in (b"HostName01=", b"IPAddress01=", b"[HQHOST]"):
            hits = scan_marker(pid, m)
            if hits:
                print(f"[+] 改用备用标记 {m!r}，命中 {len(hits)} 处")
                break
    if not hits:
        print("[-] 未定位到解密后的 INI 明文（可能客户端尚未加载 comte 配置）。")
        return

    base = hits[0]
    L = min(payload_len, 20000)
    hProc = kernel32.OpenProcess(PROCESS_VM_READ, False, pid)
    buf = ctypes.create_string_buffer(L)
    got = ctypes.c_size_t(0)
    ok = kernel32.ReadProcessMemory(hProc, ctypes.c_void_p(base), buf, L, ctypes.byref(got))
    kernel32.CloseHandle(hProc)
    if not ok:
        print("[-] 在命中地址读取内存失败。")
        return
    P = bytes(buf[: got.value])

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
    print("[+] KS[0:17] =", KS[:17].hex(), "（主族应为 f96b49adae221c9abaa02dd63903762fa0）")
    print("----- 解密 INI 前 240 字节预览（GBK）-----")
    print(P[:240].decode("gbk", "replace"))


if __name__ == "__main__":
    main()
