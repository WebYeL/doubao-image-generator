<template>
  <div class="page-container">
    <a-layout>
      <!-- 顶部导航 -->
      <a-layout-header class="header">
        <div class="header-content">
          <div class="logo">
            <ThunderboltOutlined class="logo-icon" />
            <span>生成历史</span>
          </div>
          <div class="header-actions">
            <a-space>
              <a-button @click="$router.push('/')">
                <template #icon><ArrowLeftOutlined /></template>
                返回
              </a-button>
            </a-space>
          </div>
        </div>
      </a-layout-header>

      <!-- 主内容 -->
      <a-layout-content class="main-content">
        <a-card title="历史记录" class="history-card">
          <template #extra>
            <a-space>
              <a-button @click="handleRefresh" :loading="imageStore.loadingHistory">
                <template #icon><ReloadOutlined /></template>
                刷新
              </a-button>
              <a-button
                danger
                @click="handleClearHistory"
                :disabled="imageStore.historyTotal === 0"
              >
                <template #icon><DeleteOutlined /></template>
                清空全部
              </a-button>
            </a-space>
          </template>

          <!-- 统计信息 -->
          <div class="stats-bar" v-if="imageStore.historyTotal > 0">
            <span>共 {{ imageStore.historyTotal }} 条记录</span>
          </div>

          <!-- 加载状态 -->
          <a-spin v-if="imageStore.loadingHistory" class="loading-spinner" />

          <!-- 空状态 -->
          <a-empty v-else-if="imageStore.history.length === 0" :image="Empty.PRESENTED_IMAGE_SIMPLE">
            <template #description>
              <span class="empty-text">暂无生成历史</span>
            </template>
          </a-empty>

          <!-- 历史记录列表 -->
          <a-table
            v-else
            :dataSource="imageStore.history"
            :columns="columns"
            :pagination="false"
            :row-key="record => record.id"
            class="history-table"
          >
            <!-- 缩略图 -->
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'thumbnail'">
                <div class="thumbnail-cell">
                  <img
                    :src="record.thumbnail_url || '/placeholder.png'"
                    :alt="record.prompt"
                    @error="handleImageError"
                  />
                </div>
              </template>

              <!-- 提示词 -->
              <template v-if="column.key === 'prompt'">
                <a-tooltip :title="record.prompt" placement="topLeft">
                  <span class="prompt-text">{{ record.prompt }}</span>
                </a-tooltip>
              </template>

              <!-- 尺寸 -->
              <template v-if="column.key === 'size'">
                <span>{{ record.width }} × {{ record.height }}</span>
              </template>

              <!-- 时间 -->
              <template v-if="column.key === 'created_at'">
                <span>{{ formatTime(record.created_at) }}</span>
              </template>

              <!-- 操作 -->
              <template v-if="column.key === 'action'">
                <a-space>
                  <a-button type="link" size="small" @click="handlePreview(record)">
                    预览
                  </a-button>
                  <a-button type="link" size="small" @click="handleDownload(record)">
                    下载
                  </a-button>
                  <a-button type="link" danger size="small" @click="handleDelete(record)">
                    删除
                  </a-button>
                </a-space>
              </template>
            </template>
          </a-table>

          <!-- 分页 -->
          <div class="pagination-wrapper" v-if="imageStore.historyTotal > 0">
            <a-pagination
              v-model:current="currentPage"
              :total="imageStore.historyTotal"
              :page-size="imageStore.historyPageSize"
              show-quick-jumper
              @change="handlePageChange"
            />
          </div>
        </a-card>

        <!-- 预览弹窗 -->
        <a-modal
          v-model:open="previewVisible"
          :footer="null"
          :width="900"
          title="图片预览"
          centered
        >
          <div class="preview-modal-content" v-if="previewImage">
            <div class="preview-image-container">
              <img :src="previewImage.thumbnail_url" :alt="previewImage.prompt" />
            </div>
            <div class="preview-details">
              <a-descriptions :column="1" size="small">
                <a-descriptions-item label="提示词">
                  {{ previewImage.prompt }}
                </a-descriptions-item>
                <a-descriptions-item label="尺寸">
                  {{ previewImage.width }} × {{ previewImage.height }}
                </a-descriptions-item>
                <a-descriptions-item label="生成时间">
                  {{ formatTime(previewImage.created_at) }}
                </a-descriptions-item>
              </a-descriptions>
              <div class="preview-actions">
                <a-button type="primary" @click="handleDownload(previewImage)">
                  下载
                </a-button>
              </div>
            </div>
          </div>
        </a-modal>
      </a-layout-content>

      <!-- 页脚 -->
      <a-layout-footer class="footer">
        <span>Doubao Image Generator v1.0.0</span>
      </a-layout-footer>
    </a-layout>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import { Empty } from 'ant-design-vue'
