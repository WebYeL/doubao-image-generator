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

---

## 开源协作

我们非常欢迎社区贡献！本项目采用 PR（Pull Request）协作模式，所有代码变更必须通过 PR 提交并由维护者审核后方可合并。

### 如何贡献

#### 1. Fork 本仓库

点击 GitHub 仓库页面的 "Fork" 按钮，将仓库复制到您的 GitHub 账号。

#### 2. 克隆到本地

```bash
git clone https://github.com/您的用户名/doubao-image-generator.git
cd doubao-image-generator
```

#### 3. 创建功能分支

```bash
git checkout -b feat/你的功能名称
# 或
git checkout -b fix/问题描述
```

**分支命名规范：**
- 新功能：`feat/功能描述`
- 问题修复：`fix/问题描述`
- 文档更新：`docs/文档描述`
- 重构：`refactor/重构描述`

#### 4. 提交代码

```bash
git add .
git commit -m "feat: 添加新功能"
```

**提交信息规范：**
- 使用中文或英文清晰描述
- 建议采用 Conventional Commits 格式：
  - `feat:` 新功能
  - `fix:` 问题修复
  - `docs:` 文档更新
  - `style:` 代码格式（不影响功能）
  - `refactor:` 重构
  - `test:` 测试
  - `chore:` 构建或辅助工具变动

示例：
```bash
git commit -m "feat: 新增视频水印配置选项"
git commit -m "fix: 修复视频下载失败的问题"
```

#### 5. 推送到您的 Fork

```bash
git push origin feat/你的功能名称
```

#### 6. 创建 Pull Request

1. 访问原仓库：https://github.com/WebYeL/doubao-image-generator
2. 点击 "New Pull Request"
3. 选择您的分支与原仓库的 `master` 分支
4. 填写 PR 标题和详细描述：
   - 说明做了什么变更
   - 关联的相关 Issue（如有）
   - 测试情况
5. 提交 PR，等待审核

### PR 审核流程

1. **维护者收到 PR 后会进行代码审查**
   - 检查代码质量和风格
   - 验证功能是否正常工作
   - 评估是否与项目目标一致

2. **可能需要修改**
   - 维护者会提出修改建议
   - 请在原分支修改并重新推送，PR 会自动更新

3. **审核通过后合并**
   - 维护者会将 PR 合并到 `master` 分支
   - 您将成为本次贡献的贡献者

### 开发建议

#### 代码规范

**后端（Python）：**
- 遵循 PEP 8 规范
- 使用类型提示（Type Hints）
- 添加必要的文档字符串
- 异常处理要完整

**前端（Vue 3）：**
- 使用 Composition API
- 遵循 Vue 3 最佳实践
- 组件命名使用 PascalCase
- 保持组件单一职责

#### 测试

- 新功能请尽量添加单元测试
- 确保现有测试通过
- 手动测试主要功能路径

#### 文档

- 更新相关文档（README、API文档等）
- 代码注释要清晰
- 更新 CHANGELOG.md（可在 PR 中由维护者统一更新）

### Issue 反馈

如果您发现问题或有功能建议，请先创建 Issue：

1. 搜索是否已存在相关 Issue
2. 使用模板创建新 Issue
3. 清晰描述问题或需求
4. 提供必要的上下文（截图、日志等）

### 行为准则

- 尊重所有社区成员
- 提供建设性反馈
- 接受合理的批评和建议
- 共同维护良好的开源氛围

### 许可证

本项目采用开源许可证，详情请查看 `LICENSE` 文件（如有）。贡献代码即表示您同意您的代码将根据项目许可证进行分发。

---

感谢您的贡献！🎉
