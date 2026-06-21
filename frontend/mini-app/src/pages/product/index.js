// pages/product/index.js
import { productApi, cartApi } from '../../api/request'

Page({
  data: {
    product: null as any,
    extra: null as any,
    quantity: 1,
    images: [] as string[],
    activeImageIndex: 0,
    loading: true,
    showQuantityModal: false,
    actionMode: 'cart', // 'cart' | 'buy'
    cartCount: 0,
  },

  onLoad(query: any) {
    if (query.id) {
      this.loadProduct(Number(query.id))
    }
    this.updateCartCount()
  },

  onShow() {
    this.updateCartCount()
  },

  async loadProduct(id: number) {
    this.setData({ loading: true })
    try {
      const product = await productApi.getProductDetail(id)
      const images = product.images ? JSON.parse(product.images) : [product.main_image]
      this.setData({
        product,
        images,
        loading: false,
      })
      wx.setNavigationBarTitle({ title: product.name })
    } catch {
      this.setData({ loading: false })
      wx.showToast({ title: '加载失败', icon: 'none' })
    }
  },

  onImageChange(e: any) {
    this.setData({ activeImageIndex: e.detail.current })
  },

  previewImages(e: any) {
    const { current } = e.currentTarget.dataset
    const { images } = this.data
    wx.previewImage({
      urls: images,
      current: images[current],
    })
  },

  changeQuantity(e: any) {
    const { type } = e.currentTarget.dataset
    const { quantity, product } = this.data
    if (type === 'add' && quantity < product.stock) {
      this.setData({ quantity: quantity + 1 })
    } else if (type === 'sub' && quantity > 1) {
      this.setData({ quantity: quantity - 1 })
    }
  },

  onAddToCart() {
    this.setData({ actionMode: 'cart', showQuantityModal: true })
  },

  onBuyNow() {
    this.setData({ actionMode: 'buy', showQuantityModal: true })
  },

  closeQuantityModal() {
    this.setData({ showQuantityModal: false })
  },

  stopPropagation() {
    // 阻止冒泡
  },

  async confirmQuantity() {
    const { actionMode, product, quantity } = this.data

    if (actionMode === 'cart') {
      await this.addToCart()
    } else {
      this.buyNow()
    }

    this.closeQuantityModal()
  },

  async addToCart() {
    const { product, quantity } = this.data
    if (!product) return

    try {
      const res = await cartApi.addToCart({ product_id: product.id, quantity })
      wx.showToast({ title: '已加入购物车', icon: 'success' })
      this.setData({ cartCount: res.count })
      // 更新 tabBar badge
      wx.setTabBarBadge({ index: 1, text: String(res.count) })
    } catch {
      // error handled in api
    }
  },

  buyNow() {
    const { product, quantity } = this.data
    if (!product) return
    // 直接购买：保存到全局，跳转到确认订单
    wx.navigateTo({ url: `/pages/orderDetail/index?from=buy&product_id=${product.id}&quantity=${quantity}` })
  },

  goHome() {
    wx.switchTab({ url: '/pages/index/index' })
  },

  goCart() {
    wx.switchTab({ url: '/pages/cart/index' })
  },

  updateCartCount() {
    const count = wx.getStorageSync('cartCount') || 0
    this.setData({ cartCount: count })
    if (count > 0) {
      wx.setTabBarBadge({
        index: 1,
        text: String(count),
      })
    } else {
      wx.removeTabBarBadge({ index: 1 })
    }
  },
})
