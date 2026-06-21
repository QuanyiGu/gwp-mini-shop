// src/router/index.ts
import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '商家登录', requiresAuth: false },
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/views/layout/index.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '数据概览', icon: 'DataLine' },
      },
      {
        path: 'products',
        name: 'Products',
        component: () => import('@/views/products/list.vue'),
        meta: { title: '商品管理', icon: 'Goods' },
      },
      {
        path: 'products/edit/:id?',
        name: 'ProductEdit',
        component: () => import('@/views/products/edit.vue'),
        meta: { title: '编辑商品', hidden: true },
      },
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('@/views/orders/list.vue'),
        meta: { title: '订单管理', icon: 'Document' },
      },
      {
        path: 'orders/detail/:orderNo',
        name: 'OrderDetail',
        component: () => import('@/views/orders/detail.vue'),
        meta: { title: '订单详情', hidden: true },
      },
      {
        path: 'banners',
        name: 'Banners',
        component: () => import('@/views/banners/list.vue'),
        meta: { title: 'Banner管理', icon: 'Picture' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('admin_token')
  
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/')
  } else {
    next()
  }
})

export default router
