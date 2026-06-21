<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside width="200px" class="sidebar">
      <div class="logo">
        <h2>GWP 小店</h2>
        <p>商家管理后台</p>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="menu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
      >
        <el-menu-item
          v-for="route in menuRoutes"
          :key="route.path"
          :index="route.path"
        >
          <el-icon><component :is="route.meta?.icon" /></el-icon>
          <span>{{ route.meta?.title }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 主内容区 -->
    <el-container class="main-container">
      <!-- 顶部导航栏 -->
      <el-header class="header">
        <div class="header-left">
          <h3>{{ pageTitle }}</h3>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon><User /></el-icon>
              {{ userStore.userInfo?.username || '管理员' }}
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store'
import { User } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 菜单路由
const menuRoutes = computed(() => {
  return router.options.routes
    .find(r => r.path === '/')?.children
    ?.filter((r: any) => !r.meta?.hidden) || []
})

// 当前激活的菜单
const activeMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/products/edit')) return '/products'
  if (path.startsWith('/orders/detail')) return '/orders'
  return path
})

// 页面标题
const pageTitle = computed(() => route.meta?.title || '')

// 处理下拉菜单命令
const handleCommand = (command: string) => {
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }).then(() => {
      userStore.logout()
      ElMessage.success('已退出登录')
      router.push('/login')
    }).catch(() => {})
  }
}
</script>

<style scoped>
.layout-container {
  height: 100%;
}

.sidebar {
  background-color: #304156;
  display: flex;
  flex-direction: column;
}

.logo {
  padding: 24px 16px;
  text-align: center;
  border-bottom: 1px solid #1f2d3d;
}

.logo h2 {
  color: #fff;
  font-size: 20px;
  margin-bottom: 4px;
}

.logo p {
  color: #909399;
  font-size: 12px;
}

.menu {
  border: none;
  flex: 1;
}

.main-container {
  display: flex;
  flex-direction: column;
  background-color: #f0f2f5;
}

.header {
  background-color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.header-left h3 {
  font-size: 18px;
  color: #303133;
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
  cursor: pointer;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}
</style>
