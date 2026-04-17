<template>
  <div class="page-container">
    <a-layout>
      <!-- 顶部导航 -->
      <a-layout-header class="header">
        <div class="header-content">
          <div class="logo">
            <VideoCameraAddOutlined class="logo-icon" />
            <span>Doubao 视频生成器</span>
          </div>
          <div class="header-actions">
            <a-space>
              <a-button type="primary" ghost @click="$router.push('/history')">
                <template #icon><HistoryOutlined /></template>
                图片历史
              </a-button>
              <a-button type="primary" ghost @click="$router.push('/video-history')">
                <template #icon><VideoCameraOutlined /></template>
                视频历史
              </a-button>
            </a-space>
          </div>
        </div>
      </a-layout-header>

      <!-- 主内容 -->
      <a-layout-content class="main-content">
        <div class="content-grid">
          <!-- 左侧：表单 -->
          <div class="form-section">
            <VideoPromptForm
              ref="promptFormRef"
              :generating="videoStore.generating"
              @submit="handleGenerate"
              @clear="handleClear"
            />
          </div>

          <!-- 右侧：结果展示 -->
          <div class="result-section">
            <a-card title="生成结果" class="result-card">
              <template #extra>
                <a-button
                  v-if="videoStore.currentVideo"
                  type="text"
                  danger
                  size="small"
                  @click="handleClearVideo"
                >
                  清空结果
                </a-button>
              </template>

              <!-- 加载状态 -->
              <div v-if="videoStore.generating" class="generating-status">
                <a-spin size="large" />
                <p class="status-text">{{ videoStore.generatingMessage }}</p>
                <a-progress
                  :percent="progressPercent"
                  status="active"
                  :stroke-width="8"
                  size="small"
                />
              </div>

              <!-- 错误提示 -->
              <a-alert
                v-else-if="videoStore.error"
                type="error"
                show-icon
                closable
                @close="videoStore.clearError"
                class="error-alert"
              >
                <template #message>生成失败</template>
                <template #description>{{ videoStore.error }}</template>
              </a-alert>

              <!-- 视频画廊 -->
              <VideoGallery
                v-else
                :video="videoStore.currentVideo"
                @delete="handleDeleteVideo"
                @download="handleDownload"
              />
            </a-card>
          </div>
        </div>
      </a-layout-content>

      <!-- 页脚 -->
      <a-layout-footer class="footer">
        <span>Doubao Video Generator v2.0.0</span>
      </a-layout-footer>
    </a-layout>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import {
  VideoCameraAddOutlined,
  HistoryOutlined,
  VideoCameraOutlined
} from '@ant-design/icons-vue'
import { useVideoStore } from '@/stores/videoStore'
import VideoPromptForm from '@/components/VideoPromptForm.vue'
import VideoGallery from '@/components/VideoGallery.vue'

const router = useRouter()
const videoStore = useVideoStore()
const promptFormRef = ref(null)
const progressPercent = ref(0)
let progressTimer = null

onMounted(() => {
  // 恢复之前的轮询任务（页面刷新后）
  videoStore.restorePolling()
})

const handleGenerate = async (params) => {
  // 判断是否是图生视频请求
  const hasImageInput = params.image_url || params.image_base64

  // 开始进度动画
  progressPercent.value = 0
  startProgressAnimation()

  let result
  if (hasImageInput) {
    result = await videoStore.generateVideoFromImage(params)
  } else {
    result = await videoStore.generateVideo(params)
  }

  // 停止进度动画（但保持generating状态，等待轮询完成）
  stopProgressAnimation()

  if (result.success) {
    // 任务已提交，轮询中...
    message.success('任务已提交，开始生成视频')
  } else {
    videoStore.generating = false
    message.error(result.error || '提交失败')
  }
}

const startProgressAnimation = () => {
  progressTimer = setInterval(() => {
    if (progressPercent.value < 90) {
      progressPercent.value += Math.random() * 5
    }
  }, 1000)
}

const stopProgressAnimation = () => {
  if (progressTimer) {
    clearInterval(progressTimer)
    progressTimer = null
  }
}

const handleClear = () => {
  videoStore.clearCurrentVideo()
  progressPercent.value = 0
}

const handleClearVideo = () => {
  Modal.confirm({
    title: '确认清空',
    content: '确定要清空当前生成的视频吗？',
    okText: '确认',
    cancelText: '取消',
    onOk() {
      videoStore.clearCurrentVideo()
      message.success('已清空')
    }
  })
}

const handleDeleteVideo = async (video) => {
  const result = await videoStore.deleteVideo(video.id)

  if (result.success) {
    message.success('视频已删除')
  } else {
    message.error(result.error || '删除失败')
  }
}

const handleDownload = (video) => {
  message.success('开始下载')
}

onUnmounted(() => {
  stopProgressAnimation()
  videoStore.stopPolling()
})
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

.content-grid {
  display: grid;
  grid-template-columns: 450px 1fr;
  gap: 24px;
  min-height: calc(100vh - 180px);
}

.form-section {
  height: fit-content;
  position: sticky;
  top: 24px;
}

.result-section {
  min-height: 500px;
}

.result-card {
  min-height: 500px;
}

.generating-status {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  gap: 16px;
}

.status-text {
  color: #666;
  font-size: 16px;
}

.error-alert {
  margin-bottom: 16px;
}

.footer {
  text-align: center;
  color: #999;
  font-size: 12px;
  padding: 16px;
}

/* 响应式布局 */
@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .form-section {
    position: static;
  }
}
</style>
