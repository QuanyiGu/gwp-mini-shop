/**
 * GWP小店 - API 请求封装
 * 微信小程序 HTTP 客户端
 * 支持 401 自动 refresh_token 并重试一次
 */

const BASE_URL = 'http://localhost:8001'  // 开发环境本地调试
const APP = getApp<IAppOption>()

// 是否正在刷新 token（防止并发请求同时刷新）
let isRefreshing = false
// 等待刷新完成的请求队列
let refreshQueue: Array<{
  resolve: (token: string | null) => void
  reject: (err: any) => void
}> = []

interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  header?: Record<string, string>
  loading?: boolean
  loadingText?: string
}

/**
 * 尝试刷新 access_token
 * 用队列确保并发 401 只触发一次 refresh
 */
function tryRefreshToken(): Promise<string | null> {
  return new Promise((resolve, reject) => {
    if (isRefreshing) {
      // 已经在刷新了，排队等待
      refreshQueue.push({ resolve, reject })
      return
    }

    isRefreshing = true
    const refreshToken = wx.getStorageSync('refresh_token')
    if (!refreshToken) {
      isRefreshing = false
      resolve(null)
      return
    }

    wx.request({
      url: `${BASE_URL}/api/auth/refresh`,
      method: 'POST',
      data: { refresh_token: refreshToken },
      header: { 'Content-Type': 'application/json' },
      success: (res) => {
        if (res.statusCode === 200) {
          const body = res.data as any
          if (body.code === 0 && body.data?.access_token) {
            const newToken = body.data.access_token
            wx.setStorageSync('token', newToken)
            if (APP) APP.globalData.token = newToken
            resolve(newToken)
          } else {
            resolve(null)
          }
        } else {
          resolve(null)
        }
      },
      fail: () => resolve(null),
      complete: () => {
        isRefreshing = false
        // 唤醒排队队列
        const q = refreshQueue.slice()
        refreshQueue = []
        // 如果刚刚的 refresh 成功，就带着新 token 唤醒每人一次
        const latestToken = wx.getStorageSync('token') || null
        q.forEach((item) => item.resolve(latestToken))
      },
    })
  })
}

/**
 * 通用请求方法
 */
function request<T = any>(options: RequestOptions): Promise<T> {
  return new Promise((resolve, reject) => {
    const { url, method = 'GET', data, header = {}, loading = true } = options

    // 显示加载中
    if (loading) {
      wx.showLoading({ title: options.loadingText || '加载中...', mask: true })
    }

    // 获取 token
    const token = wx.getStorageSync('token')
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...header,
    }
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    // 是否需要重试（避免无限递归）
    let hasRetried = false

    function doRequest(): void {
      wx.request({
        url: `${BASE_URL}${url}`,
        method,
        data,
        header: headers,
        success: async (res) => {
          wx.hideLoading()

          if (res.statusCode >= 200 && res.statusCode < 300) {
            const body = res.data as any
            if (body.code === 0 || body.code === 200) {
              resolve(body.data)
            } else {
              APP.handleError({ errno: res.statusCode, ...body }, url)
              reject(body)
            }
          } else if (res.statusCode === 401 && !hasRetried) {
            // 401 → 尝试 refresh → 重试一次
            hasRetried = true
            const newToken = await tryRefreshToken()
            if (newToken) {
              headers['Authorization'] = `Bearer ${newToken}`
              doRequest()
            } else {
              // refresh 也失败 → 清除登录态
              wx.removeStorageSync('token')
              wx.removeStorageSync('refresh_token')
              wx.removeStorageSync('userInfo')
              APP.handleError({ errno: 401, message: '登录已过期，请重新登录' }, url)
              reject({ errno: 401, message: '登录已过期' })
            }
          } else {
            const err = { errno: res.statusCode, message: '请求失败' }
            APP.handleError(err, url)
            reject(err)
          }
        },
        fail: (err) => {
          wx.hideLoading()
          const errMsg = { errno: -1, message: '网络请求失败，请检查网络连接' }
          console.error('[API] Request failed:', err)
          wx.showToast({ title: '网络请求失败', icon: 'none' })
          reject(errMsg)
        },
      })
    }

    doRequest()
  })
}

/**
 * GET 请求
 */
function get<T = any>(url: string, data?: any, loading = true): Promise<T> {
  return request<T>({ url, method: 'GET', data, loading })
}

/**
 * POST 请求
 */
function post<T = any>(url: string, data?: any, loading = true): Promise<T> {
  return request<T>({ url, method: 'POST', data, loading })
}

/**
 * PUT 请求
 */
function put<T = any>(url: string, data?: any, loading = true): Promise<T> {
  return request<T>({ url, method: 'PUT', data, loading })
}

/**
 * DELETE 请求
 */
function del<T = any>(url: string, data?: any, loading = true): Promise<T> {
  return request<T>({ url, method: 'DELETE', data, loading })
}

