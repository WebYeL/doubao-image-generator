<template>
  <div class="page-container">
    <a-layout>
      <!-- 顶部导航 -->
      <a-layout-header class="header">
        <div class="header-content">
          <div class="logo">
            <VideoCameraOutlined class="logo-icon" />
            <span>视频生成历史</span>
          </div>
          <div class="header-actions">
            <a-space>
              <a-button type="primary" ghost @click="$router.push('/')">
                <template #icon><HomeOutlined /></template>
                返回首页
              </a-button>
            </a-space>
          </div>
        </div>
      </a-layout-header>

      <!-- 主内容 -->
      <a-layout-content class="main-content">
        <a-card>
          <template #title>
            <div class="card-title">
              <span>视频历史记录</span>
              <a-space>
                <a-button
                  type="primary"
                  danger
                  size="small"
                  @click="handleClearHistory"
                  :loading="clearing"
                >
                  清空全部
                </a-button>
              </a-space>
            </div>
          </template>

          <!-- 加载状态 -->
          <a-spin v-if="loading" size="large" />

          <!-- 空状态 -->
          <a-empty v-else-if="!videoStore.history.length" :image="Empty.PRESENTED_IMAGE_SIMPLE">
            <template #description>
              <span class="empty-text">暂无视频历史记录</span>
            </template>
          </a-empty>

          <!-- 视频列表 -->
          <div v-else class="video-list">
            <div
              v-for="video in videoStore.history"
              :key="video.id"
              class="video-item"
            >
              <div class="video-thumb">
                <video
                  :src="getVideoSrc(video)"
                  controls
                  preload="metadata"
                  @error="handleThumbError"
                >
                  您的浏览器不支持视频播放
                </video>
              </div>
              <div class="video-info">
                <div class="video-prompt">{{ video.prompt }}</div>
                <div class="video-meta">
                  <a-tag color="blue">{{ video.resolution }}</a-tag>
                  <a-tag color="green">{{ video.aspect_ratio }}</a-tag>
                  <span class="video-duration">{{ video.duration }}秒</span>
                  <span class="video-date">{{ formatDate(video.created_at) }}</span>
                </div>
              </div>
              <div class="video-actions">
                <a-space>
                  <a-tooltip title="播放">
                    <a-button type="text" @click="handlePreview(video)">
                      <PlayCircleOutlined />
                    </a-button>
                  </a-tooltip>
                  <a-tooltip title="下载">
                    <a-button type="text" @click="handleDownload(video)">
                      <DownloadOutlined />
                    </a-button>
                  </a-tooltip>
                  <a-tooltip title="删除">
                    <a-button type="text" danger @click="handleDelete(video)">
                      <DeleteOutlined />
                    </a-button>
                  </a-tooltip>
                </a-space>
              </div>
            </div>

            <!-- 分页 -->
            <div class="pagination-wrapper">
              <a-pagination
                v-model:current="currentPage"
                :total="videoStore.historyTotal"
                :page-size="20"
                show-quick-jumper
                @change="handlePageChange"
              />
            </div>
          </div>
        </a-card>
      </a-layout-content>

      <!-- 页脚 -->
      <a-layout-footer class="footer">
        <span>Doubao Video Generator v2.0.0</span>
      </a-layout-footer>
    </a-layout>

    <!-- 预览弹窗 -->
    <a-modal
      v-model:open="previewVisible"
      title="视频预览"
      :footer="null"
      width="900px"
      centered
    >
      <video
        v-if="previewVisible"
        :src="previewUrl"
        controls
        autoplay
        class="preview-video"
      >
        您的浏览器不支持视频播放
      </video>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import { Empty } from 'ant-design-vue'
