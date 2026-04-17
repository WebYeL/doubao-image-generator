# Doubao 图片/视频生成器

基于 Doubao-Seedream-5.0-lite 的 AI 图片生成和 Doubao-Seedance 2.0 的视频生成应用。

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
│   │       ├── image_service.py   # 图片生成服务
│   │       ├── video_service.py   # 视频生成服务
│   │       └── storage.py         # 存储服务
│   ├── requirements.txt    # Python依赖
│   └── .env.example        # 环境变量示例
├── frontend/               # Vue 3 + Ant Design 前端
│   ├── src/
│   │   ├── components/    # 组件
│   │   │   ├── ImageGallery.vue   # 图片画廊
│   │   │   ├── ImagePromptForm.vue # 图片表单
│   │   │   ├── VideoGallery.vue   # 视频画廊
│   │   │   └── VideoPromptForm.vue # 视频表单
│   │   ├── views/         # 页面
│   │   │   ├── ImageGenerator.vue  # 图片生成页
│   │   │   ├── ImageHistory.vue    # 图片历史页
│   │   │   ├── VideoGenerator.vue  # 视频生成页
│   │   │   └── VideoHistory.vue    # 视频历史页
│   │   ├── api/           # API调用
│   │   │   ├── image.js   # 图片API
│   │   │   └── video.js   # 视频API
│   │   └── stores/        # 状态管理
│   │       ├── imageStore.js # 图片状态
│   │       └── videoStore.js # 视频状态
│   └── package.json
├── docs/                  # 文档
│   ├── API接口文档.md
│   └── 部署说明.md
└── CHANGELOG.md           # 更新日志
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

## 功能特性

### 图片生成
- AI图片生成（基于 Doubao-Seedream-5.0-lite 模型）
- 文生图功能：根据文字描述生成图片
- 图生图功能：根据输入图片生成新图片
- 多种尺寸支持（1K/2K/4K/竖图1K/竖图2K）
- 支持批量生成（1-4张）
- 生成历史记录管理
- 图片预览和下载

### 视频生成
- AI视频生成（基于 Doubao-Seedance 2.0 模型）
- 文生视频：根据文字描述生成视频
- 图生视频：根据输入图片生成视频
- 支持多种分辨率（480p/720p/1080p）
- 支持多种宽高比（16:9/4:3/1:1/3:4/9:16/21:9）
- 可调视频时长（2-12秒）
- 自动生成音频
- 视频历史记录管理
- 视频预览和下载

### 通用功能
- 响应式布局
- CORS跨域支持
- 异步任务处理
- 任务状态轮询
- 页面刷新后任务恢复

## 技术栈

- **后端**：Python 3.8+ / FastAPI / volcengine-python-sdk
- **前端**：Vue 3 / Vite / Ant Design Vue / Pinia
- **图片模型**：Doubao-Seedream-5.0-lite（`doubao-seedream-5-0-260128`）
- **视频模型**：Doubao-Seedance 2.0 Pro（`doubao-seedance-2-0-pro-260416`）

## API接口

### 图片接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/images/generate | 生成图片 |
| POST | /api/v1/images/generate-from-image | 图生图 |
| GET | /api/v1/images/{image_id} | 获取图片详情 |
| GET | /api/v1/images/history/list | 获取历史记录 |
| DELETE | /api/v1/images/{image_id} | 删除图片 |
| GET | /api/v1/images/download/{image_id} | 下载图片 |
| DELETE | /api/v1/images/history/clear | 清空历史 |

### 视频接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/videos/generate | 生成视频（文生视频） |
| POST | /api/v1/videos/generate-from-image | 生成视频（图生视频） |
| GET | /api/v1/videos/{video_id} | 获取视频详情 |
| GET | /api/v1/videos/status/{task_id} | 查询任务状态 |
| GET | /api/v1/videos/history/list | 获取视频历史 |
| DELETE | /api/v1/videos/{video_id} | 删除视频 |
| GET | /api/v1/videos/download/{video_id} | 下载视频 |
| DELETE | /api/v1/videos/history/clear | 清空视频历史 |

### 系统接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /health | 健康检查 |
| GET | /api/v1 | API信息 |

## 接口文档

详细接口说明请查看 [API接口文档](./docs/API接口文档.md)，或访问 http://localhost:8886/docs 查看自动生成的 Swagger 文档。

## 更新日志

详细更新记录请查看 [CHANGELOG.md](./CHANGELOG.md)。
