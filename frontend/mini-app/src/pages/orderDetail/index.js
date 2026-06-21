// pages/orderDetail/index.js - 订单确认/详情页
import { orderApi, addressApi, productApi, cartApi, wxpayApi } from '../../api/request'

Page({
  data: {
    from: 'cart',       // cart | buy
    product: null,      // 直接购买时的商品
    quantity: 1,
    address: null,
    items: [] as any[],
    coupon: null,
    giftPackage: 0,
    greetingCard: '',
    remark: '',
    totalAmount: 0,
    payAmount: 0,
    loading: false,
  },
  
  onLoad(query: any) {
    this.setData({ from: query.from || 'cart' })
    
    if (query.from === 'buy' && query.product_id) {
      this.loadProduct(Number(query.product_id), Number(query.quantity))
    } else {
      this.loadCartData()
    }
    this.loadAddress()
  },
  
  async loadProduct(productId: number, quantity: number) {
    const product = await productApi.getProductDetail(productId)
    const items = [{
      product_id: product.id,
      product,
      quantity,
      selected: true,
    }]
    const totalAmount = product.price * quantity
    this.setData({ product, quantity, items, totalAmount, payAmount: totalAmount })
  },
  
  async loadCartData() {
    try {
      const cartList = await cartApi.getCartList()
      const selected = cartList.filter((item: any) => item.selected)
      if (selected.length === 0) {
        wx.showToast({ title: '请选择商品', icon: 'none' })
        return
      }
      const items = selected
      const totalAmount = selected.reduce(
        (sum: number, item: any) => sum + item.product.price * item.quantity, 0
      )
      this.setData({ items, totalAmount, payAmount: totalAmount })
    } catch {}
  },
  
  async loadAddress() {
    try {
      const address = await addressApi.getDefaultAddress()
      this.setData({ address })
    } catch {
      wx.showToast({ title: '请先添加收货地址', icon: 'none' })
    }
  },
  
  onGreetingInput(e: any) {
    this.setData({ greetingCard: e.detail.value })
  },
  
  onRemarkInput(e: any) {
    this.setData({ remark: e.detail.value })
  },
  
  toggleGiftPackage() {
    this.setData({ giftPackage: this.data.giftPackage ? 0 : 1 })
  },
  
  async onSubmit() {
    const { address, giftPackage, greetingCard, remark, from, items } = this.data
    if (!address) {
      wx.showToast({ title: '请选择收货地址', icon: 'none' })
      return
    }
    
    this.setData({ loading: true })
    try {
      // 1. 创建订单
      const order = await orderApi.createOrder({
        address_id: address.id,
        gift_package: giftPackage,
        greeting_card: greetingCard,
        remark,
      })
      
      // 2. 发起微信支付
      const payData = await wxpayApi.prepay(order.order_no)
      
      // 3. 调用微信支付
      wx.requestPayment({
        ...payData,
        success: () => {
          wx.showToast({ title: '支付成功', icon: 'success' })
          setTimeout(() => {
            wx.redirectTo({ url: `/pages/orderDetail/index?order_no=${order.order_no}` })
          }, 1500)
        },
        fail: () => {
          wx.showToast({ title: '支付取消', icon: 'none' })
        }
      })
    } catch {
      this.setData({ loading: false })
    }
  },
})
