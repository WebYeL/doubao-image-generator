<template>
  <div class="image-gallery">
    <!-- 工具栏 -->
    <div class="gallery-toolbar" v-if="images.length > 0">
      <div class="toolbar-left">
        <span class="image-count">共 {{ images.length }} 张图片</span>
      </div>
      <div class="toolbar-right">
        <a-button-group>
          <a-button
            :type="viewMode === 'grid' ? 'primary' : 'default'"
            @click="viewMode = 'grid'"
          >
            <AppstoreOutlined />
          </a-button>
          <a-button
            :type="viewMode === 'list' ? 'primary' : 'default'"
            @click="viewMode = 'list'"
          >
            <BarsOutlined />
          </a-button>
        </a-button-group>
      </div>
    </div>

    <!-- 空状态 -->
    <a-empty v-if="images.length === 0" :image="Empty.PRESENTED_IMAGE_SIMPLE">
      <template #description>
        <span class="empty-text">暂无生成的图片</span>
      </template>
    </a-empty>

    <!-- 网格视图 -->
    <div v-else-if="viewMode === 'grid'" class="gallery-grid">
      <div
        v-for="(image, index) in images"
        :key="image.id || index"
        class="gallery-item"
        @click="handlePreview(image, index)"
      >
        <div class="image-wrapper">
          <img
            :src="getImageSrc(image)"
            :alt="`Image ${index + 1}`"
            loading="lazy"
            @error="handleImageError"
          />
          <div class="image-overlay">
            <div class="overlay-actions">
              <a-tooltip title="预览">
                <a-button type="text" size="small" @click.stop="handlePreview(image, index)">
                  <EyeOutlined />
                </a-button>
              </a-tooltip>
              <a-tooltip title="下载">
                <a-button type="text" size="small" @click.stop="handleDownload(image)">
                  <DownloadOutlined />
                </a-button>
              </a-tooltip>
              <a-tooltip title="复制链接">
                <a-button type="text" size="small" @click.stop="handleCopyLink(image)">
                  <CopyOutlined />
                </a-button>
              </a-tooltip>
              <a-tooltip title="删除">
                <a-button type="text" size="small" danger @click.stop="handleDelete(image)">
                  <DeleteOutlined />
                </a-button>
              </a-tooltip>
            </div>
          </div>
        </div>
        <div class="image-info">
          <span class="image-size">{{ image.width }} × {{ image.height }}</span>
        </div>
      </div>
    </div>

    <!-- 列表视图 -->
    <div v-else class="gallery-list">
      <div
        v-for="(image, index) in images"
        :key="image.id || index"
        class="list-item"
        @click="handlePreview(image, index)"
      >
        <div class="list-item-thumb">
          <img :src="getImageSrc(image)" :alt="`Image ${index + 1}`" @error="handleImageError" />
        </div>
        <div class="list-item-info">
          <div class="list-item-prompt">{{ image.prompt || '未命名' }}</div>
          <div class="list-item-meta">
            <span>尺寸: {{ image.width }} × {{ image.height }}</span>
            <span v-if="image.local_path">已下载</span>
            <span v-else>仅URL</span>
          </div>
        </div>
        <div class="list-item-actions">
          <a-button type="text" @click.stop="handlePreview(image, index)">
            <EyeOutlined />
          </a-button>
          <a-button type="text" @click.stop="handleDownload(image)">
            <DownloadOutlined />
          </a-button>
          <a-button type="text" danger @click.stop="handleDelete(image)">
            <DeleteOutlined />
          </a-button>
        </div>
      </div>
    </div>

    <!-- 图片预览弹窗 -->
    <ImagePreview
      v-model:visible="previewVisible"
      :image="currentImage"
      :images="images"
      :currentIndex="currentIndex"
      @prev="handlePrev"
      @next="handleNext"
      @delete="handleDelete"
      @download="handleDownload"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { Empty } from 'ant-design-vue'
import {
  AppstoreOutlined,
  BarsOutlined,
  EyeOutlined,
  DownloadOutlined,
  CopyOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue'
import { downloadImage as getDownloadUrl, serveImage as getServeUrl } from '@/api/image'
import ImagePreview from './ImagePreview.vue'

const props = defineProps({
  images: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['delete', 'download', 'preview'])

const viewMode = ref('grid')
const previewVisible = ref(false)
const currentImage = ref(null)
const currentIndex = ref(0)

const getImageSrc = (image) => {
  if (image.local_path) {
    return `/api/v1/images/serve/${image.id}`
  }
  return image.url || ''
}

const handleImageError = (e) => {
  e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect fill="%23f0f0f0" width="200" height="200"/%3E%3Ctext fill="%23999" font-size="14" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3E图片加载失败%3C/text%3E%3C/svg%3E'
}

const handlePreview = (image, index) => {
  currentImage.value = image
  currentIndex.value = index
  previewVisible.value = true
  emit('preview', { image, index })
}

const handlePrev = () => {
  if (currentIndex.value > 0) {
    currentIndex.value--
    currentImage.value = props.images[currentIndex.value]
  }
}

const handleNext = () => {
  if (currentIndex.value < props.images.length - 1) {
    currentIndex.value++
    currentImage.value = props.images[currentIndex.value]
  }
}

const handleDownload = (image) => {
  const url = image.local_path ? getDownloadUrl(image.id) : image.url
  if (!url) {
    message.error('图片地址无效')
    return
  }

  // 创建下载链接
  const link = document.createElement('a')
  link.href = url
  link.download = `doubao_${image.id}.png`
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)

  emit('download', image)
}

const handleCopyLink = (image) => {
  const url = image.url || image.local_path
  if (url) {
    navigator.clipboard.writeText(url).then(() => {
      message.success('链接已复制到剪贴板')
    }).catch(() => {
      message.error('复制失败')
    })
  }
}

const handleDelete = (image) => {
  Modal.confirm({
    title: '确认删除',
    content: '确定要删除这张图片吗？',
    okText: '确认',
    cancelText: '取消',
    onOk() {
      emit('delete', image)
    }
  })
}
</script>

<style scoped>
.image-gallery {
  width: 100%;
}

.gallery-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding: 8px 0;
}

.image-count {
  color: #666;
  font-size: 14px;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.gallery-item {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  background: #f5f5f5;
  cursor: pointer;
  transition: all 0.3s;
}

.gallery-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.image-wrapper {
  position: relative;
  aspect-ratio: 1;
}

.image-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  opacity: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.3s;
}

.gallery-item:hover .image-overlay {
  opacity: 1;
}

.overlay-actions {
  display: flex;
  gap: 8px;
}

.overlay-actions :deep(.ant-btn) {
  color: white;
  background: rgba(255, 255, 255, 0.2);
}

.overlay-actions :deep(.ant-btn:hover) {
  background: rgba(255, 255, 255, 0.3);
}

.image-info {
  padding: 8px;
  text-align: center;
  font-size: 12px;
  color: #666;
}

.gallery-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.list-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background: #fafafa;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.3s;
}

.list-item:hover {
  background: #f0f0f0;
}

.list-item-thumb {
  width: 60px;
  height: 60px;
  border-radius: 4px;
  overflow: hidden;
  flex-shrink: 0;
}

.list-item-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.list-item-info {
  flex: 1;
  margin-left: 12px;
  min-width: 0;
}

.list-item-prompt {
  font-size: 14px;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.list-item-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.list-item-actions {
  display: flex;
  gap: 4px;
  margin-left: 12px;
}

.empty-text {
  color: #999;
}
</style>
