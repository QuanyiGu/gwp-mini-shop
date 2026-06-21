// src/store/index.ts
import { defineStore } from 'pinia'

interface UserState {
  token: string
  userInfo: any
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    token: localStorage.getItem('admin_token') || '',
    userInfo: JSON.parse(localStorage.getItem('admin_user') || 'null'),
  }),
  
  actions: {
    setToken(token: string) {
      this.token = token
      localStorage.setItem('admin_token', token)
    },
    
    setUserInfo(userInfo: any) {
      this.userInfo = userInfo
      localStorage.setItem('admin_user', JSON.stringify(userInfo))
    },
    
    logout() {
      this.token = ''
      this.userInfo = null
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_user')
    },
  },
})
