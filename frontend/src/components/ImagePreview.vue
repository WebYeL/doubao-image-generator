<template>
  <a-modal
    :open="visible"
    :footer="null"
    :width="800"
    :centered="true"
    @cancel="handleClose"
    class="image-preview-modal"
  >
    <template #title>
      <span>图片预览</span>
    </template>

    <div class="preview-container" v-if="image">
      <div class="preview-main">
        <div class="preview-image-wrapper">
          <img
            :src="getImageSrc()"
            :alt="image.id"
            @error="handleImageError"
          />
        </div>

        <!-- 导航按钮 -->
        <div class="preview-nav" v-if="images && images.length > 1">
          <a-button
            class="nav-btn prev-btn"
            :disabled="currentIndex <= 0"
            @click="$emit('prev')"
          >
            <LeftOutlined />
          </a-button>
          <span class="nav-indicator">
            {{ currentIndex + 1 }} / {{ images.length }}
          </span>
          <a-button
            class="nav-btn next-btn"
            :disabled="currentIndex >= images.length - 1"
            @click="$emit('next')"
          >
            <RightOutlined />
          </a-button>
        </div>
      </div>

      <div class="preview-info">
        <a-descriptions :column="1" size="small">
          <a-descriptions-item label="图片ID">
            <span class="info-value">{{ image.id }}</span>
          </a-descriptions-item>
          <a-descriptions-item label="尺寸">
            <span class="info-value">{{ image.width }} × {{ image.height }}</span>
          </a-descriptions-item>
          <a-descriptions-item label="文件大小">
            <span class="info-value">{{ formatSize(image.size_bytes) }}</span>
          </a-descriptions-item>
          <a-descriptions-item label="状态">
            <a-tag :color="image.local_path ? 'green' : 'orange'">
              {{ image.local_path ? '已下载' : '仅URL' }}
            </a-tag>
          </a-descriptions-item>
        </a-descriptions>

        <div class="preview-actions">
          <a-space>
            <a-button type="primary" @click="handleDownload">
              <template #icon><DownloadOutlined /></template>
              下载
            </a-button>
            <a-button @click="handleCopyLink">
              <template #icon><CopyOutlined /></template>
              复制链接
            </a-button>
            <a-button danger @click="handleDelete">
              <template #icon><DeleteOutlined /></template>
              删除
            </a-button>
          </a-space>
        </div>
      </div>
    </div>
  </a-modal>
</template>

<script setup>
import { computed } from 'vue'
import { message } from 'ant-design-vue'
import {
  LeftOutlined,
  RightOutlined,
  DownloadOutlined,
  CopyOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue'
import { downloadImage as getDownloadUrl } from '@/api/image'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  image: {
    type: Object,
    default: null
  },
  images: {
    type: Array,
    default: () => []
  },
  currentIndex: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['update:visible', 'prev', 'next', 'delete', 'download'])

const getImageSrc = () => {
  if (!props.image) return ''
  if (props.image.local_path) {
    return `/api/v1/images/serve/${props.image.id}`
  }
  return props.image.url || ''
}

const handleImageError = (e) => {
  e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23f0f0f0" width="200" height="200"/%3E%3Ctext fill="%23999" font-size="14" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3E图片加载失败%3C/text%3E%3C/svg%3E'
}

const formatSize = (bytes) => {
  if (!bytes) return '未知'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

const handleClose = () => {
  emit('update:visible', false)
}

const handleDownload = () => {
  const url = props.image.local_path ? getDownloadUrl(props.image.id) : props.image.url
  if (!url) {
    message.error('图片地址无效')
    return
  }

  const link = document.createElement('a')
  link.href = url
  link.download = `doubao_${props.image.id}.png`
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)

  emit('download', props.image)
}

const handleCopyLink = () => {
  const url = props.image.url || props.image.local_path
  if (url) {
    navigator.clipboard.writeText(url).then(() => {
      message.success('链接已复制到剪贴板')
    }).catch(() => {
      message.error('复制失败')
    })
  }
}

const handleDelete = () => {
  emit('delete', props.image)
  emit('update:visible', false)
}
</script>

<style scoped>
.preview-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.preview-main {
  position: relative;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}

.preview-image-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  max-height: 60vh;
  overflow: hidden;
}

.preview-image-wrapper img {
  max-width: 100%;
  max-height: 60vh;
  object-fit: contain;
}

.preview-nav {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 12px;
}

.nav-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-indicator {
  color: white;
  font-size: 14px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

.preview-info {
  padding: 16px;
  background: #fafafa;
  border-radius: 8px;
}

.info-value {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
}

.preview-actions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}
</style>
