// pages/order/index.js
import { orderApi } from '../../api/request'

const STATUS_MAP = [
  { key: 'all', label: '全部', value: null },
  { key: '0', label: '待付款', value: 0 },
  { key: '1', label: '待发货', value: 1 },
  { key: '2', label: '待收货', value: 2 },
  { key: '3', label: '已完成', value: 3 },
  { key: 'refund', label: '退款/售后', value: -1 },
]

Page({
  data: {
    tabs: STATUS_MAP,
    activeTab: 0,
    orders: [] as any[],
    page: 1,
    hasMore: true,
    loading: false,
  },
  
  onLoad(query: any) {
    const status = query.status !== undefined ? Number(query.status) : null
    const activeTab = STATUS_MAP.findIndex(t => t.value === status)
    if (activeTab >= 0) {
      this.setData({ activeTab })
    }
  },
  
  onShow() {
    if (wx.getStorageSync('token')) {
      this.loadOrders(true)
    }
  },
  
  onPullDownRefresh() {
    this.loadOrders(true).finally(() => wx.stopPullDownRefresh())
  },
  
  onReachBottom() {
    if (this.data.hasMore) this.loadOrders(false)
  },
  
  switchTab(e: any) {
    const { index } = e.currentTarget.dataset
    this.setData({ activeTab: index, orders: [], page: 1, hasMore: true })
    this.loadOrders(true)
  },
  
  async loadOrders(refresh = false) {
    const { activeTab, tabs, page } = this.data
    const status = tabs[activeTab].value
    
    if (this.data.loading) return
    this.setData({ loading: true })
    
    try {
      const newPage = refresh ? 1 : page
      const res = await orderApi.getOrderList({ 
        status: status ?? undefined,
        page: newPage,
        page_size: 10 
      })
      
      const list = refresh ? res.list : [...this.data.orders, ...res.list]
      this.setData({
        orders: list,
        page: newPage + 1,
        hasMore: list.length < res.total,
        loading: false,
      })
    } catch {
      this.setData({ loading: false })
    }
  },
  
  goDetail(e: any) {
    const { orderno } = e.currentTarget.dataset
    wx.navigateTo({ url: `/pages/orderDetail/index?order_no=${orderno}` })
  },
  
  getStatusName(status: number) {
    const map: Record<number, string> = {
      0: '待付款', 1: '待发货', 2: '待收货', 3: '已完成',
      4: '已取消', 5: '已退款', 6: '退款中'
    }
    return map[status] || '未知'
  },
  
  getStatusClass(status: number) {
    if (status === 0) return 'tag-red'
    if (status === 3) return 'tag-green'
    return ''
  },
})
