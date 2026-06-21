// pages/index/index.js
import { productApi } from '../../api/request'

Page({
  data: {
    banners: [] as any[],
    categories: [] as any[],
    products: [] as any[],
    growthStatus: null as any,
    loading: true,
    activeCategory: 0,
  },
  
  onLoad() {
    this.loadHomeData()
  },
  
  onShow() {
    // 更新购物车数量
    this.updateCartCount()
  },
  
  onPullDownRefresh() {
    this.loadHomeData().finally(() => {
      wx.stopPullDownRefresh()
    })
  },
  
  async loadHomeData() {
    this.setData({ loading: true })
    try {
      const data = await productApi.getHomeData()
      this.setData({
        banners: data.banners || [],
        categories: data.categories || [],
        products: data.products || [],
        growthStatus: data.growth_status || null,
        loading: false,
      })
    } catch (e) {
      this.setData({ loading: false })
    }
  },
  
  // 切换分类
  onCategoryChange(e: any) {
    const { id } = e.currentTarget.dataset
    this.setData({ activeCategory: id })
    if (id === 0) {
      this.loadHomeData()
    } else {
      this.loadCategoryProducts(id)
    }
  },
  
  async loadCategoryProducts(categoryId: number) {
    try {
      const res = await productApi.getProducts({ category_id: categoryId })
      this.setData({ products: res.list })
    } catch (e) {
      // handled in request
    }
  },
  
  // 跳转到商品详情
  goProduct(e: any) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({ url: `/pages/product/index?id=${id}` })
  },
  
  // 跳转到分类页
  goCategory(e: any) {
    const { id } = e.currentTarget.dataset
    wx.navigateTo({ url: `/pages/product/index?category_id=${id}` })
  },
  
  // 搜索
  onSearch() {
    wx.navigateTo({ url: '/pages/product/index' })
  },
  
  updateCartCount() {
    const cartCount = wx.getStorageSync('cartCount') || 0
    if (cartCount > 0) {
      wx.setTabBarBadge({
        index: 1,
        text: String(cartCount),
      })
    } else {
      wx.removeTabBarBadge({ index: 1 })
    }
  },
})
