@echo off
chcp 65001 >nul
echo ==========================================
echo   Doubao 图片生成器 - Windows启动脚本
echo ==========================================
echo.

cd /d "%~dp0"

echo [1/4] 检查Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo [2/4] 进入后端目录...
cd backend
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

echo [3/4] 激活虚拟环境并安装依赖...
call venv\Scripts\activate.bat
pip install -r requirements.txt

if not exist ".env" (
    if exist ".env.example" (
        echo 创建.env配置文件...
        copy .env.example .env
        echo.
        echo ==========================================
        echo   请编辑 backend\.env 文件
        echo   填入您的 ARK_API_KEY
        echo ==========================================
        echo.
    )
)

echo [4/4] 启动后端服务...
cd ..
echo.
echo ==========================================
echo   启动后端服务...
echo   API地址: http://localhost:8000
echo   文档: http://localhost:8000/docs
echo ==========================================
echo.

start "Doubao Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo 启动完成！
echo.
pause
