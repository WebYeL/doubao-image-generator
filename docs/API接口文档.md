# API 接口文档

## 基础信息

- **Base URL**: `http://localhost:8886`
- **API版本**: v1
- **数据格式**: JSON

## 认证

所有API请求无需认证，但请确保 `ARK_API_KEY` 已配置在环境变量中。

---

## 接口列表

### 1. 生成图片

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
| negative_prompt | string | 否 | 负向提示词，不希望出现的元素（最多500字符） |
| watermark | boolean | 否 | 是否添加水印（默认true） |
| response_format | string | 否 | 返回格式：url（默认）/ b64_json |

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

### 2. 获取图片详情

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

### 3. 获取生成历史

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

### 4. 删除图片

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

### 5. 下载图片

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

### 6. 获取图片（用于预览）

获取图片内容，可用于前端直接展示。

**请求**

```http
GET /api/v1/images/serve/{image_id}
```

**响应**

- 如果本地存在：返回图片文件（Content-Type: `image/png`）
- 如果只有URL：返回 `{ "url": "..." }`

---

### 7. 清空历史

清空所有生成历史记录（包括本地图片文件）。

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

### 8. 健康检查

检查服务运行状态。

**请求**

```http
GET /health
```

**响应**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "api_key_configured": true
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

### 获取历史

```bash
curl http://localhost:8886/api/v1/images/history/list?page=1
```

### 删除图片

```bash
curl -X DELETE http://localhost:8886/api/v1/images/img_xxx
```

---

## 技术信息

- **AI模型**: `doubao-seedream-5-0-260128`（Doubao-Seedream-5.0-lite）
- **API Endpoint**: `https://ark.cn-beijing.volces.com/api/v3`
- **默认端口**: 8886
- **图片存储**: `./generated_images/` 目录

## Web界面

访问 http://localhost:8886/docs 查看自动生成的 Swagger 文档。
