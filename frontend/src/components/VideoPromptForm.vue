<template>
  <a-card title="视频生成" class="prompt-form-card">
    <template #extra>
      <a-space>
        <a-button-group>
          <a-button
            :type="!isImageToVideo ? 'primary' : 'default'"
            @click="switchToTextToVideo"
            :disabled="generating"
          >
            文生视频
          </a-button>
          <a-button
            :type="isImageToVideo ? 'primary' : 'default'"
            @click="switchToImageToVideo"
            :disabled="generating"
          >
            图生视频
          </a-button>
        </a-button-group>
        <a-button type="text" @click="handleClear" :disabled="generating">
          <template #icon><ClearOutlined /></template>
          清空
        </a-button>
      </a-space>
    </template>

    <a-form
      ref="formRef"
      :model="formState"
      :rules="rules"
      layout="vertical"
      @finish="handleSubmit"
    >
      <!-- 主提示词 -->
      <a-form-item label="提示词" name="prompt">
        <a-textarea
          v-model:value="formState.prompt"
          placeholder="描述你想要生成的视频内容..."
          :rows="4"
          :maxlength="2000"
          show-count
          :disabled="generating"
        />
      </a-form-item>

      <!-- 图生视频选项 -->
      <div v-if="isImageToVideo">
        <a-form-item label="参考图片">
          <a-upload
            :file-list="fileList"
            :before-upload="handleBeforeUpload"
            :custom-request="handleCustomRequest"
            :show-upload-list="true"
            :disabled="generating"
          >
            <a-button>
              <template #icon><UploadOutlined /></template>
              上传参考图片
            </a-button>
          </a-upload>
          <p class="ant-upload-hint">
            支持上传本地图片作为参考，或直接输入图片URL
          </p>
        </a-form-item>

        <a-form-item label="图片URL或Base64">
          <a-input
            v-model:value="formState.image_input"
            placeholder="输入图片URL或Base64编码字符串"
            :disabled="generating"
          />
        </a-form-item>
      </div>

      <!-- 视频参数 -->
      <div class="options-row">
        <a-form-item label="分辨率" name="resolution" class="options-item">
          <a-select
            v-model:value="formState.resolution"
            :disabled="generating"
          >
            <a-select-option value="480p">480p (标清)</a-select-option>
            <a-select-option value="720p">720p (高清)</a-select-option>
            <a-select-option value="1080p">1080p (全高清)</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="时长" name="duration" class="options-item">
          <a-select
            v-model:value="formState.duration"
            :disabled="generating"
          >
            <a-select-option :value="2">2秒</a-select-option>
            <a-select-option :value="5">5秒</a-select-option>
            <a-select-option :value="8">8秒</a-select-option>
            <a-select-option :value="10">10秒</a-select-option>
            <a-select-option :value="12">12秒</a-select-option>
          </a-select>
        </a-form-item>
      </div>

      <!-- 宽高比 -->
      <a-form-item label="宽高比" name="aspect_ratio">
        <a-select
          v-model:value="formState.aspect_ratio"
          :disabled="generating"
        >
          <a-select-option value="16:9">16:9 (横版)</a-select-option>
          <a-select-option value="4:3">4:3 (传统)</a-select-option>
          <a-select-option value="1:1">1:1 (方形)</a-select-option>
          <a-select-option value="3:4">3:4 (竖版)</a-select-option>
          <a-select-option value="9:16">9:16 (短视频)</a-select-option>
          <a-select-option value="21:9">21:9 (电影)</a-select-option>
        </a-select>
      </a-form-item>

      <!-- 视频模板 -->
      <a-form-item label="视频模板">
        <a-select
          v-model:value="selectedTemplate"
          placeholder="选择一个模板或自定义"
          allow-clear
          :disabled="generating"
          @change="handleTemplateChange"
        >
          <a-select-option value="nature">自然风景</a-select-option>
          <a-select-option value="city">城市建筑</a-select-option>
          <a-select-option value="portrait">人物特写</a-select-option>
          <a-select-option value="action">动作场景</a-select-option>
          <a-select-option value="animation">动画风格</a-select-option>
        </a-select>
      </a-form-item>

      <!-- 水印开关 -->
      <a-form-item>
        <a-checkbox v-model:checked="formState.watermark" :disabled="generating">
          添加水印
        </a-checkbox>
      </a-form-item>

      <!-- 提示信息 -->
      <a-alert
        type="info"
        show-icon
        class="video-tip"
      >
        <template #message>视频生成说明</template>
        <template #description>
          视频生成需要一定时间（通常1-3分钟），请耐心等待。
          视频生成为异步任务，生成完成后可在历史记录中查看。
        </template>
      </a-alert>

      <!-- 提交按钮 -->
      <a-form-item>
        <a-button
          type="primary"
          html-type="submit"
          :loading="generating"
          :disabled="generating"
          size="large"
          block
        >
          <template #icon>
            <VideoCameraAddOutlined v-if="!generating" />
          </template>
          {{ generating ? '生成中...' : isImageToVideo ? '图生视频' : '文生视频' }}
        </a-button>
      </a-form-item>
    </a-form>
  </a-card>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import {
  ClearOutlined,
  UploadOutlined,
  VideoCameraAddOutlined
} from '@ant-design/icons-vue'

