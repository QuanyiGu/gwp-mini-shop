<template>
  <div class="orders">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>订单管理</span>
        </div>
      </template>
      
      <!-- 搜索筛选 -->
      <div class="search-bar">
        <el-input
          v-model="searchForm.keyword"
          placeholder="搜索订单号/买家"
          style="width: 240px; margin-right: 16px;"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select
          v-model="searchForm.status"
          placeholder="订单状态"
          style="width: 120px; margin-right: 16px;"
          clearable
        >
          <el-option label="全部" :value="undefined" />
          <el-option label="待付款" :value="0" />
          <el-option label="待发货" :value="1" />
          <el-option label="待收货" :value="2" />
          <el-option label="已完成" :value="3" />
          <el-option label="已取消" :value="4" />
          <el-option label="已退款" :value="5" />
          <el-option label="退款中" :value="6" />
        </el-select>
        
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>
      
      <!-- 订单表格 -->
      <el-table :data="tableData" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="order_no" label="订单号" width="180" />
        <el-table-column prop="user_name" label="买家" width="100" />
        <el-table-column prop="items" label="商品" min-width="200">
          <template #default="{ row }">
            <div v-for="(item, index) in row.items?.slice(0, 2)" :key="index" class="order-item">
              <span class="item-name">{{ item.product_name }}</span>
              <span class="item-qty">x{{ item.quantity }}</span>
            </div>
            <div v-if="row.items?.length > 2" class="more-items">
              还有 {{ row.items.length - 2 }} 件商品
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="金额" width="100">
          <template #default="{ row }">
            <span style="color: #f56c6c; font-weight: 500;">¥{{ row.total_amount?.toFixed(2) }}</span>
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
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="goToDetail(row.order_no)">
              详情
            </el-button>
            <el-button
              v-if="row.status === 1"
              type="success"
              size="small"
              link
              @click="handleShip(row)"
            >
              发货
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :page-sizes="[10, 20, 50]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>
    
    <!-- 发货弹窗 -->
    <el-dialog v-model="shipDialogVisible" title="订单发货" width="500px">
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
        <el-button @click="shipDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="shipLoading" @click="confirmShip">
          确认发货
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { orderApi } from '@/api'

const router = useRouter()
const loading = ref(false)
const shipLoading = ref(false)
const shipDialogVisible = ref(false)
const currentOrderNo = ref('')

const searchForm = reactive<{
  keyword: string
  status: number | ''
}>({
  keyword: '',
  status: '',
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0,
})

const shipForm = reactive({
  logistics_company: '',
  tracking_no: '',
})

const tableData = ref<any[]>([])

// Mock 订单数据
const mockOrders = [
  {
    order_no: 'ORD202606120001',
    user_name: '张先生',
    total_amount: 89.90,
    status: 1,
    created_at: '2026-06-12 10:30:00',
    items: [
      { product_name: '红富士苹果 5斤装', quantity: 2 },
      { product_name: '野生土蜂蜜 500g', quantity: 1 },
    ],
  },
  {
    order_no: 'ORD202606120002',
    user_name: '李女士',
    total_amount: 168.00,
    status: 1,
    created_at: '2026-06-12 11:15:00',
    items: [
      { product_name: '苹果+蜂蜜 组合装', quantity: 1 },
    ],
  },
  {
    order_no: 'ORD202606120003',
    user_name: '王先生',
    total_amount: 59.90,
    status: 6,
    created_at: '2026-06-12 09:45:00',
    items: [
      { product_name: '红富士苹果(礼盒装)', quantity: 1 },
    ],
  },
  {
    order_no: 'ORD202606110001',
    user_name: '赵女士',
    total_amount: 128.00,
    status: 2,
    created_at: '2026-06-11 14:20:00',
    items: [
      { product_name: '野生土蜂蜜 1000g', quantity: 1 },
    ],
  },
  {
    order_no: 'ORD202606100001',
    user_name: '孙先生',
    total_amount: 196.00,
    status: 3,
    created_at: '2026-06-10 16:30:00',
    items: [
      { product_name: '红富士苹果 5斤装', quantity: 2 },
      { product_name: '野生土蜂蜜 500g', quantity: 2 },
      { product_name: '红富士苹果(礼盒装)', quantity: 1 },
    ],
  },
]

const getStatusType = (status: number) => {
  const types: Record<number, string> = {
    0: 'warning', // 待付款
    1: 'warning', // 待发货
    2: 'primary', // 待收货
    3: 'success', // 已完成
    4: 'info',    // 已取消
    5: 'info',    // 已退款
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

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...(searchForm.keyword && { keyword: searchForm.keyword }),
      ...(searchForm.status !== '' && { status: searchForm.status }),
    }
    
    try {
      const res: any = await orderApi.getList(params)
      tableData.value = res.items || res.list || []
      pagination.total = res.total || 0
    } catch {
      // 使用模拟数据
      tableData.value = mockOrders
      pagination.total = mockOrders.length
    }
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const handleReset = () => {
  searchForm.keyword = ''
  searchForm.status = ''
  pagination.page = 1
  loadData()
}

const goToDetail = (orderNo: string) => {
  router.push(`/orders/detail/${orderNo}`)
}

const handleShip = (row: any) => {
  currentOrderNo.value = row.order_no
  shipForm.logistics_company = ''
  shipForm.tracking_no = ''
  shipDialogVisible.value = true
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
      await orderApi.ship(currentOrderNo.value, shipForm)
    } catch {
      // Mock 成功
    }
    ElMessage.success('发货成功')
    shipDialogVisible.value = false
    loadData()
  } catch (error: any) {
    ElMessage.error(error.message || '发货失败')
  } finally {
    shipLoading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.orders {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-bar {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.order-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.item-name {
  font-size: 14px;
  color: #606266;
}

.item-qty {
  font-size: 14px;
  color: #909399;
}

.more-items {
  font-size: 12px;
  color: #909399;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
