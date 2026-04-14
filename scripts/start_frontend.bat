@echo off
chcp 65001 >nul
echo ==========================================
echo   Doubao 图片生成器 - 前端启动脚本
echo ==========================================
echo.

cd /d "%~dp0..\frontend"

if not exist "node_modules" (
    echo 安装前端依赖...
    call npm install
)

echo.
echo ==========================================
echo   启动前端开发服务器...
echo   地址: http://localhost:5173
echo ==========================================
echo.

call npm run dev

pause
