/**
 * GWP小店 - 认证 API
 * 对接后端 /api/auth/*
 */

interface UserInfoBrief {
  uid: string
  nickname: string
  avatar_url: string
  phone: string
}

interface WxLoginResp {
  access_token: string
  refresh_token: string
  user_info: UserInfoBrief
}

interface RefreshResp {
  access_token: string
}

interface BizResponse<T> {
  code: number
  message: string
  data: T
}

const BASE_URL = 'https://api.gwp-shop.com'  // TODO: 与 request.ts 保持一致

/**
 * 直接调用 wx.request，不走 request.ts 的包装
 * （避免触发 401 拦截造成无限递归）
 */
function rawPost<T>(path: string, body: Record<string, any>): Promise<BizResponse<T>> {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${BASE_URL}${path}`,
      method: 'POST',
      data: body,
      header: { 'Content-Type': 'application/json' },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data as BizResponse<T>)
        } else {
          reject({ errno: res.statusCode, message: '请求失败' })
        }
      },
      fail: (err) => reject(err),
    })
  })
}

/**
 * 微信登录：wx.login 拿 code → 调后端 /api/auth/wxlogin
 * 成功后把 access_token / refresh_token / user_info 写入 storage
 */
export function wxLogin(extra?: { nickname?: string; avatar_url?: string }): Promise<UserInfoBrief> {
  return new Promise((resolve, reject) => {
    wx.login({
      success: async (loginRes) => {
        if (!loginRes.code) {
          return reject({ message: '获取微信 code 失败' })
        }
        try {
          const resp = await rawPost<WxLoginResp>('/api/auth/wxlogin', {
            code: loginRes.code,
            nickname: extra?.nickname || '',
            avatar_url: extra?.avatar_url || '',
          })
          if (resp.code !== 0) {
            return reject({ code: resp.code, message: resp.message })
          }
          const data = resp.data
          wx.setStorageSync('token', data.access_token)
          wx.setStorageSync('refresh_token', data.refresh_token)
          wx.setStorageSync('userInfo', data.user_info)
          const app = getApp<IAppOption>()
          if (app) {
            app.globalData.token = data.access_token
            app.globalData.userInfo = data.user_info as any
          }
          resolve(data.user_info)
        } catch (err) {
          reject(err)
        }
      },
      fail: (err) => reject(err),
    })
  })
}

/**
 * 用 refresh_token 换取新的 access_token
 * 失败返回 null（外层应触发重新登录）
 */
export function refreshAccessToken(): Promise<string | null> {
  const refresh = wx.getStorageSync('refresh_token')
  if (!refresh) return Promise.resolve(null)

  return rawPost<RefreshResp>('/api/auth/refresh', { refresh_token: refresh })
    .then((resp) => {
      if (resp.code !== 0) {
        wx.removeStorageSync('refresh_token')
        return null
      }
      const newAccess = resp.data.access_token
      wx.setStorageSync('token', newAccess)
      const app = getApp<IAppOption>()
      if (app) app.globalData.token = newAccess
      return newAccess
    })
    .catch(() => null)
}

export const authApi = { wxLogin, refreshAccessToken }
export default authApi
