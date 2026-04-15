# Doubao 图片生成器

基于 Doubao-Seedream-5.0-lite 的AI图片生成应用。

## 项目结构

```
doubao_test/
├── backend/                 # Python FastAPI 后端
│   ├── app/
│   │   ├── main.py         # FastAPI 主入口
│   │   ├── config.py       # 配置管理
│   │   ├── models.py       # 数据模型
│   │   ├── api/            # API路由
│   │   └── services/       # 服务层
│   ├── requirements.txt    # Python依赖
│   └── .env.example        # 环境变量示例
├── frontend/               # Vue 3 + Ant Design 前端
│   ├── src/
│   │   ├── components/    # 组件
│   │   ├── views/          # 页面
│   │   ├── api/            # API调用
│   │   └── stores/         # 状态管理
│   └── package.json
└── scripts/                # 启动脚本
```

## 快速开始

### 1. 配置API密钥

1. 复制环境变量示例文件：
   ```bash
   cp backend/.env.example backend/.env
   ```

2. 编辑 `backend/.env`，填入您的API密钥：
   ```
   ARK_API_KEY=您的密钥
   ```

### 2. 启动后端服务

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8886 --reload
```

### 3. 启动前端服务

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173

## API接口

### 生成图片
- `POST /api/v1/images/generate`

### 获取历史
- `GET /api/v1/images/history/list`

### 获取详情
- `GET /api/v1/images/{image_id}`

### 删除图片
- `DELETE /api/v1/images/{image_id}`

### 下载图片
- `GET /api/v1/images/download/{image_id}`

### 清空历史
- `DELETE /api/v1/images/history/clear`

### 健康检查
- `GET /health`

## 功能特性

- AI图片生成（基于 Doubao-Seedream-5.0-lite 模型）
- 文生图功能：根据文字描述生成图片
- 图生图功能：根据输入图片生成新图片
- 多种尺寸支持（1K/2K/4K/竖图1K/竖图2K）
- 支持批量生成（1-4张）
- 生成历史记录管理
- 图片预览和下载
- 响应式布局
- CORS跨域支持

## 技术栈

- 后端：Python 3.8+ / FastAPI / volcengine-python-sdk
- 前端：Vue 3 / Vite / Ant Design Vue / Pinia
- AI模型：Doubao-Seedream-5.0-lite（`doubao-seedream-5-0-260128`）

## 接口文档

详细接口说明请查看 [API接口文档](./docs/API接口文档.md)，或访问 http://localhost:8886/docs 查看自动生成的 Swagger 文档。

## 新增功能 - 图生图

应用现在支持图生图功能，可以通过以下两种方式提供输入图片：

1. **上传本地图片**：直接上传本地图片文件
2. **图片URL**：输入公开的图片URL地址
3. **Base64编码**：输入图片的base64编码字符串

### 图生图接口

- **路径**: `POST /api/v1/images/generate-from-image`
- **参数**: 
  - `prompt`: 图片描述提示词（必填）
  - `image_url`: 输入图片URL（与image_base64二选一）
  - `image_base64`: 输入图片base64数据（与image_url二选一）
  - `size`: 图片尺寸（可选，默认2K）
  - `n`: 生成数量（可选，默认1）
  - `style`: 风格预设（可选）
  - `negative_prompt`: 负向提示词（可选）
  - `watermark`: 是否添加水印（可选，默认true）
  - `strength`: 生成强度（可选，0-1，默认0.75）
