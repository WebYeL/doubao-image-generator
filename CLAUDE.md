# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## 项目概述

Doubao 图片生成器 - 基于 Doubao-Seedream-5.0-lite 的 AI 图片生成应用。

## 技术栈

- **后端**: Python 3.8+ / FastAPI / volcengine-python-sdk
- **前端**: Vue 3 / Vite / Ant Design Vue / Pinia
- **AI模型**: Doubao-Seedream-5.0-lite (`doubao-seedream-5-0-260128`)

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
│   │       ├── image_service.py  # 图片生成服务
│   │       └── storage.py   # 存储服务
│   ├── requirements.txt    # Python依赖
│   └── .env                # 环境变量（API密钥）
├── frontend/               # Vue 3 + Ant Design 前端
│   ├── src/
│   │   ├── components/     # 组件
│   │   ├── views/          # 页面
│   │   ├── api/            # API调用
│   │   ├── stores/         # Pinia 状态管理
│   │   └── utils/          # 工具函数
│   └── package.json
└── scripts/                # 启动脚本
```

## 常用命令

### 后端
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8886 --reload
```

### 前端
```bash
cd frontend
npm install
npm run dev    # 开发模式
npm run build  # 构建
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/images/generate | 生成图片 |
| GET | /api/v1/images/history/list | 获取历史记录 |
| GET | /api/v1/images/{image_id} | 获取图片详情 |
| DELETE | /api/v1/images/{image_id} | 删除图片 |
| GET | /api/v1/images/download/{image_id} | 下载图片 |
| DELETE | /api/v1/images/history/clear | 清空历史 |
| GET | /health | 健康检查 |

访问 http://localhost:8886/docs 查看 Swagger 文档。

## 配置说明

后端需要配置 `ARK_API_KEY`（火山引擎 API 密钥），位于 `backend/.env` 文件中。

## 功能特性

- AI 图片生成（支持 1K/2K/4K/竖图等多种尺寸）
- 支持批量生成（1-4张）
- 生成历史记录管理
- 图片预览和下载
- 响应式布局
