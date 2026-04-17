<template>
  <div class="video-gallery">
    <!-- 空状态 -->
    <a-empty v-if="!video" :image="Empty.PRESENTED_IMAGE_SIMPLE">
      <template #description>
        <span class="empty-text">暂无生成的视频</span>
      </template>
    </a-empty>

    <!-- 视频展示 -->
    <div v-else class="video-container">
      <div class="video-info-bar">
        <div class="video-meta">
          <a-tag color="blue">{{ video.width }} x {{ video.height }}</a-tag>
          <a-tag color="green">{{ video.duration }}秒</a-tag>
          <span class="video-date">{{ formatDate(video.created_at) }}</span>
        </div>
      </div>

      <div class="video-player-wrapper">
        <video
          ref="videoRef"
          :src="videoUrl"
          controls
          :poster="video.thumbnail_url"
          class="video-player"
          @error="handleVideoError"
        >
          您的浏览器不支持视频播放
        </video>
      </div>

      <div class="video-actions">
        <a-space>
          <a-button type="primary" @click="handleDownload">
            <template #icon><DownloadOutlined /></template>
            下载视频
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

      <div class="video-prompt">
        <h4>提示词</h4>
        <p>{{ video.prompt }}</p>
      </div>
    </div>

    <!-- 视频预览弹窗 -->
    <a-modal
      v-model:open="previewVisible"
      title="视频预览"
      :footer="null"
      width="800px"
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
import { ref, computed } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { Empty } from 'ant-design-vue'
import {
  DownloadOutlined,
  CopyOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue'
import { downloadVideo as getDownloadUrl, serveVideo as getServeUrl } from '@/api/video'

const props = defineProps({
  video: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['delete', 'download'])

const videoRef = ref(null)
const previewVisible = ref(false)
const previewUrl = ref('')

const videoUrl = computed(() => {
  if (!props.video) return ''
  if (props.video.local_path) {
    return getServeUrl(props.video.id)
  }
  return props.video.url || ''
})

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleVideoError = () => {
  message.error('视频加载失败')
}

const handleDownload = () => {
  const url = props.video.local_path ? getDownloadUrl(props.video.id) : props.video.url
  if (!url) {
    message.error('视频地址无效')
    return
  }

  const link = document.createElement('a')
  link.href = url
  link.download = `doubao_video_${props.video.id}.mp4`
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)

  emit('download', props.video)
}

const handleCopyLink = () => {
  const url = props.video.url || videoUrl.value
  if (url) {
    navigator.clipboard.writeText(url).then(() => {
      message.success('链接已复制到剪贴板')
    }).catch(() => {
      message.error('复制失败')
    })
  }
}

const handleDelete = () => {
  Modal.confirm({
    title: '确认删除',
    content: '确定要删除这个视频吗？',
    okText: '确认',
    cancelText: '取消',
    onOk() {
      emit('delete', props.video)
    }
  })
}

const handlePreview = () => {
  previewUrl.value = videoUrl.value
  previewVisible.value = true
}

defineExpose({
  handlePreview
})
</script>

<style scoped>
.video-gallery {
  width: 100%;
}

.empty-text {
  color: #999;
}

.video-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.video-info-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.video-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.video-date {
  color: #999;
  font-size: 12px;
}

.video-player-wrapper {
  background: #000;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  justify-content: center;
  align-items: center;
}

.video-player {
  width: 100%;
  max-height: 500px;
  object-fit: contain;
}

.video-actions {
  display: flex;
  justify-content: center;
  padding: 8px 0;
}

.video-prompt {
  background: #fafafa;
  border-radius: 8px;
  padding: 16px;
}

.video-prompt h4 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 14px;
}

.video-prompt p {
  margin: 0;
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}

.preview-video {
  width: 100%;
  max-height: 600px;
  object-fit: contain;
}
</style>