import {
  ThunderboltOutlined,
  ArrowLeftOutlined,
  ReloadOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue'
import { useImageStore } from '@/stores/imageStore'
import { downloadImage } from '@/api/image'
import dayjs from 'dayjs'

const router = useRouter()
const imageStore = useImageStore()

const currentPage = ref(1)
const previewVisible = ref(false)
const previewImage = ref(null)

const columns = [
  {
    title: '缩略图',
    key: 'thumbnail',
    width: 100
  },
  {
    title: '提示词',
    key: 'prompt',
    ellipsis: true
  },
  {
    title: '尺寸',
    key: 'size',
    width: 150
  },
  {
    title: '时间',
    key: 'created_at',
    width: 180
  },
  {
    title: '操作',
    key: 'action',
    width: 180
  }
]

onMounted(() => {
  loadHistory()
})

const loadHistory = (page = 1) => {
  imageStore.loadHistory(page)
}

const handlePageChange = (page) => {
  currentPage.value = page
  loadHistory(page)
}

const handleRefresh = () => {
  loadHistory(currentPage.value)
  message.success('已刷新')
}

const handleClearHistory = () => {
  Modal.confirm({
    title: '确认清空',
    content: '确定要清空所有历史记录吗？此操作不可恢复。',
    okText: '确认',
    cancelText: '取消',
    okType: 'danger',
    onOk: async () => {
      const result = await imageStore.clearHistory()
      if (result.success) {
        message.success(`已清空 ${result.count} 条记录`)
      } else {
        message.error(result.error || '清空失败')
      }
    }
  })
}

const handlePreview = (record) => {
  previewImage.value = record
  previewVisible.value = true
}

const handleDownload = (record) => {
  const url = downloadImage(record.id)
  const link = document.createElement('a')
  link.href = url
  link.download = `doubao_${record.id}.png`
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  message.success('开始下载')
}

const handleDelete = (record) => {
  Modal.confirm({
    title: '确认删除',
    content: '确定要删除这条记录吗？',
    okText: '确认',
    cancelText: '取消',
    okType: 'danger',
    onOk: async () => {
      const result = await imageStore.deleteImage(record.id)
      if (result.success) {
        message.success('删除成功')
      } else {
        message.error(result.error || '删除失败')
      }
    }
  })
}

const handleImageError = (e) => {
  e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="60" height="60"%3E%3Crect fill="%23f0f0f0" width="60" height="60"/%3E%3C/svg%3E'
}

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
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

.history-card {
  min-height: 600px;
}

.stats-bar {
  margin-bottom: 16px;
  padding: 12px;
  background: #fafafa;
  border-radius: 4px;
  color: #666;
}

.loading-spinner {
  display: flex;
  justify-content: center;
  padding: 60px 20px;
}

.empty-text {
  color: #999;
}

.history-table :deep(.ant-table-thead > tr > th) {
  background: #fafafa;
}

.thumbnail-cell {
  width: 60px;
  height: 60px;
  border-radius: 4px;
  overflow: hidden;
}

.thumbnail-cell img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.prompt-text {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.pagination-wrapper {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

.preview-modal-content {
  display: flex;
  gap: 24px;
}

.preview-image-container {
  flex: 1;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-image-container img {
  max-width: 100%;
  max-height: 400px;
  object-fit: contain;
}

.preview-details {
  width: 300px;
}

.preview-actions {
  margin-top: 24px;
}

.footer {
  text-align: center;
  color: #999;
  font-size: 12px;
  padding: 16px;
}
</style>
