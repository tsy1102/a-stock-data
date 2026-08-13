@echo off
REM ============================================================================
REM upload_reports_to_gd.bat - Re-upload missing reports to Google Drive
REM ============================================================================
REM Reuses project GD logic (gd_uploader.py): skip files already on Drive,
REM upload only missing ones. Stock reports -> "code-name" subfolder,
REM val/mak reports -> type folder.
REM
REM Usage:
REM   upload_reports_to_gd.bat            (scan + upload)
REM   upload_reports_to_gd.bat --dry-run  (scan only)
REM NOTE: keep this file ASCII-only + CRLF (cmd parses bat in ANSI codepage)
REM ============================================================================

setlocal
chcp 65001 >nul

REM Locate script dir (self-contained: bat + py in same folder)
set "BAT_DIR=%~dp0"

REM Probe Python (SYSTEM_PYTHON_EXE first, then PATH python.exe)
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
    echo [ERROR] Python not found. Set env SYSTEM_PYTHON_EXE.
    exit /b 1
)

echo [INFO] Using Python: %PYTHON_EXE%
echo [INFO] Script: %BAT_DIR%upload_reports_to_gd.py
echo.

REM Call sibling script (relative path, no hardcode)
"%PYTHON_EXE%" "%BAT_DIR%upload_reports_to_gd.py" %*
exit /b %errorlevel%
