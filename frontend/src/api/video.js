/**
 * 视频生成相关API接口
 */
import axios from 'axios'
import { API_CONFIG, getApiUrl } from '@/utils/config'

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    return Promise.reject(new Error(message))
  }
)

/**
 * 生成视频（文生视频）
 * @param {Object} params - 生成参数
 * @param {string} params.prompt - 提示词
 * @param {string} [params.resolution] - 分辨率 (480p/720p/1080p)
 * @param {string} [params.aspect_ratio] - 宽高比
 * @param {number} [params.duration] - 时长(秒)
 * @param {boolean} [params.watermark] - 是否添加水印
 */
export const generateVideo = (params) => {
  return apiClient.post(getApiUrl('/api/v1/videos/generate'), params)
}

/**
 * 生成视频（图生视频）
 * @param {Object} params - 生成参数
 * @param {string} params.prompt - 提示词
 * @param {string} [params.image_url] - 输入图片URL
 * @param {string} [params.image_base64] - 输入图片base64数据
 * @param {string} [params.resolution] - 分辨率
 * @param {string} [params.aspect_ratio] - 宽高比
 * @param {number} [params.duration] - 时长(秒)
 * @param {boolean} [params.watermark] - 是否添加水印
 */
export const generateVideoFromImage = (params) => {
  return apiClient.post(getApiUrl('/api/v1/videos/generate-from-image'), params)
}

/**
 * 获取视频详情
 * @param {string} videoId - 视频ID
 */
export const getVideoDetail = (videoId) => {
  return apiClient.get(getApiUrl(`/api/v1/videos/${videoId}`))
}

/**
 * 查询任务状态
 * @param {string} taskId - 任务ID
 */
export const getTaskStatus = (taskId) => {
  return apiClient.get(getApiUrl(`/api/v1/videos/status/${taskId}`))
}

/**
 * 获取视频生成历史
 * @param {number} page - 页码
 * @param {number} pageSize - 每页数量
 */
export const getVideoHistory = (page = 1, pageSize = 20) => {
  return apiClient.get(getApiUrl('/api/v1/videos/history/list'), {
    params: { page, page_size: pageSize }
  })
}

/**
 * 删除视频
 * @param {string} videoId - 视频ID
 */
export const deleteVideo = (videoId) => {
  return apiClient.delete(getApiUrl(`/api/v1/videos/${videoId}`))
}

/**
 * 清空视频历史
 */
export const clearVideoHistory = () => {
  return apiClient.delete(getApiUrl('/api/v1/videos/history/clear'))
}

/**
 * 下载视频
 * @param {string} videoId - 视频ID
 */
export const downloadVideo = (videoId) => {
  return `${API_CONFIG.BASE_URL}/api/v1/videos/download/${videoId}`
}

/**
 * 获取视频（用于播放）
 * @param {string} videoId - 视频ID
 */
export const serveVideo = (videoId) => {
  return `${API_CONFIG.BASE_URL}/api/v1/videos/serve/${videoId}`
}

export default {
  generateVideo,
  generateVideoFromImage,
  getVideoDetail,
  getTaskStatus,
  getVideoHistory,
  deleteVideo,
  clearVideoHistory,
  downloadVideo,
  serveVideo
}
