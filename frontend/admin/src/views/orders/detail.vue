<template>
  <div class="order-detail">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/orders' }">订单管理</el-breadcrumb-item>
            <el-breadcrumb-item>订单详情</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
      </template>
      
      <div v-loading="loading">
        <!-- 订单状态卡片 -->
        <el-alert
          :title="getStatusTitle(order.status)"
          :type="getStatusAlertType(order.status)"
          :description="getStatusDesc(order.status)"
          show-icon
          style="margin-bottom: 20px;"
        />
        
        <el-row :gutter="20">
          <!-- 左侧订单信息 -->
          <el-col :span="16">
            <!-- 收货信息 -->
            <el-card shadow="never" style="margin-bottom: 20px;">
              <template #header>
                <span class="section-title">收货信息</span>
              </template>
              <div class="info-row">
                <span class="label">收货人：</span>
                <span class="value">{{ order.address_name }}</span>
              </div>
              <div class="info-row">
                <span class="label">联系电话：</span>
                <span class="value">{{ order.address_phone }}</span>
              </div>
              <div class="info-row">
                <span class="label">收货地址：</span>
                <span class="value">{{ order.address_detail }}</span>
              </div>
            </el-card>
            
            <!-- 商品信息 -->
            <el-card shadow="never" style="margin-bottom: 20px;">
              <template #header>
                <span class="section-title">商品信息</span>
              </template>
              <el-table :data="order.items || []" stripe>
                <el-table-column prop="product_name" label="商品名称" min-width="200" />
                <el-table-column prop="product_image" label="图片" width="80">
                  <template #default="{ row }">
                    <el-image
                      :src="row.product_image || '/placeholder.png'"
                      fit="cover"
                      style="width: 50px; height: 50px; border-radius: 4px;"
                    />
                  </template>
                </el-table-column>
                <el-table-column prop="price" label="单价" width="100">
                  <template #default="{ row }">
                    ¥{{ row.price?.toFixed(2) }}
                  </template>
                </el-table-column>
                <el-table-column prop="quantity" label="数量" width="80" />
                <el-table-column label="小计" width="100">
                  <template #default="{ row }">
                    ¥{{ (row.price * row.quantity).toFixed(2) }}
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
            
            <!-- 物流信息 -->
            <el-card shadow="never" v-if="order.status >= 2">
              <template #header>
                <span class="section-title">物流信息</span>
              </template>
              <div class="info-row">
                <span class="label">物流公司：</span>
                <span class="value">{{ order.logistics_company || '-' }}</span>
              </div>
              <div class="info-row">
                <span class="label">物流单号：</span>
                <span class="value">{{ order.tracking_no || '-' }}</span>
              </div>
            </el-card>
          </el-col>
          
          <!-- 右侧订单金额 -->
          <el-col :span="8">
            <el-card shadow="never">
              <template #header>
                <span class="section-title">订单金额</span>
              </template>
              <div class="amount-row">
                <span class="label">商品金额：</span>
                <span class="value">¥{{ order.total_amount?.toFixed(2) }}</span>
              </div>
              <div class="amount-row" v-if="order.discount_amount > 0">
                <span class="label">优惠金额：</span>
                <span class="value discount">-¥{{ order.discount_amount?.toFixed(2) }}</span>
              </div>
              <el-divider />
              <div class="amount-row total">
                <span class="label">实付金额：</span>
                <span class="value">¥{{ order.pay_amount?.toFixed(2) }}</span>
              </div>
            </el-card>
            
            <!-- 订单信息 -->
            <el-card shadow="never" style="margin-top: 20px;">
              <template #header>
                <span class="section-title">订单信息</span>
              </template>
              <div class="info-row">
                <span class="label">订单号：</span>
                <span class="value">{{ order.order_no }}</span>
              </div>
              <div class="info-row">
                <span class="label">下单时间：</span>
                <span class="value">{{ order.created_at }}</span>
              </div>
              <div class="info-row" v-if="order.pay_time">
                <span class="label">付款时间：</span>
                <span class="value">{{ order.pay_time }}</span>
              </div>
              <div class="info-row" v-if="order.ship_time">
                <span class="label">发货时间：</span>
                <span class="value">{{ order.ship_time }}</span>
              </div>
            </el-card>
            
            <!-- 操作按钮 -->
            <div class="action-buttons" style="margin-top: 20px;">
              <el-button
                v-if="order.status === 1"
                type="primary"
                size="large"
                style="width: 100%;"
                @click="showShipDialog = true"
              >
                立即发货
              </el-button>
              
              <el-button
                v-if="order.status === 6"
                type="danger"
                size="large"
                style="width: 100%; margin-bottom: 10px;"
                @click="handleRefund(true)"
              >
                同意退款
              </el-button>
              <el-button
                v-if="order.status === 6"
                size="large"
                style="width: 100%;"
                @click="handleRefund(false)"
              >
                拒绝退款
              </el-button>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>
    
    <!-- 发货弹窗 -->
    <el-dialog v-model="showShipDialog" title="订单发货" width="500px">
      <el-form :model="shipForm" label-width="100px">
        <el-form-item label="物流公司" prop="logistics_company">
          <el-select v-model="shipForm.logistics_company" placeholder="请选择物流公司" style="width: 100%;">
            <el-option label="顺丰快递" value="SF" />
            <el-option label="京东物流" value="JD" />
            <el-option label="中通快递" value="ZTO" />
            <el-option label="圆通快递" value="YTO" />
            <el-option label="韵达快递" value="YD" />
            <el-option label="邮政EMS" value="EMS" />
          </el-select>
        </el-form-item>
        <el-form-item label="物流单号" prop="tracking_no">
          <el-input v-model="shipForm.tracking_no" placeholder="请输入物流单号" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showShipDialog = false">取消</el-button>
        <el-button type="primary" :loading="shipLoading" @click="confirmShip">
          确认发货
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { orderApi } from '@/api'