// ============================================
// API 模块
// ============================================

// 用户模块
export const userApi = {
  // 微信登录（推荐使用 api/auth.ts 中的 wxLogin，它会自动调用 wx.login）
  wxLogin: (code: string, nickname = '', avatar_url = '') =>
    post('/api/auth/wxlogin', { code, nickname, avatar_url }, false),

  // 获取用户信息
  getUserInfo: () => get<UserInfo>('/api/user/info'),

  // 更新用户信息
  updateUserInfo: (data: Partial<UserInfo>) => post('/api/user/update', data),

  // 获取邀请码
  getInviteCode: () => post<{ invite_code: string }>('/api/invites/generate'),
}

// 商品模块
export const productApi = {
  // 获取分类列表
  getCategories: () => get<Category[]>('/api/categories'),
  
  // 获取商品列表
  getProducts: (params: {
    category_id?: number
    page?: number
    page_size?: number
    keyword?: string
  }) => get<PageResult<Product>>('/api/products', params),
  
  // 获取商品详情
  getProductDetail: (id: number) => get<Product>('/api/products/' + id, null),
  
  // 获取首页数据
  getHomeData: () => get<{
    banners: Banner[]
    categories: Category[]
    products: Product[]
    growth_status: Banner
  }>('/api/home/data'),
}

// 购物车模块
export const cartApi = {
  // 获取购物车列表
  getCartList: () => get<CartItem[]>('/api/cart'),
  
  // 添加到购物车
  addToCart: (data: { product_id: number; quantity: number }) =>
    post<{ count: number }>('/api/cart', data),
  
  // 更新购物车数量
  updateCart: (data: { id: number; quantity: number }) =>
    put('/api/cart/' + data.id, { quantity: data.quantity }),

  // 删除购物车项
  removeCart: (id: number) =>
    del('/api/cart/' + id),
  
  // 全选/取消全选
  selectAll: (selected: boolean) =>
    post('/api/cart/select-all', { selected }),
}

// 订单模块
export const orderApi = {
  // 创建订单
  createOrder: (data: {
    address_id: number
    coupon_id?: number
    gift_package?: number
    greeting_card?: string
    remark?: string
  }) => post<Order>('/api/orders', data),
  
  // 订单列表
  getOrderList: (params: {
    status?: number
    page?: number
    page_size?: number
  }) => get<PageResult<Order>>('/api/orders', params),
  
  // 订单详情
  getOrderDetail: (order_no: string) =>
    get<OrderDetail>('/api/orders/' + order_no),
  
  // 取消订单
  cancelOrder: (order_no: string) =>
    post('/api/orders/' + order_no + '/cancel'),
  
  // 确认收货
  confirmReceive: (order_no: string) =>
    post('/api/orders/' + order_no + '/confirm'),
  
  // 申请退款
  applyRefund: (order_no: string, reason: string) =>
    post('/api/orders/' + order_no + '/refund', { reason }),
}

// 地址模块
export const addressApi = {
  // 获取地址列表
  getAddressList: () => get<Address[]>('/api/addresses'),
  
  // 获取默认地址
  getDefaultAddress: () => get<Address>('/api/addresses/default'),
  
  // 添加地址
  addAddress: (data: Omit<Address, 'id'>) =>
    post<{ id: number }>('/api/addresses', data),
  
  // 更新地址
  updateAddress: (data: Address) =>
    put('/api/addresses/' + data.id, data),

  // 删除地址
  deleteAddress: (id: number) =>
    del(`/api/addresses/${id}`),

  // 设置默认地址
  setDefaultAddress: (id: number) =>
    put('/api/addresses/' + id + '/default'),
}

// 优惠券模块
export const couponApi = {
  // 获取优惠券列表
  getCouponList: (params?: { status?: number }) =>
    get<Coupon[]>('/api/coupons', params),
  
  // 领取优惠券
  receiveCoupon: (code: string) =>
    post<{ id: number }>('/api/coupons/claim', { code }),
  
  // 我的优惠券
  getMyCoupons: (params?: { status?: number }) =>
    get<Coupon[]>('/api/coupons', params),
}

// 微信支付
export const wxpayApi = {
  /**
   * 发起预下单，返回 wx.requestPayment 直接可用的 5 个字段
   * 对接后端 POST /api/pay/prepare（需要 Bearer Token，由 request.ts 自动注入）
   */
  prepay: (order_no: string) =>
    post<{
      timeStamp: string
      nonceStr: string
      package: string
      signType: string
      paySign: string
    }>('/api/pay/prepare', { order_no }),
}

// 导出
export default {
  get,
  post,
  put,
  del,
  request,
  user: userApi,
  product: productApi,
  cart: cartApi,
  order: orderApi,
  address: addressApi,
  coupon: couponApi,
  wxpay: wxpayApi,
}
