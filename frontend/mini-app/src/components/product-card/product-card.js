// components/product-card/product-card.js
import { cartApi } from '../../api/request'

Component({
  properties: {
    product: {
      type: Object,
      value: {}
    }
  },

  methods: {
    onTap() {
      const { id } = this.properties.product
      wx.navigateTo({
        url: `/pages/product/index?id=${id}`
      })
    },

    async onAddCart(e) {
      e.stopPropagation()
      const { id, stock } = this.properties.product
      
      if (stock <= 0) {
        wx.showToast({ title: '商品已售罄', icon: 'none' })
        return
      }

      try {
        await cartApi.add({ product_id: id, quantity: 1 })
        wx.showToast({ title: '已加入购物车', icon: 'success' })
        // 触发事件通知父页面更新购物车数量
        this.triggerEvent('cartUpdated')
      } catch (err) {
        console.error('加入购物车失败:', err)
        wx.showToast({ title: err.message || '加入失败', icon: 'none' })
      }
    }
  }
})
