# Doubao 图片生成器 - 启动脚本

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "=========================================="
echo "  Doubao 图片生成器 - 启动脚本"
echo "=========================================="
echo ""

# 检查Python
if ! command -v python &> /dev/null; then
    echo -e "${RED}错误: 未找到Python，请先安装Python 3.8+${NC}"
    exit 1
fi

echo -e "${GREEN}[1/5]${NC} 进入后端目录..."
cd backend || exit

# 创建虚拟环境（可选）
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}创建虚拟环境...${NC}"
    python -m venv venv
fi

# 激活虚拟环境
echo -e "${YELLOW}激活虚拟环境...${NC}"
source venv/bin/activate

# 安装依赖
echo -e "${GREEN}[2/5]${NC} 安装Python依赖..."
pip install -r requirements.txt

# 检查环境变量
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}创建.env文件...${NC}"
        cp .env.example .env
        echo -e "${RED}请编辑.env文件，填入您的ARK_API_KEY${NC}"
    fi
fi

# 启动后端
echo -e "${GREEN}[3/5]${NC} 启动后端服务 (端口8000)..."
cd ..
echo -e "${GREEN}后端目录: $(pwd)${NC}"

# 返回项目根目录
cd ..

# 启动后端服务
echo ""
echo -e "${GREEN}=========================================="
echo "  启动后端服务..."
echo "  API地址: http://localhost:8000"
echo "  文档: http://localhost:8000/docs"
echo "==========================================${NC}"

# 在后台启动后端
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动前端
echo ""
echo -e "${GREEN}[4/5]${NC} 启动前端服务 (端口5173)..."
cd ../frontend

if ! command -v npm &> /dev/null; then
    echo -e "${RED}错误: 未找到npm，请先安装Node.js${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# 安装前端依赖
npm install

# 启动前端开发服务器
echo ""
echo -e "${GREEN}=========================================="
echo "  启动前端服务..."
echo "  前端地址: http://localhost:5173"
echo "==========================================${NC}"
npm run dev &
FRONTEND_PID=$!

# 等待前端启动
sleep 3

echo ""
echo -e "${GREEN}=========================================="
echo "  所有服务已启动！"
echo "  - 后端API: http://localhost:8000"
echo "  - API文档: http://localhost:8000/docs"
echo "  - 前端界面: http://localhost:5173"
echo "==========================================${NC}"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo ""

# 等待终止信号
trap "echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM
wait
