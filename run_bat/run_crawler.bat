@echo off
chcp 65001 >nul 2>&1
echo ===============================================
echo   Community Aggregator - Crawler Only
echo ===============================================
echo.

cd /d "%~dp0\.."

echo [CRAWLER] Starting web crawling...
echo.

python dev/crawl_only.py

echo.
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Crawling completed successfully!
    echo [INFO] Check results on the website.
) else (
    echo [ERROR] Crawling failed.
    echo [TIP] Please check internet connection and Python environment.
)

echo.
echo Start local server? (y/n)
set /p choice=Choice: 
if /i "%choice%"=="y" (
    echo.
    echo [SERVER] Starting local server...
    echo Open http://localhost:5000 in your browser.
    echo Press Ctrl+C to stop the server.
    echo.
    python run.py
)

echo.
echo Task completed. Press any key to exit...
pause >nul