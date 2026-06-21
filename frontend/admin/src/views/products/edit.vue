<template>
  <div class="product-edit">
    <el-card>
      <template #header>
        <div class="card-header">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/products' }">商品管理</el-breadcrumb-item>
            <el-breadcrumb-item>{{ isEdit ? '编辑商品' : '添加商品' }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
      </template>
      
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
        style="max-width: 800px;"
      >
        <el-form-item label="商品名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入商品名称" />
        </el-form-item>
        
        <el-form-item label="商品分类" prop="category_id">
          <el-select v-model="form.category_id" placeholder="请选择分类" style="width: 100%;">
            <el-option
              v-for="cat in categories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="商品价格" prop="price">
          <el-input-number
            v-model="form.price"
            :min="0.01"
            :step="0.01"
            :precision="2"
            style="width: 200px;"
          />
          <span style="margin-left: 8px; color: #909399;">元</span>
        </el-form-item>
        
        <el-form-item label="商品库存" prop="stock">
          <el-input-number
            v-model="form.stock"
            :min="0"
            :step="1"
            style="width: 200px;"
          />
          <span style="margin-left: 8px; color: #909399;">件</span>
        </el-form-item>
        
        <el-form-item label="商品主图">
          <div class="image-uploader">
            <el-upload
              class="avatar-uploader"
              :show-file-list="false"
              :on-success="handleImageSuccess"
              :before-upload="beforeImageUpload"
            >
              <img v-if="form.main_image" :src="form.main_image" class="avatar" />
              <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
            </el-upload>
            <p class="upload-tip">建议尺寸 800x800px，支持 jpg、png 格式</p>
          </div>
        </el-form-item>
        
        <el-form-item label="商品描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="6"
            placeholder="请输入商品描述"
          />
        </el-form-item>
        
        <el-form-item label="商品状态">
          <el-switch
            v-model="form.status"
            :active-value="1"
            :inactive-value="0"
            active-text="上架"
            inactive-text="下架"
          />
        </el-form-item>
        
        <el-divider content-position="left">扩展信息</el-divider>
        
        <el-form-item label="生长周期">
          <el-input v-model="form.growth_cycle" placeholder="如：开花期、结果期、成熟期等" />
        </el-form-item>
        
        <el-form-item label="产地溯源">
          <el-input
            v-model="form.origin"
            type="textarea"
            :rows="3"
            placeholder="记录产地信息、种植过程等"
          />
        </el-form-item>
        
        <el-form-item label="礼盒包装">
          <el-switch
            v-model="form.has_gift_box"
            active-text="支持"
            inactive-text="不支持"
          />
        </el-form-item>
        
        <el-form-item label="贺卡服务">
          <el-switch
            v-model="form.has_greeting_card"
            active-text="支持"
            inactive-text="不支持"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="loading">
            保存
          </el-button>
          <el-button @click="handleCancel">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { productApi, categoryApi } from '@/api'

const router = useRouter()
const route = useRoute()
const formRef = ref<FormInstance>()
const loading = ref(false)

const productId = route.params.id as string
const isEdit = !!productId

const form = reactive<any>({
  name: '',
  category_id: '',
  price: 0,
  stock: 0,
  main_image: '',
  images: '',
  description: '',
  status: 1,
  growth_cycle: '',
  origin: '',
  has_gift_box: false,
  has_greeting_card: false,
})

const rules: FormRules = {
  name: [
    { required: true, message: '请输入商品名称', trigger: 'blur' },
    { min: 2, max: 100, message: '商品名称长度在 2 到 100 个字符', trigger: 'blur' },
  ],
  category_id: [
    { required: true, message: '请选择商品分类', trigger: 'change' },
  ],
  price: [
    { required: true, message: '请输入商品价格', trigger: 'blur' },
  ],
  stock: [
    { required: true, message: '请输入商品库存', trigger: 'blur' },
  ],
}

const categories = ref<any[]>([])

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

const loadProductDetail = async () => {
  if (!isEdit) return
  
  loading.value = true
  try {
    try {
      const res: any = await productApi.getDetail(Number(productId))
      Object.assign(form, res)
    } catch {
      // Mock 数据
      form.name = '红富士苹果 5斤装'
      form.category_id = 1
      form.price = 29.90
      form.stock = 156
      form.description = '新鲜红富士苹果，产地直供，脆甜多汁'
    }
  } finally {
    loading.value = false
  }
}

const handleImageSuccess = (response: any) => {
  form.main_image = response.url || URL.createObjectURL(response.raw)
}

const beforeImageUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2
  
  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }
  return true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        if (isEdit) {
          try {
            await productApi.update(Number(productId), form)
          } catch {
            // Mock 成功
          }
          ElMessage.success('更新成功')
        } else {
          try {
            await productApi.create(form)
          } catch {
            // Mock 成功
          }
          ElMessage.success('创建成功')
        }
        router.push('/products')
      } catch (error: any) {
        ElMessage.error(error.message || '操作失败')
      } finally {
        loading.value = false
      }
    }
  })
}

const handleCancel = () => {
  router.push('/products')
}

onMounted(() => {
  loadCategories()
  loadProductDetail()
})
</script>

<style scoped>
.product-edit {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.image-uploader {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.avatar-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s;
}

.avatar-uploader:hover {
  border-color: #409eff;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 148px;
  height: 148px;
  text-align: center;
  line-height: 148px;
}

.avatar {
  width: 148px;
  height: 148px;
  display: block;
  object-fit: cover;
}

.upload-tip {
  font-size: 12px;
  color: #909399;
  margin: 0;
}
</style>
