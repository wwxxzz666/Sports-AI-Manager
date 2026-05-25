import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home/index.vue'),
    meta: { showTabBar: true, title: '首页' },
  },
  {
    path: '/agents',
    name: 'Agents',
    component: () => import('@/views/Agents/index.vue'),
    meta: { showTabBar: true, title: '智能体' },
  },
  {
    path: '/health',
    name: 'Health',
    component: () => import('@/views/Health/index.vue'),
    meta: { showTabBar: true, title: '健康中心' },
  },
  {
    path: '/rating',
    name: 'Rating',
    component: () => import('@/views/Rating/index.vue'),
    meta: { showTabBar: true, title: 'AI 评级' },
  },
  {
    path: '/upload-video',
    name: 'UploadVideo',
    component: () => import('@/views/UploadVideo/index.vue'),
    meta: { showTabBar: false, title: '动作分析' },
  },
  {
    path: '/nutrition',
    name: 'Nutrition',
    component: () => import('@/views/Nutrition/index.vue'),
    meta: { showTabBar: false, title: '饮食记录' },
  },
  {
    path: '/chat/:agentId',
    name: 'AgentChat',
    component: () => import('@/views/Chat/index.vue'),
    meta: { showTabBar: false, title: '对话' },
  },
]

export default routes
