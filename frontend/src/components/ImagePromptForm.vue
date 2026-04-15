<template>
  <a-card title="图片生成" class="prompt-form-card">
    <template #extra>
      <a-space>
        <a-button-group>
          <a-button
            :type="!isImageToImage ? 'primary' : 'default'"
            @click="switchToTextToImage"
            :disabled="generating"
          >
            文生图
          </a-button>
          <a-button
            :type="isImageToImage ? 'primary' : 'default'"
            @click="switchToImageToImage"
            :disabled="generating"
          >
            图生图
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
          placeholder="描述你想要生成的图片内容..."
          :rows="6"
          :maxlength="2000"
          show-count
          :disabled="generating"
        />
      </a-form-item>

      <!-- 图生图选项 - 仅在图生图模式下显示 -->
      <div v-if="isImageToImage">
        <!-- 图生图输入 -->
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

      <!-- 提示词模板 -->
      <a-form-item label="提示词模板">
        <a-select
          v-model:value="selectedTemplate"
          placeholder="选择一个模板或自定义"
          allow-clear
          :disabled="generating"
          @change="handleTemplateChange"
        >
          <a-select-option value="fantasy">奇幻风格</a-select-option>
          <a-select-option value="sci-fi">科幻风格</a-select-option>
          <a-select-option value="portrait">人物肖像</a-select-option>
          <a-select-option value="landscape">自然风景</a-select-option>
          <a-select-option value="abstract">抽象艺术</a-select-option>
          <a-select-option value="cyberpunk">赛博朋克</a-select-option>
        </a-select>
      </a-form-item>

      <!-- 高级选项折叠 -->
      <a-collapse v-model:activeKey="activeKey" :bordered="false">
        <a-collapse-panel key="advanced" header="高级选项">
          <!-- 尺寸和数量 -->
          <div class="options-row">
            <a-form-item label="图片尺寸" name="size" class="options-item">
              <a-select
                v-model:value="formState.size"
                :disabled="generating"
              >
                <a-select-option value="1K">1K (横版)</a-select-option>
                <a-select-option value="2K">2K (横版)</a-select-option>
                <a-select-option value="4K">4K (横版)</a-select-option>
                <a-select-option value="竖图1K">竖图 1K</a-select-option>
                <a-select-option value="竖图2K">竖图 2K</a-select-option>
              </a-select>
            </a-form-item>

            <a-form-item label="生成数量" name="n" class="options-item">
              <a-select
                v-model:value="formState.n"
                :disabled="generating"
              >
                <a-select-option :value="1">1 张</a-select-option>
                <a-select-option :value="2">2 张</a-select-option>
                <a-select-option :value="3">3 张</a-select-option>
                <a-select-option :value="4">4 张</a-select-option>
              </a-select>
            </a-form-item>
          </div>

          <!-- 风格 -->
          <a-form-item label="风格预设">
            <a-select
              v-model:value="formState.style"
              placeholder="选择风格（可选）"
              allow-clear
              :disabled="generating"
            >
              <a-select-option value="写实">写实</a-select-option>
              <a-select-option value="动漫">动漫</a-select-option>
              <a-select-option value="油画">油画</a-select-option>
              <a-select-option value="水彩">水彩</a-select-option>
              <a-select-option value="素描">素描</a-select-option>
              <a-select-option value="3D渲染">3D渲染</a-select-option>
            </a-select>
          </a-form-item>

          <!-- 负向提示词 -->
          <a-form-item label="负向提示词">
            <a-textarea
              v-model:value="formState.negative_prompt"
              placeholder="输入不希望出现在图片中的元素（可选）..."
              :rows="2"
              :maxlength="500"
              show-count
              :disabled="generating"
            />
          </a-form-item>

          <!-- 水印开关 -->
          <a-form-item>
            <a-checkbox v-model:checked="formState.watermark" :disabled="generating">
              添加水印
            </a-checkbox>
          </a-form-item>
        </a-collapse-panel>
      </a-collapse>

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
            <ThunderboltOutlined v-if="!generating" />
          </template>
          {{ generating ? '生成中...' : isImageToImage ? '图生图' : '生成图片' }}
        </a-button>
      </a-form-item>
    </a-form>
  </a-card>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'
import { message } from 'ant-design-vue'
import {
  ClearOutlined,
  ThunderboltOutlined,
  UploadOutlined
} from '@ant-design/icons-vue'

const props = defineProps({
  generating: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit', 'clear'])

const formRef = ref(null)
const activeKey = ref(['advanced'])
const selectedTemplate = ref(null)

const formState = reactive({
  prompt: '',
  size: '2K',
  n: 1,
  style: null,
  negative_prompt: '',
  watermark: true,
  image_input: ''
})

const fileList = ref([])
const isImageToImage = ref(false)

const rules = {
  prompt: [
    { required: true, message: '请输入图片描述提示词' },
    { min: 1, message: '提示词至少1个字符' },
    { max: 2000, message: '提示词最多2000个字符' }
  ]
}

// 提示词模板
const templates = {
  'fantasy': '奇幻风格的魔法世界，精灵、巨龙、古老的城堡，神秘的光影效果，史诗般的构图',
  'sci-fi': '未来科幻城市，高耸的摩天大楼，飞行汽车，霓虹灯光，赛博朋克风格',
  'portrait': '精致的人物肖像，柔和的光线，专业的摄影棚，细节丰富，皮肤纹理真实',
  'landscape': '壮丽的自然风景，连绵的山脉，日落的金色光芒，湖面倒影，超宽视角',
  'abstract': '抽象艺术作品，流动的色彩，几何形状，大胆的配色，视觉冲击力',
  'cyberpunk': '赛博朋克城市夜景，霓虹灯牌，雨中的街道，反光的水洼，高科技感'
}

const handleTemplateChange = (value) => {
  if (value && templates[value]) {
    formState.prompt = templates[value]
  }
}

const switchToTextToImage = () => {
  isImageToImage.value = false
  formState.image_input = ''
  fileList.value = []
}

const switchToImageToImage = () => {
  isImageToImage.value = true
  formState.image_input = ''
  fileList.value = []
}

const handleClear = () => {
  formState.prompt = ''
  formState.size = '2K'
  formState.n = 1
  formState.style = null
  formState.negative_prompt = ''
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
  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    message.error('图片大小不能超过10MB')
    return false
  }
  return true
}

const handleCustomRequest = (options) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    // 保留完整的data URL格式（Doubao API需要完整格式：data:image/png;base64,...）
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
      size: formState.size,
      n: formState.n,
      watermark: formState.watermark
    }

    if (formState.style) {
      params.style = formState.style
    }

    if (formState.negative_prompt) {
      params.negative_prompt = formState.negative_prompt
    }

    if (formState.image_input) {
      // 判断是URL还是base64数据
      // Base64格式：data:image/png;base64,... 或纯base64字符串
      // URL格式：以 http:// 或 https:// 开头
      if (formState.image_input.startsWith('data:')) {
        // 完整的data URL格式
        params.image_base64 = formState.image_input
      } else if (formState.image_input.startsWith('http://') || formState.image_input.startsWith('https://')) {
        // URL格式
        params.image_url = formState.image_input
      } else {
        // 纯base64字符串，添加前缀
        params.image_base64 = `data:image/png;base64,${formState.image_input}`
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

:deep(.ant-collapse-header) {
  font-weight: 500;
}

:deep(.ant-collapse-content-box) {
  padding: 16px !important;
}
</style>
