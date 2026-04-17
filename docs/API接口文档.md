# API 接口文档

## 基础信息

- **Base URL**: `http://localhost:8886`
- **API版本**: v1
- **数据格式**: JSON

## 认证

所有API请求无需认证，但请确保 `ARK_API_KEY` 已配置在环境变量中。

---

## 接口列表

## 📸 图片生成接口

### 1. 生成图片（文生图）

生成AI图片。

**请求**

```http
POST /api/v1/images/generate
Content-Type: application/json
```

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| prompt | string | 是 | 图片描述提示词（1-2000字符） |
| size | string | 否 | 图片尺寸：1K/2K/4K/竖图1K/竖图2K（默认2K） |
| n | integer | 否 | 生成数量：1-4（默认1） |
| style | string | 否 | 风格预设 |
| negative_prompt | string | 否 | 负向提示词（最多500字符） |
| watermark | boolean | 否 | 是否添加水印（默认true） |
| response_format | string | 否 | 返回格式：url（默认）/b64_json |

**示例请求**

```json
{
  "prompt": "一只可爱的猫咪在草地上玩耍",
  "size": "2K",
  "n": 1,
  "watermark": true
}
```

**响应**

```json
{
  "success": true,
  "data": [
    {
      "id": "img_20240101_120000_abc12345",
      "url": "https://ark.cn-beijing.volces.com/...",
      "local_path": "generated_images/img_xxx.png",
      "width": 2048,
      "height": 2048,
      "size_bytes": 1048576
    }
  ],
  "message": "Successfully generated 1 images",
  "task_id": "img_20240101_120000_abc12345"
}
```

---

### 2. 生成图片（图生图）

根据输入图片生成新图片。

**请求**

```http
POST /api/v1/images/generate-from-image
Content-Type: application/json
```

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| prompt | string | 是 | 图片描述提示词（1-2000字符） |
| image_url | string | 二选一 | 输入图片URL |
| image_base64 | string | 二选一 | 输入图片base64数据 |
| size | string | 否 | 图片尺寸：1K/2K/4K/竖图1K/竖图2K（默认2K） |
| n | integer | 否 | 生成数量：1-4（默认1） |
| style | string | 否 | 风格预设 |
| negative_prompt | string | 否 | 负向提示词（最多500字符） |
| watermark | boolean | 否 | 是否添加水印（默认true） |
| strength | float | 否 | 生成强度，0-1（默认0.75） |

**示例请求**

```json
{
  "prompt": "将这张图片转换为油画风格",
  "image_url": "https://example.com/image.jpg",
  "size": "2K",
  "watermark": true
}
```

**响应**

```json
{
  "success": true,
  "data": [
    {
      "id": "img_20240101_120000_xyz789",
      "url": "https://ark.cn-beijing.volces.com/...",
      "local_path": "generated_images/img_yyy.png",
      "width": 2048,
      "height": 2048,
      "size_bytes": 1048576
    }
  ],
  "message": "Successfully generated 1 images"
}
```

---

### 3. 获取图片详情

根据图片ID获取详细信息。

**请求**

```http
GET /api/v1/images/{image_id}
```

**路径参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| image_id | string | 是 | 图片ID |

**响应**

```json
{
  "id": "img_20240101_120000_abc12345",
  "prompt": "一只可爱的猫咪在草地上玩耍",
  "size": "2K",
  "style": null,
  "created_at": "2024-01-01T12:00:00",
  "url": "https://ark.cn-beijing.volces.com/...",
  "local_path": "generated_images/img_xxx.png",
  "width": 2048,
  "height": 2048,
  "size_bytes": 1048576
}
```

---

### 4. 获取图片生成历史

获取图片生成历史记录（分页）。

**请求**

```http
GET /api/v1/images/history/list?page=1&page_size=20
```

**查询参数**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | integer | 否 | 1 | 页码 |
| page_size | integer | 否 | 20 | 每页数量（最大100） |

**响应**

```json
{
  "success": true,
  "data": [
    {
      "id": "img_20240101_120000_abc12345",
      "prompt": "一只可爱的猫咪...",
      "size": "2K",
      "thumbnail_url": "https://ark.cn-beijing.volces.com/...",
      "created_at": "2024-01-01T12:00:00",
      "width": 2048,
      "height": 2048
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```

---

### 5. 删除图片

删除指定的图片记录和本地文件。

**请求**

```http
DELETE /api/v1/images/{image_id}
```

**路径参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| image_id | string | 是 | 图片ID |

**响应**

```json
{
  "success": true,
  "message": "Image deleted successfully"
}
```

