@echo off
REM ============================================================================
REM run_with_system_python.bat - Run commands using system Python 3.12
REM ============================================================================
REM NOTE: AGENTS.md 优先使用 .ps1 版(run_with_system_python.ps1);
REM       这个 .bat 仅保留给 cmd / 老式终端。PowerShell 用户请改用:
REM         .\scripts\run_with_system_python.ps1 @args
REM Purpose: Avoid TRAE IDE's built-in Python 3.10 and force system Python 3.12
REM
REM Usage:
REM   scripts\run_with_system_python.bat -m pytest tests/test_cache.py
REM   scripts\run_with_system_python.bat -m unittest tests.test_cache
REM   scripts\run_with_system_python.bat get_sht_report.py 600519 --no-upload
REM
REM Equivalent direct command:
REM   set SYSTEM_PYTHON_EXE=C:\path\to\python.exe 然后运行本脚本
REM ============================================================================

setlocal

REM V16.4.1: 强制 UTF-8 代码页（cmd 老式终端中文输出不乱码；仅影响本进程）
chcp 65001 >nul

REM ────────────────────────────────────────────────────────────────────────────
REM 自动探测系统 Python 3.12（不再硬编码路径）
REM 探测顺序:
REM   1) 环境变量 SYSTEM_PYTHON_EXE（优先）
REM   2) PATH 上第一个 python.exe（校验版本为 3.12.x）
REM ────────────────────────────────────────────────────────────────────────────
set "PYTHON_EXE="
if defined SYSTEM_PYTHON_EXE (
    if exist "%SYSTEM_PYTHON_EXE%" set "PYTHON_EXE=%SYSTEM_PYTHON_EXE%"
)

if not defined PYTHON_EXE (
    for /f "delims=" %%i in ('where python.exe 2^>nul') do (
        if not defined PYTHON_EXE set "PYTHON_EXE=%%i"
    )
)

if not defined PYTHON_EXE (
    echo [ERROR] System Python 3.12 not found. Set env SYSTEM_PYTHON_EXE.
    exit /b 1
)

REM Version check (temp file to avoid nested-quote issues)
"%PYTHON_EXE%" --version > "%TEMP%\run_with_system_python_ver.txt" 2>&1
set /p PV=<"%TEMP%\run_with_system_python_ver.txt"
del "%TEMP%\run_with_system_python_ver.txt" >nul 2>&1
echo %PV% | findstr /R "Python 3\.12" >nul
if errorlevel 1 (
    echo [ERROR] %PYTHON_EXE% is not Python 3.12: %PV%
    echo         Set env SYSTEM_PYTHON_EXE to a Python 3.12 interpreter.
    exit /b 1
)

REM Put system Python dir at front of PATH
for %%d in ("%PYTHON_EXE%") do set "PYTHON_DIR=%%~dpd"
set "PATH=%PYTHON_DIR%;%PYTHON_DIR%Scripts;%PATH%"

REM Forward all args to system Python
"%PYTHON_EXE%" %*
exit /b %errorlevel%