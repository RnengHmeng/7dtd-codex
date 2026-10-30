@echo off
chcp 65001 >nul
cd /d "%~dp0"
python scripts\build_site.py %*
echo.
echo 生成完成：site\
pause
