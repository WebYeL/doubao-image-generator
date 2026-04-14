/**
 * 图片生成相关API接口
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
 * 生成图片
 * @param {Object} params - 生成参数
 * @param {string} params.prompt - 提示词
 * @param {string} params.size - 尺寸
 * @param {number} params.n - 数量
 * @param {string} [params.style] - 风格
 * @param {string} [params.negative_prompt] - 负向提示词
 * @param {boolean} [params.watermark] - 是否添加水印
 */
export const generateImages = (params) => {
  return apiClient.post(getApiUrl('/api/v1/images/generate'), params)
}

/**
 * 获取图片详情
 * @param {string} imageId - 图片ID
 */
export const getImageDetail = (imageId) => {
  return apiClient.get(getApiUrl(`/api/v1/images/${imageId}`))
}

/**
 * 获取生成历史
 * @param {number} page - 页码
 * @param {number} pageSize - 每页数量
 */
export const getImageHistory = (page = 1, pageSize = 20) => {
  return apiClient.get(getApiUrl('/api/v1/images/history/list'), {
    params: { page, page_size: pageSize }
  })
}

/**
 * 删除图片
 * @param {string} imageId - 图片ID
 */
export const deleteImage = (imageId) => {
  return apiClient.delete(getApiUrl(`/api/v1/images/${imageId}`))
}

/**
 * 清空历史
 */
export const clearHistory = () => {
  return apiClient.delete(getApiUrl('/api/v1/images/history/clear'))
}

/**
 * 下载图片
 * @param {string} imageId - 图片ID
 */
export const downloadImage = (imageId) => {
  return `${API_CONFIG.BASE_URL}/api/v1/images/download/${imageId}`
}

/**
 * 获取图片（用于预览）
 * @param {string} imageId - 图片ID
 */
export const serveImage = (imageId) => {
  return `${API_CONFIG.BASE_URL}/api/v1/images/serve/${imageId}`
}

/**
 * 健康检查
 */
export const healthCheck = () => {
  return apiClient.get(getApiUrl('/health'))
}

export default {
  generateImages,
  getImageDetail,
  getImageHistory,
  deleteImage,
  clearHistory,
  downloadImage,
  serveImage,
  healthCheck
}
