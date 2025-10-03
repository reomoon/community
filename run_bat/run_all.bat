@echo off
chcp 65001 >nul 2>&1
echo ===============================================
echo   Community Aggregator - All in One
echo ===============================================
echo.

cd /d "%~dp0\.."

echo What would you like to run?
echo.
echo 1. Crawler only
echo 2. Mobile capture only  
echo 3. Crawler + Capture (sequential)
echo 4. Start local server
echo 5. Exit
echo.

:menu
set /p choice=Select number (1-5): 

if "%choice%"=="1" goto crawler
if "%choice%"=="2" goto capture
if "%choice%"=="3" goto both
if "%choice%"=="4" goto server
if "%choice%"=="5" goto exit

echo [ERROR] Invalid selection. Please try again.
goto menu

:crawler
echo.
echo [CRAWLER] Starting web crawling...
python dev/crawl_only.py
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Crawling completed!
) else (
    echo [ERROR] Crawling failed!
)
goto end

:capture
echo.
echo [CAPTURE] Starting mobile screenshot capture...
python capture_posts.py
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Capture completed!
    if exist capture (
        explorer capture
    )
) else (
    echo [ERROR] Capture failed!
)
goto end

:both
echo.
echo [STEP 1] Starting web crawling...
python dev/crawl_only.py
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Crawling completed!
    echo.
    echo [STEP 2] Starting mobile screenshot capture...
    python capture_posts.py
    if %ERRORLEVEL% EQU 0 (
        echo [SUCCESS] All tasks completed!
        if exist capture (
            explorer capture
        )
    ) else (
        echo [ERROR] Capture failed!
    )
) else (
    echo [ERROR] Crawling failed! Skipping capture.
)
goto end

:server
echo.
echo [SERVER] Starting local server...
echo Open http://localhost:5000 in your browser.
echo Press Ctrl+C to stop the server.
echo.
python run.py
goto end

:exit
echo Goodbye!
exit /b 0

:end
echo.
echo Task completed. Press any key to exit...
pause >nul