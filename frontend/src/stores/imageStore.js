/**
 * 图片状态管理
 */
import { defineStore } from 'pinia'
import {
  generateImages as apiGenerateImages,
  getImageHistory as apiGetHistory,
  deleteImage as apiDeleteImage,
  clearHistory as apiClearHistory
} from '@/api/image'

export const useImageStore = defineStore('image', {
  state: () => ({
    // 生成状态
    generating: false,
    generatingMessage: '',
    currentImages: [],

    // 历史记录
    history: [],
    historyTotal: 0,
    historyPage: 1,
    historyPageSize: 20,
    loadingHistory: false,

    // 错误信息
    error: null
  }),

  getters: {
    hasImages: (state) => state.currentImages.length > 0,
    hasHistory: (state) => state.history.length > 0
  },

  actions: {
    /**
     * 生成图片
     */
    async generateImages(params) {
      this.generating = true
      this.error = null
      this.generatingMessage = '正在生成图片...'

      try {
        const response = await apiGenerateImages(params)

        if (response.success) {
          this.currentImages = response.data
          this.generatingMessage = '生成成功！'
          return { success: true, data: response.data }
        } else {
          this.error = response.message
          this.generatingMessage = response.message
          return { success: false, error: response.message }
        }
      } catch (error) {
        this.error = error.message
        this.generatingMessage = error.message
        return { success: false, error: error.message }
      } finally {
        this.generating = false
      }
    },

    /**
     * 加载历史记录
     */
    async loadHistory(page = 1) {
      this.loadingHistory = true

      try {
        const response = await apiGetHistory(page, this.historyPageSize)

        if (response.success) {
          this.history = response.data
          this.historyTotal = response.total
          this.historyPage = page
        }
      } catch (error) {
        this.error = error.message
      } finally {
        this.loadingHistory = false
      }
    },

    /**
     * 删除图片
     */
    async deleteImage(imageId) {
      try {
        const response = await apiDeleteImage(imageId)

        if (response.success) {
          // 从当前图片中移除
          this.currentImages = this.currentImages.filter(img => img.id !== imageId)
          // 从历史中移除
          this.history = this.history.filter(img => img.id !== imageId)
          this.historyTotal--
          return { success: true }
        }
      } catch (error) {
        this.error = error.message
        return { success: false, error: error.message }
      }
    },

    /**
     * 清空历史
     */
    async clearHistory() {
      try {
        const response = await apiClearHistory()

        if (response.success) {
          this.history = []
          this.historyTotal = 0
          return { success: true, count: response.count }
        }
      } catch (error) {
        this.error = error.message
        return { success: false, error: error.message }
      }
    },

    /**
     * 清空当前图片
     */
    clearCurrentImages() {
      this.currentImages = []
      this.error = null
    },

    /**
     * 清空错误
     */
    clearError() {
      this.error = null
    }
  }
})
