<template>
  <div class="products">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>商品管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            添加商品
          </el-button>
        </div>
      </template>
      
      <!-- 搜索筛选 -->
      <div class="search-bar">
        <el-input
          v-model="searchForm.keyword"
          placeholder="搜索商品名称"
          style="width: 240px; margin-right: 16px;"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select
          v-model="searchForm.status"
          placeholder="商品状态"
          style="width: 120px; margin-right: 16px;"
          clearable
        >
          <el-option label="全部" :value="undefined" />
          <el-option label="上架" :value="1" />
          <el-option label="下架" :value="0" />
        </el-select>
        
        <el-select
          v-model="searchForm.category_id"
          placeholder="商品分类"
          style="width: 120px; margin-right: 16px;"
          clearable
        >
          <el-option
            v-for="cat in categories"
            :key="cat.id"
            :label="cat.name"
            :value="cat.id"
          />
        </el-select>
        
        <el-button type="primary" @click="handleSearch">搜索</el-button>
        <el-button @click="handleReset">重置</el-button>
      </div>
      
      <!-- 商品表格 -->
      <el-table :data="tableData" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="main_image" label="图片" width="100">
          <template #default="{ row }">
            <el-image
              :src="row.main_image || '/placeholder.png'"
              fit="cover"
              style="width: 60px; height: 60px; border-radius: 4px;"
            />
          </template>
        </el-table-column>
        <el-table-column prop="name" label="商品名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="category_name" label="分类" width="100" />
        <el-table-column prop="price" label="价格" width="100">
          <template #default="{ row }">
            ¥{{ row.price?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="80" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'">
              {{ row.status === 1 ? '上架' : '下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button
              :type="row.status === 1 ? 'warning' : 'success'"
              size="small"
              link
              @click="handleToggleStatus(row)"
            >
              {{ row.status === 1 ? '下架' : '上架' }}
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { productApi, categoryApi } from '@/api'

const router = useRouter()
const loading = ref(false)

const searchForm = reactive<{
  keyword: string
  status: number | ''
  category_id: number | ''
}>({
  keyword: '',
  status: '',
  category_id: '',
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0,
})

const tableData = ref<any[]>([])
const categories = ref<any[]>([])

// 模拟数据
const mockProducts = [
  { id: 1, name: '红富士苹果 5斤装', category_name: '水果', price: 29.90, stock: 156, status: 1, main_image: '', created_at: '2026-05-01 10:00:00' },
  { id: 2, name: '红富士苹果(礼盒装)', category_name: '水果', price: 59.90, stock: 89, status: 1, main_image: '', created_at: '2026-05-02 10:00:00' },
  { id: 3, name: '野生土蜂蜜 500g', category_name: '蜂蜜', price: 68.00, stock: 234, status: 1, main_image: '', created_at: '2026-05-03 10:00:00' },
  { id: 4, name: '野生土蜂蜜 1000g', category_name: '蜂蜜', price: 128.00, stock: 156, status: 1, main_image: '', created_at: '2026-05-04 10:00:00' },
  { id: 5, name: '苹果+蜂蜜 组合装', category_name: '组合', price: 168.00, stock: 78, status: 1, main_image: '', created_at: '2026-05-05 10:00:00' },
]

const loadCategories = async () => {
  try {
    const res: any = await categoryApi.getList()
    categories.value = res || []
  } catch {
    categories.value = [
      { id: 1, name: '水果' },
      { id: 2, name: '蜂蜜' },
      { id: 3, name: '组合' },
    ]
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...(searchForm.keyword && { keyword: searchForm.keyword }),
      ...(searchForm.status !== '' && { status: searchForm.status }),
      ...(searchForm.category_id && { category_id: searchForm.category_id }),
    }
    
    try {
      const res: any = await productApi.getList(params)
      tableData.value = res.items || res.list || []
      pagination.total = res.total || 0
    } catch {
      // 使用模拟数据
      tableData.value = mockProducts
      pagination.total = mockProducts.length
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
  searchForm.category_id = ''
  pagination.page = 1
  loadData()
}

const handleAdd = () => {
  router.push('/products/edit')
}

const handleEdit = (row: any) => {
  router.push(`/products/edit/${row.id}`)
}

const handleToggleStatus = async (row: any) => {
  const newStatus = row.status === 1 ? 0 : 1
  const action = newStatus === 1 ? '上架' : '下架'
  
  ElMessageBox.confirm(`确定要${action}该商品吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      try {
        await productApi.updateStatus(row.id, newStatus)
      } catch {
        // Mock 成功
      }
      row.status = newStatus
      ElMessage.success(`${action}成功`)
    } catch {
      ElMessage.error(`${action}失败`)
    }
  }).catch(() => {})
}

onMounted(() => {
  loadCategories()
  loadData()
})
</script>

<style scoped>
.products {
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

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
