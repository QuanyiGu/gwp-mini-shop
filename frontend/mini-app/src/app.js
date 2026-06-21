// ============================================
// GWP小店 - 微信小程序入口文件
// ============================================
import { createStore } from './store/index'
import { wxLogin } from './api/auth'

App<IAppOption>({
  globalData: {
    userInfo: null,
    token: null,
    openid: null,
  },
  store: createStore(),

  onLaunch() {
    // 检查登录态
    this.checkLogin()
    // 获取系统信息
    this.getSystemInfo()
  },

  /**
   * 启动时检查本地登录态。
   * - 有 token + userInfo：直接复用，等到接口 401 时由 request.ts 触发 refresh
   * - 无登录态：静默调用 wx.login + /api/auth/wxlogin 自动登录
   */
  checkLogin() {
    const token = wx.getStorageSync('token')
    const userInfo = wx.getStorageSync('userInfo')
    if (token && userInfo) {
      this.globalData.token = token
      this.globalData.userInfo = userInfo
      return
    }
    // 静默登录
    wxLogin().catch((err) => {
      console.warn('[Auth] 自动登录失败:', err)
    })
  },

  getSystemInfo() {
    wx.getSystemInfo({
      success: (res) => {
        this.globalData.systemInfo = res
        this.globalData.statusBarHeight = res.statusBarHeight
      }
    })
  },

  // 全局错误处理
  handleError(err, apiName) {
    console.error(`[API Error] ${apiName}:`, err)
    if (err.errno === 401 || err.code === 401) {
      // token 过期，清除登录态（request.ts 已自动尝试过 refresh）
      wx.removeStorageSync('token')
      wx.removeStorageSync('refresh_token')
      wx.removeStorageSync('userInfo')
      wx.showToast({ title: '登录已过期，请重新登录', icon: 'none' })
      setTimeout(() => {
        wx.navigateTo({ url: '/pages/index/index' })
      }, 1500)
    } else {
      wx.showToast({ title: err.message || '请求失败', icon: 'none' })
    }
  }
})
