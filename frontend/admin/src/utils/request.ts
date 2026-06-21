// src/utils/request.ts
import axios from 'axios'
import { ElMessage } from 'element-plus'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'

const request = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('admin_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.code === 0 || res.code === 200) {
      return res.data
    } else {
      ElMessage.error(res.message || res.msg || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
  },
  (error) => {
    if (error.response?.status === 401) {
      ElMessage.error('登录已过期，请重新登录')
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_user')
      window.location.href = '/#/login'
    } else {
      ElMessage.error(error.message || '网络错误')
    }
    return Promise.reject(error)
  }
)

export default request
