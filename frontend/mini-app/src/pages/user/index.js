// pages/user/index.js - 个人中心
import { userApi } from '../../api/request'

Page({
  data: {
    userInfo: null,
    menuItems: [
      { icon: '🎫', label: '我的优惠券', path: '/pages/coupon/index' },
      { icon: '📍', label: '收货地址', path: '/pages/address/index' },
      { icon: '🎁', label: '邀请有礼', action: 'onInvite' },
      { icon: '❓', label: '帮助中心', path: '' },
    ],
    orderStats: {
      pending: 0,
      paid: 0,
      shipped: 0,
      completed: 0
    }
  },

  onShow() {
    const userInfo = wx.getStorageSync('userInfo')
    this.setData({ userInfo })
    // 加载订单统计
    this.loadOrderStats()
  },

  async loadOrderStats() {
    // TODO: 调用接口获取订单统计
    // 暂时使用模拟数据
    this.setData({
      orderStats: {
        pending: 0,
        paid: 0,
        shipped: 0,
        completed: 0
      }
    })
  },

  onLogin() {
    if (wx.getStorageSync('token')) {
      wx.showToast({ title: '已登录', icon: 'none' })
      return
    }
    // 使用 wx.login 进行静默登录
    wx.login({
      success: async (res) => {
        if (res.code) {
          try {
            // 登录逻辑在 auth.ts 中处理
            const userInfo = wx.getStorageSync('userInfo')
            if (userInfo) {
              this.setData({ userInfo })
              wx.showToast({ title: '登录成功', icon: 'success' })
            }
          } catch (err) {
            console.error('登录失败:', err)
          }
        }
      }
    })
  },

  goOrderList(e) {
    const { status } = e.currentTarget.dataset
    const url = status !== undefined 
      ? `/pages/order/index?status=${status}` 
      : '/pages/order/index'
    wx.navigateTo({ url })
  },

  goMenuItem(e) {
    const { path, action } = e.currentTarget.dataset
    
    if (action) {
      // 调用方法
      this[action]()
      return
    }
    
    if (!path) {
      wx.showToast({ title: '功能开发中', icon: 'none' })
      return
    }
    wx.navigateTo({ url: path })
  },

  async onInvite() {
    try {
      const res = await userApi.getInviteCode()
      wx.setClipboardData({ 
        data: res.invite_code,
        success: () => {
          wx.showToast({ title: '邀请码已复制', icon: 'success' })
        }
      })
    } catch (err) {
      wx.showToast({ title: '获取邀请码失败', icon: 'none' })
    }
  },

  onLogout() {
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          wx.removeStorageSync('token')
          wx.removeStorageSync('userInfo')
          wx.removeStorageSync('refresh_token')
          this.setData({ userInfo: null })
          wx.showToast({ title: '已退出登录', icon: 'success' })
        }
      }
    })
  }
})
