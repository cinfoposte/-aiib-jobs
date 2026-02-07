@echo off
REM AIIB Feed Auto-Update Script
REM This script updates the RSS feed automatically

echo ========================================
echo AIIB Job Feed Update
echo ========================================
echo Starting update at %date% %time%
echo.

cd /d "%~dp0"

echo Running scraper...
py aiib_scraper.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS! Feed updated successfully.
    echo File: %~dp0aiib_jobs.xml
    echo ========================================
) else (
    echo.
    echo ========================================
    echo ERROR! Feed update failed.
    echo Error code: %ERRORLEVEL%
    echo ========================================
)

echo.
echo Update completed at %date% %time%
echo.

REM Uncomment the next line to keep window open for debugging
REM pause