---

### 6. 下载图片

下载图片到本地。

**请求**

```http
GET /api/v1/images/download/{image_id}
```

**路径参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| image_id | string | 是 | 图片ID |

**响应**

- Content-Type: `image/png`
- Content-Disposition: `attachment; filename="img_xxx.png"`

---

### 7. 获取图片（用于预览）

获取图片内容，可用于前端直接展示。

**请求**

```http
GET /api/v1/images/serve/{image_id}
```

**响应**

- 如果本地存在：返回图片文件（Content-Type: `image/png`）
- 如果只有URL：返回 `{ "url": "..." }`

---

### 8. 清空图片历史

清空所有图片生成历史记录（包括本地图片文件）。

**请求**

```http
DELETE /api/v1/images/history/clear
```

**响应**

```json
{
  "success": true,
  "message": "Cleared 100 records",
  "count": 100
}
```

---

## 🎬 视频生成接口

### 9. 生成视频（文生视频）

使用AI模型根据文本描述生成视频。

**请求**

```http
POST /api/v1/videos/generate
Content-Type: application/json
```

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| prompt | string | 是 | 视频描述提示词（1-2000字符） |
| resolution | string | 否 | 视频分辨率：480p/720p/1080p（默认1080p） |
| aspect_ratio | string | 否 | 宽高比：16:9/4:3/1:1/3:4/9:16/21:9/adaptive（默认16:9） |
| duration | integer | 否 | 视频时长：2-12秒（默认5） |
| watermark | boolean | 否 | 是否添加水印（默认true） |

**示例请求**

```json
{
  "prompt": "一只猫咪在草地上追逐蝴蝶",
  "resolution": "1080p",
  "aspect_ratio": "16:9",
  "duration": 6,
  "watermark": true
}
```

**响应**

```json
{
  "success": true,
  "message": "Video generation task submitted",
  "task_id": "vid_20240101_120000_abc12345"
}
```

---

### 10. 生成视频（图生视频）

根据输入图片生成视频。

**请求**

```http
POST /api/v1/videos/generate-from-image
Content-Type: application/json
```

**请求参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| prompt | string | 是 | 视频描述提示词（1-2000字符） |
| image_url | string | 二选一 | 输入图片URL |
| image_base64 | string | 二选一 | 输入图片base64数据 |
| resolution | string | 否 | 视频分辨率：480p/720p/1080p（默认1080p） |
| aspect_ratio | string | 否 | 宽高比：16:9/4:3/1:1/3:4/9:16/21:9/adaptive（默认16:9） |
| duration | integer | 否 | 视频时长：2-12秒（默认5） |
| watermark | boolean | 否 | 是否添加水印（默认true） |

**示例请求**

```json
{
  "prompt": "让这张图片动起来",
  "image_url": "https://example.com/image.jpg",
  "resolution": "720p",
  "aspect_ratio": "9:16",
  "duration": 8
}
```

**响应**

```json
{
  "success": true,
  "message": "Video generation task submitted",
  "task_id": "vid_20240101_120000_xyz789"
}
```

---

### 11. 查询视频生成任务状态

查询异步视频生成任务的状态。

**请求**

```http
GET /api/v1/videos/status/{task_id}
```

**路径参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| task_id | string | 是 | 任务ID |

**响应**

```json
{
  "task_id": "vid_20240101_120000_abc12345",
  "status": "succeeded",  // pending/running/succeeded/failed/not_found
  "progress": 100,
  "video_url": "https://...",
  "message": "Video generation completed"
}
```

**状态说明**
- `pending`：任务已提交，等待处理
- `running`：任务正在生成中
- `succeeded`：生成成功
- `failed`：生成失败
- `not_found`：任务不存在

---

### 12. 获取视频详情

根据视频ID获取详细信息。

**请求**

```http
GET /api/v1/videos/{video_id}
```

**路径参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| video_id | string | 是 | 视频ID |

**响应**

```json
{
  "id": "vid_20240101_120000_abc12345",
  "prompt": "一只猫咪在草地上追逐蝴蝶",
  "resolution": "1080p",
  "aspect_ratio": "16:9",
  "duration": 6,
  "created_at": "2024-01-01T12:00:00",
  "url": "https://ark.cn-beijing.volces.com/...",
  "local_path": "generated_videos/vid_xxx.mp4",
  "width": 1920,
  "height": 1080,
  "size_bytes": 5242880
}
```

---

### 13. 获取视频生成历史

获取视频生成历史记录（分页）。

**请求**

```http
GET /api/v1/videos/history/list?page=1&page_size=20
```

