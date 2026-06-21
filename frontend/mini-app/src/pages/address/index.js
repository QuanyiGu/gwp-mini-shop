// pages/address/index.js
import { addressApi } from '../../api/request'

Page({
  data: {
    addressList: [] as any[],
    loading: false,
    showModal: false,
    editingId: 0,
    region: ['', '', ''],
    formData: {
      name: '',
      phone: '',
      province: '',
      city: '',
      district: '',
      detail: '',
      is_default: false,
    } as any,
    primaryColor: '#07c160',
  },

  onLoad() {
    this.loadAddressList()
  },

  onShow() {
    this.loadAddressList()
  },

  async loadAddressList() {
    this.setData({ loading: true })
    try {
      const list = await addressApi.getAddressList()
      this.setData({ addressList: list, loading: false })
    } catch {
      this.setData({ loading: false })
    }
  },

  showAddModal() {
    this.setData({
      showModal: true,
      editingId: 0,
      region: ['', '', ''],
      formData: {
        name: '',
        phone: '',
        province: '',
        city: '',
        district: '',
        detail: '',
        is_default: false,
      },
    })
  },

  editAddress(e: any) {
    const { id } = e.currentTarget.dataset
    const address = this.data.addressList.find((a: any) => a.id === id)
    if (address) {
      this.setData({
        showModal: true,
        editingId: id,
        region: [address.province, address.city, address.district],
        formData: {
          name: address.name,
          phone: address.phone,
          province: address.province,
          city: address.city,
          district: address.district,
          detail: address.detail,
          is_default: !!address.is_default,
        },
      })
    }
  },

  closeModal() {
    this.setData({ showModal: false })
  },

  stopPropagation() {
    // 阻止冒泡
  },

  onInputChange(e: any) {
    const { field } = e.currentTarget.dataset
    const key = `formData.${field}` as any
    this.setData({ [key]: e.detail.value })
  },

  onRegionChange(e: any) {
    const region = e.detail.value
    this.setData({
      region,
      'formData.province': region[0],
      'formData.city': region[1],
      'formData.district': region[2],
    })
  },

  onSwitchChange(e: any) {
    this.setData({ 'formData.is_default': e.detail.value })
  },

  async submitForm() {
    const { formData, editingId } = this.data

    if (!formData.name.trim()) {
      wx.showToast({ title: '请输入收货人姓名', icon: 'none' })
      return
    }
    if (!/^1[3-9]\d{9}$/.test(formData.phone)) {
      wx.showToast({ title: '请输入正确的手机号', icon: 'none' })
      return
    }
    if (!formData.province) {
      wx.showToast({ title: '请选择所在地区', icon: 'none' })
      return
    }
    if (!formData.detail.trim()) {
      wx.showToast({ title: '请输入详细地址', icon: 'none' })
      return
    }

    try {
      if (editingId) {
        await addressApi.updateAddress(editingId, formData)
        wx.showToast({ title: '更新成功', icon: 'success' })
      } else {
        await addressApi.addAddress(formData)
        wx.showToast({ title: '添加成功', icon: 'success' })
      }
      this.closeModal()
      this.loadAddressList()
    } catch {
      // error handled in api
    }
  },

  async setDefault(e: any) {
    const { id } = e.currentTarget.dataset
    try {
      await addressApi.setDefaultAddress(id)
      wx.showToast({ title: '设置成功', icon: 'success' })
      this.loadAddressList()
    } catch {
      // error handled in api
    }
  },

  async deleteAddress(e: any) {
    const { id } = e.currentTarget.dataset
    wx.showModal({
      title: '确认删除',
      content: '确定要删除该地址吗？',
      success: async (res) => {
        if (res.confirm) {
          try {
            await addressApi.deleteAddress(id)
            wx.showToast({ title: '删除成功', icon: 'success' })
            this.loadAddressList()
          } catch {
            // error handled in api
          }
        }
      },
    })
  },
})
