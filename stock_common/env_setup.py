"""env_setup.py — 首次运行自动检测/修复 UTF-8 环境（V16.4.0）。

幂等：已配置 → 零开销跳过；缺失 → 自动 setx/写 Profile/设 ExecutionPolicy。
检测项：
  1. PYTHONUTF8=1（用户级环境变量，注册表）
  2. PowerShell Profile 含 UTF-8 初始化
  3. ExecutionPolicy CurrentUser 允许本地脚本（RemoteSigned）

V16.4.1 新增 ensure_utf8_stdio()：把输出编码强制点下沉到项目代码自身。
背景：乱码根因是"运行时输出字节编码"混搭——PowerShell 按系统代码页
(936/GBK) 写输出，opencode/Codex 等工具统一按 UTF-8 解码 → 乱码。
本函数纯标准库，不依赖环境变量/shell/Profile/系统代码页：任何机器、
任何 agent、任何调用方式，只要执行项目入口脚本，输出即 UTF-8。
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def ensure_utf8_stdio() -> None:
    """强制 stdout/stderr 输出 UTF-8（V16.4.1，下沉到项目代码自身）。

    任何机器/任何 agent（opencode/Codex/手动）/任何调用方式，只要执行
    项目入口脚本，输出即 UTF-8；与 shell 代码页、环境变量、Profile 无关。
    幂等：已 UTF-8 的环境零开销跳过。
    """
    for _stream in (sys.stdout, sys.stderr):
        if _stream is not None and hasattr(_stream, "reconfigure"):
            try:
                _stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def _py_env_ok() -> bool:
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
            return winreg.QueryValueEx(k, "PYTHONUTF8")[0] == "1"
    except OSError:
        return False


def _profile_path() -> Path:
    """实际 PowerShell Profile 路径（跟随 OneDrive 文档重定向）。"""
    try:
        r = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command",
             "[Environment]::GetFolderPath('MyDocuments')"],
            capture_output=True, text=True, timeout=15,
        )
        docs = r.stdout.strip() if r.stdout else ""
        if docs:
            return Path(docs) / "WindowsPowerShell" / "Microsoft.PowerShell_profile.ps1"
    except Exception:
        pass
    return Path(os.path.expanduser("~")) / "Documents" / "WindowsPowerShell" / "Microsoft.PowerShell_profile.ps1"


_PROFILE_BODY = (
    "# UTF-8 environment init\n"
    "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8\n"
    "$OutputEncoding = [Console]::OutputEncoding\n"
    "chcp 65001 > $null\n"
)


def _profile_ok() -> bool:
    p = _profile_path()
    if not p.exists():
        return False
    try:
        return "OutputEncoding" in p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False


def _execution_policy_ok() -> bool:
    try:
        r = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", "(Get-ExecutionPolicy -Scope CurrentUser)"],
            capture_output=True, text=True, timeout=15,
        )
        v = r.stdout.strip() if r.stdout else ""
        return v in ("RemoteSigned", "Unrestricted", "Bypass")
    except Exception:
        return False


def ensure_utf8_env(verbose: bool = True) -> bool:
    """检测并修复 UTF-8 环境。返回 True=全部就绪；False=修复失败。"""
    if sys.platform != "win32":
        return True
    ok = True

    # 1. PYTHONUTF8
    if not _py_env_ok():
        try:
            subprocess.run(["setx", "PYTHONUTF8", "1"], capture_output=True, text=True, timeout=15)
            if verbose:
                print("  [env] 已设置 PYTHONUTF8=1（用户级，重登后生效）", flush=True)
        except Exception as e:
            ok = False
            print(f"  [env] PYTHONUTF8 设置失败: {e}", flush=True)

    # 2. PowerShell Profile
    if not _profile_ok():
        try:
            p = _profile_path()
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(_PROFILE_BODY, encoding="utf-8")
            if verbose:
                print(f"  [env] 已创建 PowerShell Profile（UTF-8 初始化）: {p}", flush=True)
        except OSError as e:
            ok = False
            print(f"  [env] Profile 创建失败: {e}", flush=True)

    # 3. ExecutionPolicy
    if not _execution_policy_ok():
        try:
            subprocess.run(
                ["powershell.exe", "-NoProfile", "-Command",
                 "Set-ExecutionPolicy -Scope CurrentUser RemoteSigned -Force"],
                capture_output=True, text=True, timeout=15,
            )
            if verbose:
                print("  [env] 已设置 ExecutionPolicy=RemoteSigned（允许 Profile 加载）", flush=True)
        except Exception as e:
            ok = False
            print(f"  [env] ExecutionPolicy 设置失败: {e}", flush=True)

    if verbose and ok:
        changed = not (_py_env_ok() and _profile_ok() and _execution_policy_ok())
        if changed:
            print("  [env] UTF-8 环境初始化完成（注销重登后 Python/PowerShell 中文输出永久正常）", flush=True)
    return ok
