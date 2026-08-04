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
REM   "C:\Users\tsy11\AppData\Local\Python\pythoncore-3.12-64\python.exe" %*
REM ============================================================================

set PYTHON_EXE=C:\Users\tsy11\AppData\Local\Python\pythoncore-3.12-64\python.exe

REM Self-check: verify system Python exists
if not exist "%PYTHON_EXE%" (
    echo [ERROR] System Python 3.12 not found: %PYTHON_EXE%
    echo         Please update PYTHON_EXE in this script.
    exit /b 1
)

REM Put system Python dir at front of PATH
set PATH=C:\Users\tsy11\AppData\Local\Python\pythoncore-3.12-64;C:\Users\tsy11\AppData\Local\Python\pythoncore-3.12-64\Scripts;%PATH%

REM Forward all args to system Python
"%PYTHON_EXE%" %*