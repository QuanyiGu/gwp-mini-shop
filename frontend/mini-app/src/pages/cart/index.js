// pages/cart/index.js - 购物车页面
import { cartApi, orderApi, addressApi } from '../../api/request'

Page({
  data: {
    cartList: [] as any[],
    selectedAll: false,
    totalAmount: 0,
    totalCount: 0,
    hasAddress: false,
    address: null as any,
    loading: false,
  },
  
  onShow() {
    if (this.checkLogin()) {
      this.loadCartList()
      this.loadDefaultAddress()
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
  
  async loadCartList() {
    this.setData({ loading: true })
    try {
      const list = await cartApi.getCartList()
      // 计算总金额
      const selectedItems = list.filter((item: any) => item.selected)
      const totalAmount = selectedItems.reduce(
        (sum: number, item: any) => sum + item.product.price * item.quantity, 
        0
      )
      const totalCount = selectedItems.reduce(
        (sum: number, item: any) => sum + item.quantity, 
        0
      )
      const selectedAll = list.length > 0 && selectedItems.length === list.length
      
      this.setData({ 
        cartList: list, 
        totalAmount, 
        totalCount,
        selectedAll,
        loading: false 
      })
    } catch (e) {
      this.setData({ loading: false })
    }
  },
  
  async loadDefaultAddress() {
    try {
      const address = await addressApi.getDefaultAddress()
      this.setData({ address, hasAddress: true })
    } catch (e) {
      this.setData({ hasAddress: false })
    }
  },
  
  // 选择单个商品
  onSelectItem(e: any) {
    const { id } = e.currentTarget.dataset
    const { cartList } = this.data
    const item = cartList.find((c: any) => c.id === id)
    if (item) {
      item.selected = !item.selected
      this.recalculate()
    }
  },
  
  // 全选/取消全选
  onSelectAll() {
    const { selectedAll, cartList } = this.data
    const newSelected = !selectedAll
    cartList.forEach((item: any) => item.selected = newSelected)
    this.recalculate()
  },
  
  // 增减数量
  onChangeQuantity(e: any) {
    const { id, type } = e.currentTarget.dataset
    const { cartList } = this.data
    const item = cartList.find((c: any) => c.id === id)
    if (!item) return
    
    const newQty = type === 'add' ? item.quantity + 1 : item.quantity - 1
    if (newQty < 1) return
    
    item.quantity = newQty
    this.recalculate()
    
    // 更新服务器
    cartApi.updateCart({ id, quantity: newQty }).catch(() => {
      this.loadCartList()  // 失败时重新加载
    })
  },
  
  // 删除
  onDelete(e: any) {
    const { id } = e.currentTarget.dataset
    wx.showModal({
      title: '确认删除',
      content: '确定要删除该商品吗？',
      success: (res) => {
        if (res.confirm) {
          cartApi.removeCart(id).then(() => {
            this.loadCartList()
          })
        }
      }
    })
  },
  
  recalculate() {
    const { cartList } = this.data
    const selectedItems = cartList.filter((item: any) => item.selected)
    const totalAmount = selectedItems.reduce(
      (sum: number, item: any) => sum + item.product.price * item.quantity, 
      0
    )
    const totalCount = selectedItems.reduce(
      (sum: number, item: any) => sum + item.quantity, 
      0
    )
    const selectedAll = cartList.length > 0 && selectedItems.length === cartList.length
    
    this.setData({ cartList, totalAmount, totalCount, selectedAll })
  },
  
  // 去结算
  async onCheckout() {
    const { cartList, address } = this.data
    const selectedItems = cartList.filter((item: any) => item.selected)
    
    if (selectedItems.length === 0) {
      wx.showToast({ title: '请选择商品', icon: 'none' })
      return
    }
    
    if (!address) {
      wx.showToast({ title: '请先添加收货地址', icon: 'none' })
      return
    }
    
    // 跳转到确认订单页（简化版，直接创建）
    wx.navigateTo({ url: `/pages/orderDetail/index?from=cart` })
  },
  
  // 选择地址
  goAddress() {
    wx.navigateTo({ url: '/pages/address/index' })
  },
})
