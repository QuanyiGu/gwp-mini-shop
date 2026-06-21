// pages/coupon/index.js - 优惠券列表页面
import { couponApi } from '../../api/request'

Page({
  data: {
    tabs: [
      { key: 'available', text: '可使用' },
      { key: 'used', text: '已使用' },
      { key: 'expired', text: '已过期' },
    ],
    activeTab: 'available',
    couponList: [] as any[],
    loading: false,
    // 领取优惠券弹窗
    showReceiveModal: false,
    receiveCode: '',
  },

  onLoad(options: any) {
    // 支持从订单页跳转时自动选中可用标签
    if (options.select === 'available') {
      this.setData({ activeTab: 'available' })
    }
  },

  onShow() {
    if (this.checkLogin()) {
      this.loadCouponList()
    }
  },

  checkLogin(): boolean {
    const token = wx.getStorageSync('token')
    if (!token) {
      wx.showToast({ title: '请先登录', icon: 'none' })
      setTimeout(() => wx.navigateTo({ url: '/pages/index/index' }), 1000)
      return false
    }
    return true
  },

  // 切换标签
  onTabChange(e: any) {
    const key = e.currentTarget.dataset.key
    this.setData({ activeTab: key })
    this.loadCouponList()
  },

  // 加载优惠券列表
  async loadCouponList() {
    this.setData({ loading: true })
    try {
      let status: number | undefined
      if (this.data.activeTab === 'used') {
        status = 1  // 已使用
      } else if (this.data.activeTab === 'expired') {
        status = 2  // 已过期
      } else {
        status = 0  // 未使用/可使用
      }
      
      const list = await couponApi.getCouponList({ status })
      
      // 过滤显示 - 按状态过滤，确保只显示对应状态的优惠券
      const filteredList = list.filter((item: any) => {
        // 确保优惠券有有效时间字段
        if (!item.expires_at) return false
        
        const now = Date.now()
        const expireTime = new Date(item.expires_at).getTime()
        
        if (this.data.activeTab === 'available') {
          // 可使用：status=0 且未过期
          return item.status === 0 && expireTime > now
        } else if (this.data.activeTab === 'used') {
          // 已使用：status=1
          return item.status === 1
        } else {
          // 已过期：status=2 或 (status=0 且已过期)
          return item.status === 2 || (item.status === 0 && expireTime <= now)
        }
      })
      
      // 按到期时间排序
      filteredList.sort((a: any, b: any) => 
        new Date(a.expires_at).getTime() - new Date(b.expires_at).getTime()
      )
      
      this.setData({ couponList: filteredList, loading: false })
    } catch (e) {
      console.error('加载优惠券失败:', e)
      this.setData({ loading: false })
      wx.showToast({ title: '加载失败', icon: 'none' })
    }
  },

  // 显示领取弹窗
  onShowReceive() {
    this.setData({ showReceiveModal: true, receiveCode: '' })
  },

  // 关闭领取弹窗
  onCloseReceive() {
    this.setData({ showReceiveModal: false })
  },

  // 输入兑换码
  onCodeInput(e: any) {
    this.setData({ receiveCode: e.detail.value.toUpperCase() })
  },

  // 领取优惠券
  async onReceive() {
    const code = this.data.receiveCode.trim()
    if (!code) {
      wx.showToast({ title: '请输入兑换码', icon: 'none' })
      return
    }

    try {
      wx.showLoading({ title: '领取中...' })
      await couponApi.receiveCoupon(code)
      wx.hideLoading()
      wx.showToast({ title: '领取成功！' })
      this.setData({ showReceiveModal: false })
      this.loadCouponList()
    } catch (e: any) {
      wx.hideLoading()
      const msg = e?.message || e?.msg || '领取失败，请检查兑换码'
      wx.showToast({ title: msg, icon: 'none' })
    }
  },

  // 使用优惠券 - 点击优惠券卡片
  onUseCoupon(e: any) {
    const { coupon } = e.currentTarget.dataset
    
    // 只有可使用状态的优惠券才能点击
    if (this.data.activeTab !== 'available') {
      return
    }
    
    // 可以选择返回上一页并携带优惠券信息
    // 或者直接跳转到商城页面
    const pages = getCurrentPages()
    if (pages.length > 1) {
      // 如果是从订单页过来的，返回并传递选中的优惠券
      const prevPage = pages[pages.length - 2]
      if (prevPage && prevPage.route === 'pages/order/index') {
        // 设置返回数据
        wx.setStorageSync('selectedCoupon', coupon)
        wx.navigateBack()
        return
      }
    }
    
    // 默认跳转到商品列表
    wx.showToast({ title: '去购物使用优惠券', icon: 'none' })
    setTimeout(() => {
      wx.switchTab({ url: '/pages/index/index' })
    }, 1000)
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.loadCouponList().finally(() => {
      wx.stopPullDownRefresh()
    })
  },
})
