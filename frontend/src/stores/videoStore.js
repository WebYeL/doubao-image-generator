/**
 * 视频状态管理
 */
import { defineStore } from 'pinia'
import {
  generateVideo as apiGenerateVideo,
  generateVideoFromImage as apiGenerateVideoFromImage,
  getVideoHistory as apiGetHistory,
  getTaskStatus as apiGetTaskStatus,
  deleteVideo as apiDeleteVideo,
  clearVideoHistory as apiClearHistory
} from '@/api/video'

const POLLING_TASK_KEY = 'doubao_video_polling_task'

export const useVideoStore = defineStore('video', {
  state: () => ({
    // 生成状态
    generating: false,
    generatingMessage: '',
    currentVideo: null,

    // 历史记录
    history: [],
    historyTotal: 0,
    historyPage: 1,
    historyPageSize: 20,
    loadingHistory: false,

    // 错误信息
    error: null,

    // 轮询状态
    pollingTaskId: null,
    pollingTimer: null
  }),

  getters: {
    hasVideo: (state) => state.currentVideo !== null,
    hasHistory: (state) => state.history.length > 0
  },

  actions: {
    /**
     * 保存轮询任务到 localStorage
     */
    savePollingTask(taskId) {
      if (taskId) {
        localStorage.setItem(POLLING_TASK_KEY, JSON.stringify({
          taskId,
          timestamp: Date.now()
        }))
      }
    },

    /**
     * 获取保存的轮询任务
     */
    getSavedPollingTask() {
      try {
        const saved = localStorage.getItem(POLLING_TASK_KEY)
        if (saved) {
          const data = JSON.parse(saved)
          // 有效期24小时
          if (Date.now() - data.timestamp < 24 * 60 * 60 * 1000) {
            return data.taskId
          }
          localStorage.removeItem(POLLING_TASK_KEY)
        }
      } catch (e) {
        localStorage.removeItem(POLLING_TASK_KEY)
      }
      return null
    },

    /**
     * 清除保存的轮询任务
     */
    clearSavedPollingTask() {
      localStorage.removeItem(POLLING_TASK_KEY)
    },

    /**
     * 恢复轮询（页面刷新后调用）
     */
    async restorePolling() {
      const savedTaskId = this.getSavedPollingTask()
      if (savedTaskId && !this.pollingTaskId) {
        this.pollingTaskId = savedTaskId
        this.generating = true
        this.generatingMessage = '正在恢复任务状态...'
        this.startPolling(savedTaskId)
      }
    },

    /**
     * 轮询任务状态
     */
    async pollTaskStatus(taskId) {
      try {
        const response = await apiGetTaskStatus(taskId)

        if (response.status === 'succeeded') {
          // 任务完成
          this.stopPolling()
          this.clearSavedPollingTask()
          this.currentVideo = {
            id: taskId,
            url: response.video_url,
            prompt: '视频生成'
          }
          this.generating = false
          this.generatingMessage = '视频生成成功！'
          // 刷新历史记录
          this.loadHistory()
          return { success: true, data: this.currentVideo }
        } else if (response.status === 'failed') {
          // 任务失败
          this.stopPolling()
          this.clearSavedPollingTask()
          this.error = response.error || '视频生成失败'
          this.generating = false
          this.generatingMessage = response.error || '生成失败'
          return { success: false, error: response.error }
        } else {
          // 继续轮询
          this.generatingMessage = `视频生成中... (${response.status})`
          return { polling: true, status: response.status }
        }
      } catch (error) {
        this.error = error.message
        return { success: false, error: error.message }
      }
    },

    /**
     * 开始轮询
     */
    startPolling(taskId) {
      this.pollingTaskId = taskId
      this.savePollingTask(taskId)

      // 先立即查询一次
      this.pollTaskStatus(taskId)

      // 设置定时器
      this.pollingTimer = setInterval(async () => {
        await this.pollTaskStatus(taskId)
      }, 5000) // 每5秒轮询一次
    },

    /**
     * 停止轮询
     */
    stopPolling() {
      if (this.pollingTimer) {
        clearInterval(this.pollingTimer)
        this.pollingTimer = null
      }
      this.pollingTaskId = null
      this.clearSavedPollingTask()
    },

    /**
     * 生成视频（文生视频）- 异步模式
     */
    async generateVideo(params) {
      this.generating = true
      this.error = null
      this.generatingMessage = '正在提交视频生成任务...'

      try {
        const response = await apiGenerateVideo(params)

        if (response.success && response.task_id) {
          // 任务提交成功，开始轮询
          this.generatingMessage = '任务已提交，等待视频生成...'
          this.startPolling(response.task_id)
          return { success: true, task_id: response.task_id }
        } else {
          this.error = response.message || '提交失败'
          this.generatingMessage = response.message
          this.generating = false
          return { success: false, error: response.message }
        }
      } catch (error) {
        this.error = error.message
        this.generatingMessage = error.message
        this.generating = false
        return { success: false, error: error.message }
      }
    },

    /**
     * 图生视频 - 异步模式
     */
    async generateVideoFromImage(params) {
      this.generating = true
      this.error = null
      this.generatingMessage = '正在提交视频生成任务...'

      try {
        const response = await apiGenerateVideoFromImage(params)

        if (response.success && response.task_id) {
          // 任务提交成功，开始轮询
          this.generatingMessage = '任务已提交，等待视频生成...'
          this.startPolling(response.task_id)
          return { success: true, task_id: response.task_id }
        } else {
          this.error = response.message || '提交失败'
          this.generatingMessage = response.message
          this.generating = false
          return { success: false, error: response.message }
        }
      } catch (error) {
        this.error = error.message
        this.generatingMessage = error.message
        this.generating = false
        return { success: false, error: error.message }
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
     * 删除视频
     */
    async deleteVideo(videoId) {
      try {
        const response = await apiDeleteVideo(videoId)

        if (response.success) {
          // 从当前视频中清除
          if (this.currentVideo?.id === videoId) {
            this.currentVideo = null
          }
          // 从历史中移除
          this.history = this.history.filter(v => v.id !== videoId)
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
     * 清空当前视频
     */
    clearCurrentVideo() {
      this.currentVideo = null
      this.error = null
      this.stopPolling()
    },

    /**
     * 清空错误
     */
    clearError() {
      this.error = null
    }
  }
})
