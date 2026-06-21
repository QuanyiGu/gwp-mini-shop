/**
 * GWP小店 - 类型定义
 */

// 用户信息
interface UserInfo {
  id: number
  uid: string
  openid?: string
  unionid?: string
  nickname?: string
  avatar_url?: string
  phone?: string
  created_at: string
}

// 分类
interface Category {
  id: number
  name: string
  icon: string
  sort: number
}

// 商品
interface Product {
  id: number
  category_id: number
  name: string
  main_image: string
  images?: string[]
  description?: string
  price: number
  original_price: number
  stock: number
  sales: number
  status: number
}

// Banner
interface Banner {
  id: number
  type: string
  title: string
  content: string
  status: number
}

// 收货地址
interface Address {
  id: number
  user_id: number
  name: string
  phone: string
  province: string
  city: string
  district: string
  detail: string
  is_default: number
}

// 购物车项
interface CartItem {
  id: number
  product_id: number
  product: Product
  quantity: number
  selected: boolean
}

// 订单
interface Order {
  id: number
  order_no: string
  user_id: number
  total_amount: number
  pay_amount: number
  address_name: string
  address_phone: string
  address_detail: string
  status: number
  gift_package: number
  greeting_card?: string
  logistics_company?: string
  logistics_no?: string
  created_at: string
}

// 订单详情
interface OrderDetail extends Order {
  items: OrderItem[]
  coupon?: Coupon
}

// 订单商品项
interface OrderItem {
  id: number
  product_id: number
  product_name: string
  product_image: string
  price: number
  quantity: number
  total_price: number
}

// 优惠券
interface Coupon {
  id: number
  code: string
  user_id: number
  type: number
  discount: number
  min_amount: number
  status: number
  expires_at: string
}

// 分页结果
interface PageResult<T> {
  list: T[]
  total: number
  page: number
  page_size: number
}

// App 全局数据
interface IAppOption {
  globalData: {
    userInfo: UserInfo | null
    token: string | null
    openid: string | null
    systemInfo?: wx.SystemInfo
    statusBarHeight?: number
  }
  store: any
  checkLogin(): void
  getSystemInfo(): void
  handleError(err: any, apiName: string): void
}
