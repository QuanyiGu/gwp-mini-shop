<template>
  <div class="banners">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>Banner管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            添加Banner
          </el-button>
        </div>
      </template>
      
      <!-- Banner列表 -->
      <el-table :data="tableData" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="image" label="图片" width="200">
          <template #default="{ row }">
            <el-image
              :src="row.image || '/placeholder-banner.png'"
              fit="cover"
              style="width: 180px; height: 80px; border-radius: 4px;"
            />
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="150" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 'growth' ? 'success' : 'warning'">
              {{ row.type === 'growth' ? '生长状态' : '活动' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sort" label="排序" width="80" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'">
              {{ row.status === 1 ? '显示' : '隐藏' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="180" fixed="right">
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
              {{ row.status === 1 ? '隐藏' : '显示' }}
            </el-button>
            <el-button type="danger" size="small" link @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 编辑/添加弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑Banner' : '添加Banner'" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="Banner标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入Banner标题" />
        </el-form-item>
        
        <el-form-item label="Banner图片">
          <div class="banner-uploader">
            <el-upload
              class="banner-upload"
              list-type="picture-card"
              :show-file-list="false"
              :on-success="handleImageSuccess"
              :before-upload="beforeImageUpload"
            >
              <img v-if="form.image" :src="form.image" class="banner-preview" />
              <el-icon v-else class="upload-icon"><Plus /></el-icon>
            </el-upload>
            <p class="upload-tip">建议尺寸 1080x480px，支持 jpg、png 格式</p>
          </div>
        </el-form-item>
        
        <el-form-item label="跳转链接">
          <el-input v-model="form.link" placeholder="请输入跳转链接（可选）" />
        </el-form-item>
        
        <el-form-item label="Banner类型">
          <el-radio-group v-model="form.type">
            <el-radio value="growth">生长状态</el-radio>
            <el-radio value="activity">活动推广</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="排序">
          <el-input-number v-model="form.sort" :min="0" :max="999" />
          <span style="margin-left: 8px; color: #909399;">数字越小越靠前</span>
        </el-form-item>
        
        <el-form-item label="状态">
          <el-switch
            v-model="form.status"
            :active-value="1"
            :inactive-value="0"
            active-text="显示"
            inactive-text="隐藏"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { bannerApi } from '@/api'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref<number | null>(null)

const form = reactive<any>({
  title: '',
  image: '',
  link: '',
  type: 'growth',
  sort: 0,
  status: 1,
})

const tableData = ref<any[]>([
  { id: 1, title: '苹果开花期', image: '', type: 'growth', sort: 1, status: 1, created_at: '2026-05-01 10:00:00' },
  { id: 2, title: '苹果结果期', image: '', type: 'growth', sort: 2, status: 1, created_at: '2026-05-10 10:00:00' },
  { id: 3, title: '蜂蜜新蜜上市', image: '', type: 'activity', sort: 3, status: 1, created_at: '2026-06-01 10:00:00' },
  { id: 4, title: '618特惠活动', image: '', type: 'activity', sort: 0, status: 0, created_at: '2026-06-10 10:00:00' },
])

const handleAdd = () => {
  isEdit.value = false
  editId.value = null
  Object.assign(form, {
    title: '',
    image: '',
    link: '',
    type: 'growth',
    sort: 0,
    status: 1,
  })
  dialogVisible.value = true
}

const handleEdit = (row: any) => {
  isEdit.value = true
  editId.value = row.id
  Object.assign(form, {
    title: row.title,
    image: row.image,
    link: row.link || '',
    type: row.type,
    sort: row.sort,
    status: row.status,
  })
  dialogVisible.value = true
}

const handleToggleStatus = (row: any) => {
  const newStatus = row.status === 1 ? 0 : 1
  const action = newStatus === 1 ? '显示' : '隐藏'
  
  ElMessageBox.confirm(`确定要${action}该Banner吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(() => {
    row.status = newStatus
    ElMessage.success(`${action}成功`)
  }).catch(() => {})
}

const handleDelete = (row: any) => {
  ElMessageBox.confirm('确定要删除该Banner吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    try {
      try {
        await bannerApi.delete(row.id)
      } catch {
        // Mock 成功
      }
      const index = tableData.value.findIndex(item => item.id === row.id)
      if (index > -1) {
        tableData.value.splice(index, 1)
      }
      ElMessage.success('删除成功')
    } catch {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const handleImageSuccess = (response: any) => {
  form.image = response.url || URL.createObjectURL(response.raw)
}

const beforeImageUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5
  
  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB!')
    return false
  }
  return true
}

const handleSubmit = async () => {
  if (!form.title) {
    ElMessage.warning('请输入Banner标题')
    return
  }
  if (!form.image) {
    ElMessage.warning('请上传Banner图片')
    return
  }
  
  submitLoading.value = true
  try {
    if (isEdit.value && editId.value) {
      try {
        await bannerApi.update(editId.value, form)
      } catch {
        // Mock 成功
      }
      const index = tableData.value.findIndex(item => item.id === editId.value)
      if (index > -1) {
        Object.assign(tableData.value[index], form)
      }
      ElMessage.success('更新成功')
    } else {
      try {
        await bannerApi.create(form)
      } catch {
        // Mock 成功
      }
      tableData.value.unshift({
        id: Date.now(),
        ...form,
        created_at: new Date().toLocaleString(),
      })
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    submitLoading.value = false
  }
}
</script>

<style scoped>
.banners {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.banner-uploader {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.banner-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s;
}

.banner-upload:hover {
  border-color: #409eff;
}

.upload-icon {
  font-size: 28px;
  color: #8c939d;
  width: 270px;
  height: 120px;
  text-align: center;
  line-height: 120px;
}

.banner-preview {
  width: 270px;
  height: 120px;
  display: block;
  object-fit: cover;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin: 0;
}
</style>