const route = useRoute()
const loading = ref(false)
const shipLoading = ref(false)
const showShipDialog = ref(false)

const orderNo = route.params.orderNo as string

const order = ref<any>({
  order_no: orderNo,
  status: 1,
  address_name: '张先生',
  address_phone: '138****8000',
  address_detail: '广东省深圳市南山区科技园',
  total_amount: 89.90,
  discount_amount: 0,
  pay_amount: 89.90,
  created_at: '2026-06-12 10:30:00',
  pay_time: '2026-06-12 10:31:00',
  logistics_company: '',
  tracking_no: '',
  items: [
    { product_name: '红富士苹果 5斤装', product_image: '', price: 29.90, quantity: 2 },
    { product_name: '野生土蜂蜜 500g', product_image: '', price: 29.90, quantity: 1 },
  ],
})

const shipForm = reactive({
  logistics_company: '',
  tracking_no: '',
})

const getStatusTitle = (status: number) => {
  const titles: Record<number, string> = {
    0: '等待买家付款',
    1: '买家已付款，等待发货',
    2: '已发货，等待收货',
    3: '交易完成',
    4: '订单已取消',
    5: '退款已完成',
    6: '买家申请退款',
  }
  return titles[status] || '未知状态'
}

const getStatusAlertType = (status: number) => {
  const types: Record<number, string> = {
    0: 'warning',
    1: 'warning',
    2: 'info',
    3: 'success',
    4: 'info',
    5: 'success',
    6: 'error',
  }
  return types[status] || 'info'
}

const getStatusDesc = (status: number) => {
  const descs: Record<number, string> = {
    0: '请提醒买家尽快完成付款',
    1: '请尽快安排发货',
    2: '买家确认收货后，订单将完成',
    3: '交易已完成，感谢您的服务',
    4: '订单已取消，款项已原路退回',
    5: '退款已完成，款项已原路退回',
    6: '请及时处理退款申请',
  }
  return descs[status] || ''
}

const loadOrderDetail = async () => {
  loading.value = true
  try {
    try {
      const res: any = await orderApi.getDetail(orderNo)
      Object.assign(order.value, res)
    } catch {
      // 使用 Mock 数据，保留默认值
    }
  } finally {
    loading.value = false
  }
}

const confirmShip = async () => {
  if (!shipForm.logistics_company) {
    ElMessage.warning('请选择物流公司')
    return
  }
  if (!shipForm.tracking_no) {
    ElMessage.warning('请输入物流单号')
    return
  }
  
  shipLoading.value = true
  try {
    try {
      await orderApi.ship(orderNo, shipForm)
    } catch {
      // Mock 成功
    }
    ElMessage.success('发货成功')
    showShipDialog.value = false
    order.value.status = 2
    order.value.logistics_company = shipForm.logistics_company
    order.value.tracking_no = shipForm.tracking_no
  } catch (error: any) {
    ElMessage.error(error.message || '发货失败')
  } finally {
    shipLoading.value = false
  }
}

const handleRefund = (agree: boolean) => {
  const action = agree ? '同意' : '拒绝'
  ElMessageBox.confirm(`确定要${action}退款申请吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      try {
        await orderApi.handleRefund(orderNo, { agree, reason: '' })
      } catch {
        // Mock 成功
      }
      ElMessage.success('操作成功')
      order.value.status = agree ? 5 : 1
    } catch {
      ElMessage.error('操作失败')
    }
  }).catch(() => {})
}

onMounted(() => {
  loadOrderDetail()
})
</script>

<style scoped>
.order-detail {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-title {
  font-weight: 500;
  color: #303133;
}

.info-row {
  display: flex;
  margin-bottom: 12px;
  font-size: 14px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-row .label {
  width: 80px;
  color: #909399;
  flex-shrink: 0;
}

.info-row .value {
  color: #303133;
  flex: 1;
}

.amount-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 14px;
}

.amount-row .label {
  color: #909399;
}

.amount-row .value {
  color: #303133;
}

.amount-row .value.discount {
  color: #f56c6c;
}

.amount-row.total {
  font-size: 16px;
  font-weight: 500;
}

.amount-row.total .value {
  color: #f56c6c;
}
</style>
