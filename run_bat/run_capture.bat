@echo off
chcp 65001 >nul 2>&1
echo ===============================================
echo   Community Aggregator - Mobile Capture
echo ===============================================
echo.

cd /d "%~dp0\.."

echo [CAPTURE] Starting mobile screenshot capture...
echo.

python capture_posts.py

echo.
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Mobile capture completed successfully!
    echo [INFO] Check the capture folder for generated files.
) else (
    echo [ERROR] Mobile capture failed.
    echo [TIP] Please check if Python and required packages are installed.
)

echo.
echo Open capture folder? (y/n)
set /p choice=Choice: 
if /i "%choice%"=="y" (
    if exist capture (
        explorer capture
    ) else (
        echo [WARNING] Capture folder not found.
    )
)

echo.
echo Task completed. Press any key to exit...
pause >nul