import {
  HomeOutlined,
  VideoCameraOutlined,
  PlayCircleOutlined,
  DownloadOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue'
import { useVideoStore } from '@/stores/videoStore'
import { downloadVideo as getDownloadUrl, serveVideo as getServeUrl } from '@/api/video'

const router = useRouter()
const videoStore = useVideoStore()

const loading = ref(false)
const clearing = ref(false)
const currentPage = ref(1)
const previewVisible = ref(false)
const previewUrl = ref('')

onMounted(() => {
  loadHistory()
})

const loadHistory = async () => {
  loading.value = true
  await videoStore.loadHistory(currentPage.value)
  loading.value = false
}

const getVideoSrc = (video) => {
  // 优先使用 URL 字段
  if (video.url) {
    return video.url
  }
  // 如果有本地路径，通过后端服务获取
  if (video.local_path) {
    return getServeUrl(video.id)
  }
  // 兜底：使用 thumbnail_url
  if (video.thumbnail_url) {
    return video.thumbnail_url
  }
  return ''
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  try {
    // 处理 ISO 格式
    if (typeof dateStr === 'string' && dateStr.includes('T')) {
      const date = new Date(dateStr.replace('T', ' ').replace(/\.\d+/, ''))
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
    // 处理时间戳
    if (typeof dateStr === 'number' || (typeof dateStr === 'string' && /^\d+$/.test(dateStr))) {
      const date = new Date(parseInt(dateStr) * (dateStr > 1e10 ? 1 : 1000))
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
    const date = new Date(dateStr)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (e) {
    return String(dateStr)
  }
}

const handleThumbError = (e) => {
  console.error('Video load error:', e)
  e.target.style.display = 'none'
}

const handlePreview = (video) => {
  previewUrl.value = getVideoSrc(video)
  previewVisible.value = true
}

const handleDownload = (video) => {
  const url = video.url || getDownloadUrl(video.id)
  if (!url) {
    message.error('视频地址无效')
    return
  }

  const link = document.createElement('a')
  link.href = url
  link.download = `doubao_video_${video.id}.mp4`
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)

  message.success('开始下载')
}

const handleDelete = (video) => {
  Modal.confirm({
    title: '确认删除',
    content: '确定要删除这个视频吗？',
    okText: '确认',
    cancelText: '取消',
    onOk: async () => {
      const result = await videoStore.deleteVideo(video.id)
      if (result.success) {
        message.success('视频已删除')
      } else {
        message.error(result.error || '删除失败')
      }
    }
  })
}

const handleClearHistory = () => {
  Modal.confirm({
    title: '确认清空',
    content: '确定要清空所有视频历史记录吗？此操作不可恢复。',
    okText: '确认',
    cancelText: '取消',
    okType: 'danger',
    onOk: async () => {
      clearing.value = true
      const result = await videoStore.clearHistory()
      clearing.value = false

      if (result.success) {
        message.success(`已清空 ${result.count} 条记录`)
      } else {
        message.error(result.error || '清空失败')
      }
    }
  })
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadHistory()
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
}

.header {
  background: linear-gradient(135deg, #f759ab 0%, #ab8bff 100%);
  padding: 0 24px;
  height: 64px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  max-width: 1400px;
  margin: 0 auto;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  color: white;
  font-size: 20px;
  font-weight: 600;
}

.logo-icon {
  font-size: 28px;
}

.main-content {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.card-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-text {
  color: #999;
}

.video-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.video-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  background: #fafafa;
  border-radius: 8px;
  transition: background 0.3s;
}

.video-item:hover {
  background: #f0f0f0;
}

.video-thumb {
  width: 120px;
  height: 80px;
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
  background: #000;
}

.video-thumb video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-info {
  flex: 1;
  min-width: 0;
}

.video-prompt {
  font-size: 14px;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 8px;
}

.video-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #999;
}

.video-duration {
  margin-left: 8px;
}

.video-date {
  color: #999;
}

.video-actions {
  display: flex;
  gap: 8px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.preview-video {
  width: 100%;
  max-height: 600px;
  object-fit: contain;
}

.footer {
  text-align: center;
  color: #999;
  font-size: 12px;
  padding: 16px;
}
</style>
