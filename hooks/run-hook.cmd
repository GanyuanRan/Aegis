: << 'CMDBLOCK'
@echo off
REM Cross-platform polyglot wrapper for hook scripts.
REM On Windows: cmd.exe runs the batch portion, which finds and calls bash.
REM On Unix: the shell interprets this as a script (: is a no-op in bash).
REM
REM Hook scripts use extensionless filenames (e.g. "session-start" not
REM "session-start.sh") so Claude Code's Windows auto-detection -- which
REM prepends "bash" to any command containing .sh -- doesn't interfere.
REM
REM Usage: run-hook.cmd <script-name> [args...]

if "%~1"=="" (
    echo run-hook.cmd: missing script name >&2
    exit /b 1
)

set "HOOK_DIR=%~dp0"
set "PF86=%ProgramFiles(x86)%"

REM 1. Per-user Git for Windows. The common non-admin install lives here and is
REM    invisible to a Program Files-only probe.
if exist "%LOCALAPPDATA%\Programs\Git\bin\bash.exe" (
    "%LOCALAPPDATA%\Programs\Git\bin\bash.exe" "%HOOK_DIR%%~1" %2 %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)

REM 2. Machine-wide Git for Windows.
if exist "%ProgramFiles%\Git\bin\bash.exe" (
    "%ProgramFiles%\Git\bin\bash.exe" "%HOOK_DIR%%~1" %2 %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)
if exist "%PF86%\Git\bin\bash.exe" (
    "%PF86%\Git\bin\bash.exe" "%HOOK_DIR%%~1" %2 %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)

REM 3. Other bash installs (MSYS2, Cygwin, scoop). Resolve each `where` hit
REM    through :pick_bash instead of calling bare `bash`: the default search
REM    order includes the current directory, so a repository could plant
REM    bash.cmd and have it run at session start.
set "AEGIS_BASH="
for /f "delims=" %%B in ('where bash 2^>nul') do (
    if not defined AEGIS_BASH call :pick_bash "%%B"
)
if defined AEGIS_BASH (
    "%AEGIS_BASH%" "%HOOK_DIR%%~1" %2 %3 %4 %5 %6 %7 %8 %9
    exit /b %ERRORLEVEL%
)

REM 4. No usable bash. Stay silent and keep exit success: the plugin still
REM    works, it just has no SessionStart context injection.
exit /b 0

:pick_bash
set "CANDIDATE=%~1"
if "%CANDIDATE%"=="" exit /b 0
REM Require an absolute drive-rooted path: bare names and relative hits would be
REM resolved against the working directory.
echo.%CANDIDATE%| findstr /r /c:"^[A-Za-z]:\\" >nul || exit /b 0
REM Skip WSL launchers: the System32 shim and the Store alias both forward to a
REM Linux distro, which either is absent or reads Windows paths as POSIX paths.
echo.%CANDIDATE%| findstr /i /c:"\\system32\\bash.exe" /c:"\\WindowsApps\\bash.exe" >nul && exit /b 0
REM Require the real executable name. `where` reports bash.cmd/bash.bat from PATH
REM entries ahead of the real one, including the current directory, and cmd.exe
REM would run that planted script at session start.
echo.%~nx1| findstr /i /c:"^bash\.exe$" >nul || exit /b 0
REM Reject anything resolved inside the current directory, even when the name
REM looks right: that is the path a repository can plant in place.
for %%D in ("%CANDIDATE%") do set "CAND_DIR=%%~dpD"
call :normalize_dir "%CAND_DIR%"
set "CAND_NORM=%NORMALIZED%"
call :normalize_dir "%CD%\"
if /i "%CAND_NORM%"=="%NORMALIZED%" exit /b 0
set "AEGIS_BASH=%CANDIDATE%"
exit /b 0

:normalize_dir
REM Strip trailing backslashes so drive-root and nested paths compare equally.
set "NORMALIZED=%~1"
if "%NORMALIZED:~-1%"=="\" set "NORMALIZED=%NORMALIZED:~0,-1%"
exit /b 0
CMDBLOCK

# Unix: run the named script directly
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT_NAME="$1"
shift
exec bash "${SCRIPT_DIR}/${SCRIPT_NAME}" "$@"
