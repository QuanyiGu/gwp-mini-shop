/**
 * GWP小店 - 简易状态管理
 * 替换为 Minute 小程序状态管理 或 Taro Redux
 */

// 简易事件总线 + 响应式存储
type Listener = () => void

class Store {
  private state: Record<string, any> = {}
  private listeners: Map<string, Set<Listener>> = new Map()
  
  constructor(initialState: Record<string, any> = {}) {
    this.state = initialState
  }
  
  // 获取状态
  get(key: string): any {
    return this.state[key]
  }
  
  // 设置状态（触发更新）
  set(key: string, value: any): void {
    const oldValue = this.state[key]
    if (oldValue !== value) {
      this.state[key] = value
      this.notify(key)
    }
  }
  
  // 批量设置
  setState(newState: Record<string, any>): void {
    let changed = false
    for (const key in newState) {
      if (this.state[key] !== newState[key]) {
        this.state[key] = newState[key]
        changed = true
      }
    }
    if (changed) {
      for (const key in newState) {
        this.notify(key)
      }
    }
  }
  
  // 订阅状态变化
  subscribe(key: string, listener: Listener): () => void {
    if (!this.listeners.has(key)) {
      this.listeners.set(key, new Set())
    }
    this.listeners.get(key)!.add(listener)
    
    // 返回取消订阅函数
    return () => {
      this.listeners.get(key)?.delete(listener)
    }
  }
  
  // 通知所有监听器
  private notify(key: string): void {
    const listeners = this.listeners.get(key)
    if (listeners) {
      listeners.forEach(listener => listener())
    }
    // 同时通知全局监听器（*）
    const globalListeners = this.listeners.get('*')
    if (globalListeners) {
      globalListeners.forEach(listener => listener())
    }
  }
}

// 创建全局 Store 实例
export function createStore(): Store {
  return new Store({
    // 购物车数量
    cartCount: 0,
    // 用户信息
    userInfo: null,
    // 选中的地址
    selectedAddress: null,
    // 选中的优惠券
    selectedCoupon: null,
  })
}

export { Store }
