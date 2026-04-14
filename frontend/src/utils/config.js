/**
 * API 配置文件
 */
export const API_CONFIG = {
  // 后端API地址（开发环境使用空字符串让请求走Vite代理，避免CORS）
  BASE_URL: import.meta.env.VITE_API_BASE_URL || '',
  // API版本
  API_VERSION: 'v1',
  // 请求超时时间（毫秒）
  TIMEOUT: 60000
}

// 获取完整的API路径
export const getApiUrl = (path) => {
  const base = API_CONFIG.BASE_URL || ''
  return base ? `${base}${path}` : path
}
