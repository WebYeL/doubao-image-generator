<template>
  <a-config-provider :locale="zhCN">
    <router-view />
  </a-config-provider>
</template>

<script setup>
import { ConfigProvider as AConfigProvider } from 'ant-design-vue'
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import { useRouter, useRoute } from 'vue-router'
import { computed } from 'vue'

const router = useRouter()
const route = useRoute()

// 判断当前路由是否为视频相关页面，返回不同的主色
const isVideoRoute = computed(() => {
  return route.path.startsWith('/video')
})
</script>

<style>
#app {
  width: 100%;
  min-height: 100vh;
}
</style>
