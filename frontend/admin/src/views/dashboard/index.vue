<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon sales">
              <el-icon><Money /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">今日销售额</p>
              <p class="stat-value">¥{{ stats.today_sales?.toFixed(2) || '0.00' }}</p>
              <p class="stat-growth" :class="stats.sales_growth >= 0 ? 'up' : 'down'">
                {{ stats.sales_growth >= 0 ? '+' : '' }}{{ stats.sales_growth || 0 }}% 较昨日
              </p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon orders">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">今日订单</p>
              <p class="stat-value">{{ stats.today_orders || 0 }}</p>
              <p class="stat-growth" :class="stats.orders_growth >= 0 ? 'up' : 'down'">
                {{ stats.orders_growth >= 0 ? '+' : '' }}{{ stats.orders_growth || 0 }}% 较昨日
              </p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon products">
              <el-icon><Goods /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">在售商品</p>
              <p class="stat-value">{{ stats.online_products || 0 }}</p>
              <p class="stat-growth">
                共 {{ stats.total_products || 0 }} 件商品
              </p>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon users">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <p class="stat-label">累计用户</p>
              <p class="stat-value">{{ stats.total_users || 0 }}</p>
              <p class="stat-growth up">
                +{{ stats.new_users || 0 }} 今日新增
              </p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 图表和排行区域 -->
    <el-row :gutter="20" class="charts-row">
      <!-- 销售趋势 -->
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>销售趋势</span>
              <el-radio-group v-model="trendDays" size="small">
                <el-radio-button :label="7">近7天</el-radio-button>
                <el-radio-button :label="14">近14天</el-radio-button>
                <el-radio-button :label="30">近30天</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          
          <div class="chart-placeholder">
            <el-empty description="图表组件开发中..." />
          </div>
        </el-card>
      </el-col>
      
      <!-- 热销商品排行 -->
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>热销商品 TOP5</span>
          </template>
          
          <div class="ranking-list">
            <div v-for="(item, index) in topProducts" :key="item.id" class="ranking-item">
              <span class="rank" :class="'rank-' + (index + 1)">{{ index + 1 }}</span>
              <span class="product-name">{{ item.name }}</span>
              <span class="sales-count">{{ item.sales_count }} 件</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 待处理订单 -->
    <el-row :gutter="20" class="orders-row">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>待处理订单</span>
              <el-button type="primary" size="small" link @click="goToOrders">
                查看全部
              </el-button>
            </div>
          </template>
          
          <el-table :data="pendingOrders" stripe style="width: 100%">
            <el-table-column prop="order_no" label="订单号" width="180" />
            <el-table-column prop="user_name" label="买家" width="120" />
            <el-table-column prop="total_amount" label="金额" width="100">
              <template #default="{ row }">
                ¥{{ row.total_amount?.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ getStatusName(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="下单时间" width="180" />
            <el-table-column label="操作" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" size="small" link @click="goToDetail(row.order_no)">
                  处理
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Money, Document, Goods, User } from '@element-plus/icons-vue'
import { dashboardApi } from '@/api'

const router = useRouter()

const loading = ref(false)
const trendDays = ref(7)

// 统计数据
const stats = ref<any>({
  today_sales: 12580.50,
  sales_growth: 12.5,
  today_orders: 86,
  orders_growth: 8.3,
  online_products: 45,
  total_products: 52,
  total_users: 1258,
  new_users: 23,
})

// 热销商品
const topProducts = ref<any[]>([
  { id: 1, name: '红富士苹果(礼盒装)', sales_count: 156 },
  { id: 2, name: '野生土蜂蜜 500g', sales_count: 128 },
  { id: 3, name: '红富士苹果 5斤装', sales_count: 98 },
  { id: 4, name: '野生土蜂蜜 1000g', sales_count: 76 },
  { id: 5, name: '苹果+蜂蜜 组合装', sales_count: 54 },
])

// 待处理订单
const pendingOrders = ref<any[]>([
  { order_no: 'ORD202606120001', user_name: '张**', total_amount: 89.90, status: 1, created_at: '2026-06-12 10:30:00' },
  { order_no: 'ORD202606120002', user_name: '李**', total_amount: 168.00, status: 1, created_at: '2026-06-12 11:15:00' },
  { order_no: 'ORD202606120003', user_name: '王**', total_amount: 59.90, status: 6, created_at: '2026-06-12 09:45:00' },
])

const getStatusType = (status: number) => {
  const types: Record<number, string> = {
    1: 'warning', // 待发货
    6: 'danger',  // 退款中
  }
  return types[status] || 'info'
}

const getStatusName = (status: number) => {
  const names: Record<number, string> = {
    0: '待付款',
    1: '待发货',
    2: '待收货',
    3: '已完成',
    4: '已取消',
    5: '已退款',
    6: '退款中',
  }
  return names[status] || '未知'
}

const goToOrders = () => {
  router.push('/orders')
}

const goToDetail = (orderNo: string) => {
  router.push(`/orders/detail/${orderNo}`)
}

const loadStats = async () => {
  loading.value = true
  try {
    // 尝试调用后端API
    await dashboardApi.getStats()
  } catch {
    // 使用Mock数据
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stats-row {
  margin-bottom: 0;
}

.stat-card {
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #fff;
}

.stat-icon.sales {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.orders {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.products {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.users {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.stat-growth {
  font-size: 12px;
}

.stat-growth.up {
  color: #67c23a;
}

.stat-growth.down {
  color: #f56c6c;
}

.charts-row {
  margin-bottom: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-placeholder {
  padding: 40px 0;
}

.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.rank {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
}

.rank-1 {
  background: #f56c6c;
}

.rank-2 {
  background: #e6a23c;
}

.rank-3 {
  background: #67c23a;
}

.rank-4, .rank-5 {
  background: #909399;
}

.product-name {
  flex: 1;
  font-size: 14px;
  color: #606266;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sales-count {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.orders-row {
  margin-bottom: 0;
}
</style>