**查询参数**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | integer | 否 | 1 | 页码 |
| page_size | integer | 否 | 20 | 每页数量（最大100） |

**响应**

```json
{
  "success": true,
  "data": [
    {
      "id": "vid_20240101_120000_abc12345",
      "prompt": "一只猫咪在草地上追逐蝴蝶",
      "resolution": "1080p",
      "aspect_ratio": "16:9",
      "duration": 6,
      "thumbnail_url": "https://...",
      "created_at": "2024-01-01T12:00:00",
      "width": 1920,
      "height": 1080
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 20
}
```

---

### 14. 下载视频

下载视频到本地。

**请求**

```http
GET /api/v1/videos/download/{video_id}
```

**路径参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| video_id | string | 是 | 视频ID |

**响应**

- Content-Type: `video/mp4`
- Content-Disposition: `attachment; filename="vid_xxx.mp4"`

---

### 15. 获取视频（用于播放）

获取视频内容，可用于前端直接播放。

**请求**

```http
GET /api/v1/videos/serve/{video_id}
```

**响应**

```json
{
  "url": "https://..."
}
```

---

### 16. 删除视频

删除指定的视频记录和本地文件。

**请求**

```http
DELETE /api/v1/videos/{video_id}
```

**路径参数**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| video_id | string | 是 | 视频ID |

**响应**

```json
{
  "success": true,
  "message": "Video deleted successfully"
}
```

---

### 17. 清空视频历史

清空所有视频生成历史记录（包括本地视频文件）。

**请求**

```http
DELETE /api/v1/videos/history/clear
```

**响应**

```json
{
  "success": true,
  "message": "Cleared 100 records",
  "count": 100
}
```

---

## 🔧 系统接口

### 18. 健康检查

检查服务运行状态。

**请求**

```http
GET /health
```

**响应**

```json
{
  "status": "healthy",
  "version": "2.0.0",
  "api_key_configured": true,
  "image_count": 100,
  "video_count": 50
}
```

---

### 19. API信息

获取API版本和端点信息。

**请求**

```http
GET /api/v1
```

**响应**

```json
{
  "version": "v1",
  "features": ["image-generation", "video-generation"],
  "endpoints": {
    "images": {
      "generate": "/api/v1/images/generate",
      "generate-from-image": "/api/v1/images/generate-from-image",
      "history": "/api/v1/images/history/list",
      "download": "/api/v1/images/download/{image_id}"
    },
    "videos": {
      "generate": "/api/v1/videos/generate",
      "generate-from-image": "/api/v1/videos/generate-from-image",
      "status": "/api/v1/videos/status/{task_id}",
      "history": "/api/v1/videos/history/list",
      "download": "/api/v1/videos/download/{video_id}"
    }
  }
}
```

---

## 错误响应

所有接口的错误响应格式：

```json
{
  "success": false,
  "error": "错误描述",
  "error_code": "ERROR_CODE",
  "detail": "详细错误信息"
}
```

### 常见错误码

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
| 503 | API服务不可用 |

---

## 请求示例（cURL）

### 生成图片

```bash
curl -X POST http://localhost:8886/api/v1/images/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "奇幻风格的魔法世界",
    "size": "2K",
    "n": 1
  }'
```

### 图生图

```bash
curl -X POST http://localhost:8886/api/v1/images/generate-from-image \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "转换为油画风格",
    "image_url": "https://example.com/image.jpg",
    "size": "2K"
  }'
```

### 生成视频

```bash
curl -X POST http://localhost:8886/api/v1/videos/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "一只猫咪在草地上追逐蝴蝶",
    "resolution": "1080p",
    "aspect_ratio": "16:9",
    "duration": 6
  }'
```

### 查询任务状态

```bash
curl http://localhost:8886/api/v1/videos/status/vid_20240101_120000_abc12345
```

### 获取图片历史

```bash
curl http://localhost:8886/api/v1/images/history/list?page=1
```

### 删除图片

```bash
curl -X DELETE http://localhost:8886/api/v1/images/img_xxx
```

---

## 技术信息

- **图片模型**: `doubao-seedream-5-0-260128`（Doubao-Seedream-5.0-lite）
- **视频模型**: `doubao-seedance-2-0-pro-260416`（Doubao-Seedance 2.0 Pro）
- **API Endpoint**: `https://ark.cn-beijing.volces.com/api/v3`
- **默认端口**: 8886
- **图片存储**: `./generated_images/` 目录
- **视频存储**: `./generated_videos/` 目录

## Web界面

访问 http://localhost:8886/docs 查看自动生成的 Swagger 文档。
