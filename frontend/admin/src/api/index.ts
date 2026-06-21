// src/api/index.ts
import request from '@/utils/request'

// 认证相关
export const authApi = {
  // 商家登录
  login: (data: { username: string; password: string }) => {
    return request.post('/api/admin/login', data)
  },
  
  // 获取当前管理员信息
  getProfile: () => {
    return request.get('/api/admin/profile')
  },
}

// 数据概览
export const dashboardApi = {
  // 获取统计数据
  getStats: () => {
    return request.get('/api/admin/stats')
  },
  
  // 获取销售趋势
  getSalesTrend: (days: number = 7) => {
    return request.get('/api/admin/stats/trend', { params: { days } })
  },
}

// 商品管理
export const productApi = {
  // 获取商品列表
  getList: (params: { page?: number; page_size?: number; status?: number; category_id?: number }) => {
    return request.get('/api/admin/products', { params })
  },
  
  // 获取商品详情
  getDetail: (id: number) => {
    return request.get(`/api/admin/products/${id}`)
  },
  
  // 创建商品
  create: (data: any) => {
    return request.post('/api/admin/products', data)
  },
  
  // 更新商品
  update: (id: number, data: any) => {
    return request.put(`/api/admin/products/${id}`, data)
  },
  
  // 更新商品状态（上下架）
  updateStatus: (id: number, status: number) => {
    return request.put(`/api/admin/products/${id}/status`, { status })
  },
  
  // 更新商品扩展信息
  updateExtras: (id: number, data: any) => {
    return request.put(`/api/admin/products/${id}/extras`, data)
  },
}

// 订单管理
export const orderApi = {
  // 获取订单列表
  getList: (params: { page?: number; page_size?: number; status?: number }) => {
    return request.get('/api/admin/orders', { params })
  },
  
  // 获取订单详情
  getDetail: (orderNo: string) => {
    return request.get(`/api/admin/orders/${orderNo}`)
  },
  
  // 订单发货
  ship: (orderNo: string, data: { logistics_company: string; tracking_no: string }) => {
    return request.put(`/api/admin/orders/${orderNo}/ship`, data)
  },
  
  // 更新物流追踪
  updateTracking: (orderNo: string, data: { nodes: any[] }) => {
    return request.put(`/api/admin/orders/${orderNo}/tracking`, data)
  },
  
  // 处理退款
  handleRefund: (orderNo: string, data: { agree: boolean; reason?: string }) => {
    return request.put(`/api/admin/orders/${orderNo}/refund`, data)
  },
}

// Banner管理
export const bannerApi = {
  // 获取Banner列表
  getList: (params: { page?: number; page_size?: number }) => {
    return request.get('/api/admin/banners', { params })
  },
  
  // 创建Banner
  create: (data: any) => {
    return request.post('/api/admin/banners', data)
  },
  
  // 更新Banner
  update: (id: number, data: any) => {
    return request.put(`/api/admin/banners/${id}`, data)
  },
  
  // 删除Banner
  delete: (id: number) => {
    return request.delete(`/api/admin/banners/${id}`)
  },
}

// 分类管理
export const categoryApi = {
  // 获取分类列表
  getList: () => {
    return request.get('/api/categories')
  },
  
  // 创建分类
  create: (data: { name: string; icon: string; sort?: number }) => {
    return request.post('/api/admin/categories', data)
  },
  
  // 更新分类
  update: (id: number, data: any) => {
    return request.put(`/api/admin/categories/${id}`, data)
  },
  
  // 删除分类
  delete: (id: number) => {
    return request.delete(`/api/admin/categories/${id}`)
  },
}
