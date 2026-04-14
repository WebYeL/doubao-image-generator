<template>
  <div class="page-container">
    <a-layout>
      <!-- 顶部导航 -->
      <a-layout-header class="header">
        <div class="header-content">
          <div class="logo">
            <ThunderboltOutlined class="logo-icon" />
            <span>Doubao 图片生成器</span>
          </div>
          <div class="header-actions">
            <a-space>
              <a-button type="primary" ghost @click="$router.push('/history')">
                <template #icon><HistoryOutlined /></template>
                历史记录
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
            <ImagePromptForm
              ref="promptFormRef"
              :generating="imageStore.generating"
              @submit="handleGenerate"
              @clear="handleClear"
            />
          </div>

          <!-- 右侧：结果展示 -->
          <div class="result-section">
            <a-card title="生成结果" class="result-card">
              <template #extra>
                <a-button
                  v-if="imageStore.currentImages.length > 0"
                  type="text"
                  danger
                  size="small"
                  @click="handleClearImages"
                >
                  清空结果
                </a-button>
              </template>

              <!-- 加载状态 -->
              <div v-if="imageStore.generating" class="generating-status">
                <a-spin size="large" />
                <p class="status-text">{{ imageStore.generatingMessage }}</p>
              </div>

              <!-- 错误提示 -->
              <a-alert
                v-else-if="imageStore.error"
                type="error"
                show-icon
                closable
                @close="imageStore.clearError"
                class="error-alert"
              >
                <template #message>生成失败</template>
                <template #description>{{ imageStore.error }}</template>
              </a-alert>

              <!-- 图片画廊 -->
              <ImageGallery
                v-else
                :images="imageStore.currentImages"
                @delete="handleDeleteImage"
                @download="handleDownload"
              />
            </a-card>
          </div>
        </div>
      </a-layout-content>

      <!-- 页脚 -->
      <a-layout-footer class="footer">
        <span>Doubao Image Generator v1.0.0</span>
      </a-layout-footer>
    </a-layout>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import {
  ThunderboltOutlined,
  HistoryOutlined
} from '@ant-design/icons-vue'
import { useImageStore } from '@/stores/imageStore'
import ImagePromptForm from '@/components/ImagePromptForm.vue'
import ImageGallery from '@/components/ImageGallery.vue'

const router = useRouter()
const imageStore = useImageStore()
const promptFormRef = ref(null)

const handleGenerate = async (params) => {
  const result = await imageStore.generateImages(params)

  if (result.success) {
    message.success(`成功生成 ${result.data.length} 张图片`)
  } else {
    message.error(result.error || '生成失败')
  }
}

const handleClear = () => {
  imageStore.clearCurrentImages()
}

const handleClearImages = () => {
  Modal.confirm({
    title: '确认清空',
    content: '确定要清空当前所有生成结果吗？',
    okText: '确认',
    cancelText: '取消',
    onOk() {
      imageStore.clearCurrentImages()
      message.success('已清空')
    }
  })
}

const handleDeleteImage = async (image) => {
  const result = await imageStore.deleteImage(image.id)

  if (result.success) {
    message.success('图片已删除')
  } else {
    message.error(result.error || '删除失败')
  }
}

const handleDownload = (image) => {
  message.success('开始下载')
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