const props = defineProps({
  generating: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit', 'clear'])

const formRef = ref(null)
const selectedTemplate = ref(null)

const formState = reactive({
  prompt: '',
  resolution: '720p',
  duration: 5,
  aspect_ratio: '16:9',
  watermark: true,
  image_input: ''
})

const fileList = ref([])
const isImageToVideo = ref(false)

const rules = {
  prompt: [
    { required: true, message: '请输入视频描述提示词' },
    { min: 1, message: '提示词至少1个字符' },
    { max: 2000, message: '提示词最多2000个字符' }
  ]
}

// 视频模板
const templates = {
  'nature': '壮丽的自然风景，阳光穿透森林，溪水潺潺流动，鸟语花香，微风轻拂树叶，4K超高清，电影级镜头',
  'city': '未来城市天际线，霓虹灯光闪烁，飞行汽车穿梭于高楼之间，雨夜的街道倒映着灯光，科幻风格',
  'portrait': '精致的人物面部特写，柔和的自然光线，细腻的表情变化，复古胶片质感，温暖色调',
  'action': '激烈的动作场景，快节奏剪辑，流畅的运动镜头，戏剧性的光影效果，史诗般的配乐',
  'animation': '生动的动画风格，色彩鲜艳，角色活泼可爱，梦幻般的背景，流畅的动画帧'
}

const handleTemplateChange = (value) => {
  if (value && templates[value]) {
    formState.prompt = templates[value]
  }
}

const switchToTextToVideo = () => {
  isImageToVideo.value = false
  formState.image_input = ''
  fileList.value = []
}

const switchToImageToVideo = () => {
  isImageToVideo.value = true
  formState.image_input = ''
  fileList.value = []
}

const handleClear = () => {
  formState.prompt = ''
  formState.resolution = '720p'
  formState.duration = 5
  formState.aspect_ratio = '16:9'
  formState.watermark = true
  formState.image_input = ''
  fileList.value = []
  selectedTemplate.value = null
  emit('clear')
}

const handleBeforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  if (!isImage) {
    message.error('请上传图片文件')
    return false
  }
  const isLt20M = file.size / 1024 / 1024 < 20
  if (!isLt20M) {
    message.error('图片大小不能超过20MB')
    return false
  }
  return true
}

const handleCustomRequest = (options) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    formState.image_input = e.target.result
    message.success('图片上传成功')
  }
  reader.readAsDataURL(options.file)
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()

    const params = {
      prompt: formState.prompt,
      resolution: formState.resolution,
      duration: formState.duration,
      aspect_ratio: formState.aspect_ratio,
      watermark: formState.watermark
    }

    // 如果是图生视频模式，添加图片参数
    if (isImageToVideo.value && formState.image_input) {
      if (formState.image_input.startsWith('data:')) {
        // 从 data URL 提取 base64 部分（去掉 data:image/xxx;base64, 前缀）
        const base64 = formState.image_input.split(',')[1]
        params.image_base64 = base64
      } else if (formState.image_input.startsWith('http://') || formState.image_input.startsWith('https://')) {
        params.image_url = formState.image_input
      } else {
        params.image_base64 = formState.image_input
      }
    }

    emit('submit', params)
  } catch (error) {
    message.error('请检查表单输入')
  }
}

// 暴露方法给父组件
defineExpose({
  resetForm: handleClear
})
</script>

<style scoped>
.prompt-form-card {
  height: 100%;
}

.options-row {
  display: flex;
  gap: 16px;
}

.options-item {
  flex: 1;
}

.video-tip {
  margin-bottom: 16px;
}

:deep(.ant-collapse-header) {
  font-weight: 500;
}

:deep(.ant-collapse-content-box) {
  padding: 16px !important;
}
</style>
