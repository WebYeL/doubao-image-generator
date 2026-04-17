# 更新日志

所有重要的项目更新都将记录在此文件中。

## [2.0.0] - 2026-04-16

### 重大更新
- **新增视频生成功能**：集成豆包 Seedance 1.0 Pro Fast 模型，支持文生视频和图生视频
- **版本升级**：应用版本从 1.x 升级到 2.0.0

### 后端新增

#### API 接口
- 新增视频生成 API（`/api/v1/videos/generate`）：文生视频
- 新增图生视频 API（`/api/v1/videos/generate-from-image`）：根据图片生成视频
- 新增视频状态查询 API（`/api/v1/videos/status/{task_id}`）：查询异步任务状态
- 新增视频历史 API（`/api/v1/videos/history/list`）：获取视频生成历史
- 新增视频下载 API（`/api/v1/videos/download/{video_id}`）：下载视频文件
- 新增视频删除 API（`/api/v1/videos/{video_id}`）：删除指定视频
- 新增视频播放 API（`/api/v1/videos/serve/{video_id}`）：获取视频播放地址

#### 服务层
- 新增 `video_service.py`：视频生成服务，支持异步任务处理
- 扩展 `storage.py`：新增 `VideoHistoryStorage` 类，实现视频历史持久化存储
- 更新 `config.py`：添加视频相关配置项
  - `VIDEO_MODEL_NAME`：视频模型名称
  - `VIDEO_STORAGE_PATH`：视频存储路径
  - `VIDEO_POLL_INTERVAL`：轮询间隔（秒）
  - `VIDEO_MAX_POLL_TIME`：最大轮询时间（秒）

#### 模型
- 新增视频相关 Pydantic 模型：
  - `VideoGenerateRequest`：视频生成请求
  - `VideoFromImageRequest`：图生视频请求
  - `VideoGenerateResponse`：视频生成响应
  - `VideoInfo`：视频信息
  - `VideoData`：视频数据
  - `VideoHistoryItem`：历史记录项
  - `VideoTaskStatusResponse`：任务状态响应
  - `VideoResolution` 和 `VideoAspectRatio`：枚举类型

### 前端新增

#### 页面
- 新增视频生成页面（`/video`）：提供文生视频和图生视频功能
- 新增视频历史页面（`/video-history`）：管理视频生成历史

#### 组件
- 新增 `VideoPromptForm.vue`：视频生成表单组件
- 新增 `VideoGallery.vue`：视频展示画廊组件

#### 状态管理
- 新增 `videoStore.js`：视频相关的 Pinia 状态管理
  - 轮询任务状态（每5秒查询）
  - 保存轮询状态到 localStorage（页面刷新恢复）
  - 视频历史管理

#### API 调用
- 新增 `video.js`：视频相关的 API 调用封装

#### 路由
- 新增 `/video` 路由：视频生成器页面
- 新增 `/video-history` 路由：视频历史页面

### 配置更新
- 更新 `.env.production`：添加视频相关配置
- 版本号更新：`1.x` -> `2.0.0`

---

## [1.1.0] - 2026-04-16

### 新增
- 添加生产环境配置文件 `.env.production`，包含完整的服务器配置
- 新增 CORS 跨域配置，支持多个域名访问

### 依赖更新
- 新增 `volcengine-python-sdk>=4.0.14` 依赖，用于火山引擎 SDK 支持

---

## [1.0.0] - 初始版本

### 功能
- 基于 Doubao-Seedream-5.0-lite 的 AI 图片生成应用
- 支持文生图和图生图功能
- 后端使用 FastAPI + Python
- 前端使用 Vue 3 + Ant Design Vue
- 支持多种图片尺寸（1K/2K/4K/竖图）
- 生成历史记录管理
- 图片预览和下载功能
