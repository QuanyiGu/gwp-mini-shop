# GWP的小店 - 产品设计文档

> 版本：v1.0
> 更新日期：2026-03-27

---

## 一、产品概述

### 1.1 产品定位
- **产品名称**：GWP的小店
- **产品Slogan**：自然好味，从田间到舌尖
- **目标用户**：
  - 注重健康饮食的城市家庭
  - 追求天然无添加食品的消费者
  - 有特产送礼需求的用户
- **核心价值**：提供自家产的优质苹果和蜂蜜，直连农户与消费者

### 1.2 技术栈

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| **用户端小程序** | Vue 3 + uni-app | 跨端框架，可发布到微信小程序、H5等 |
| **状态管理** | Pinia | uni-app 官方推荐状态管理库 |
| **UI组件库** | uView Plus | uni-app生态最完善的UI组件库 |
| **HTTP请求** | uView Plus 请求封装 | 统一拦截器、自动续签token |
| **商家后台H5** | Vue 3 + Vite + Element Plus | 独立部署的H5管理后台 |
| **后端语言** | Python 3.9+ | |
| **Web框架** | FastAPI | 高性能异步框架，自动生成API文档 |
| **数据库** | MySQL 8.0+ | 关系型数据库 |
| **ORM** | SQLAlchemy 2.0 | Python ORM框架 |
| **缓存** | Redis | 会话、数据缓存 |
| **任务队列** | FastAPI BackgroundTasks | 轻量级异步任务处理 |

---

## 二、功能模块设计

### 2.1 用户端功能

| 模块 | 功能点 | 说明 |
|------|--------|------|
| **首页** | 轮播Banner、快捷分类、热销推荐、**店主故事（第二屏）** | 首屏聚焦购买决策 |
| **商品** | 分类浏览、**规格选择**、商品详情、**礼盒+贺卡选项（E4）**、商品评价 | 详情页包含规格和礼盒选项 |
| **购物车** | 商品增删、数量调整、价格计算、去结算、**完整状态处理** | 含空状态引导、骨架屏、失败提示、失效处理 |
| **订单** | 订单确认、微信支付、订单列表、**订单详情内嵌追踪（E6）**、物流跟踪 | 追踪节点在详情页底部内嵌 |
| **收货地址** | 地址增删改查、默认地址设置 | |
| **个人中心** | 用户信息、我的订单、**我的优惠券（E5）**、我的收藏、联系客服 | 优惠券入口在个人中心 |
| **优惠券** | 领取优惠券、**结算页最优券提示**、分享邀请（E5） | 双入口：主动领取 + 结算页提示 |

### 2.2 商家后台功能（独立H5管理后台）

| 模块 | 功能点 | 说明 |
|------|--------|------|
| **数据概览** | 今日销售额、订单量、热销商品排行 | |
| **商品管理** | 商品列表、添加商品、编辑商品（含E2/E3扩展信息）、上下架、库存管理 | |
| **订单管理** | 订单列表、订单详情、订单发货、退款处理 | |
| **Banner管理** | 生长状态Banner配置（E1）、节日主题Banner | |
| **销售统计** | 销售额趋势、商品销量排行 | |

---

## 三、页面结构设计

### 3.1 用户端页面列表

| 序号 | 页面名称 | 路径 | 说明 |
|------|----------|------|------|
| 1 | 首页 | `/pages/index/index` | 店铺首页（Banner、分类、推荐、首屏聚焦购买） |
| 2 | 商品分类 | `/pages/category/category` | 分类浏览 |
| 3 | 商品详情 | `/pages/product/detail` | 商品信息（含规格选择、礼盒贺卡选项 E4） |
| 4 | 购物车 | `/pages/cart/index` | 购物车管理（含完整状态处理） |
| 5 | 订单确认 | `/pages/order/checkout` | 确认订单 |
| 6 | 支付结果 | `/pages/order/pay-result` | 支付成功页 |
| 7 | 订单列表 | `/pages/order/list` | 我的订单 |
| 8 | 订单详情 | `/pages/order/detail` | 订单信息（内嵌追踪节点 E6） |
| 9 | 个人中心 | `/pages/user/index` | 用户中心（含优惠券入口） |
| 10 | 收货地址 | `/pages/user/address` | 地址列表 |
| 11 | 编辑地址 | `/pages/user/address-edit` | 添加/编辑地址 |
| 12 | 我的收藏 | `/pages/user/favorites` | 收藏商品 |
| 13 | 我的优惠券 | `/pages/user/coupons` | 我的优惠券（E5） |

### 3.2 商家后台页面列表（H5 独立部署）

商家后台为独立 H5 项目，部署域名如 `https://admin.gwp-shop.com/`：

| 序号 | 页面名称 | 路径 | 说明 |
|------|----------|------|------|
| 1 | 登录页 | `/pages/login/index` | 商家登录 |
| 2 | 数据概览 | `/pages/dashboard/index` | 销售数据统计 |
| 3 | 商品管理 | `/pages/products/list` | 商品列表 |
| 4 | 商品编辑 | `/pages/products/edit` | 添加/编辑商品（含扩展信息 E2/E3） |
| 5 | 订单管理 | `/pages/orders/list` | 订单列表 |
| 6 | 订单详情 | `/pages/orders/detail` | 订单处理、发货 |
| 7 | Banner配置 | `/pages/banners/list` | 生长状态Banner管理（E1） |

---

## 四、数据库设计

### 4.1 核心数据表

#### 用户表 (users)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| uid | VARCHAR(64) | 用户唯一标识（雪花算法生成，不可枚举） |
| openid | VARCHAR(100) | 微信openid（用于微信登录） |
| unionid | VARCHAR(100) | 微信unionid（用户授权后存储，跨小程序唯一标识） |
| nickname | VARCHAR(50) | 昵称 |
| avatar_url | VARCHAR(255) | 头像 |
| phone | VARCHAR(20) | 手机号 |
| created_at | DATETIME | 创建时间 |

#### 商品表 (products)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| category_id | BIGINT | 分类ID |
| name | VARCHAR(100) | 商品名称 |
| main_image | VARCHAR(255) | 主图 |
| images | JSON | 轮播图 |
| description | TEXT | 商品详情 |
| price | DECIMAL(10,2) | 价格 |
| original_price | DECIMAL(10,2) | 原价 |
| stock | INT | 库存 |
| sales | INT | 销量 |
| status | TINYINT | 状态 1上架 0下架 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |
| 注意：采蜜日期(蜂蜜)、品种信息(苹果)存储在 product_extras 表 |

#### 订单表 (orders)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| order_no | VARCHAR(32) | 订单号（雪花算法生成，不可枚举） |
| user_id | BIGINT | 用户ID |
| total_amount | DECIMAL(10,2) | 订单总额 |
| pay_amount | DECIMAL(10,2) | 实付金额 |
| address_name | VARCHAR(50) | 收货人 |
| address_phone | VARCHAR(20) | 收货电话 |
| address_detail | VARCHAR(500) | 详细收货地址 |
| status | TINYINT | 0待付款 1待发货 2待收货 3已完成 4已取消 |
| gift_package | TINYINT | 是否有礼盒包装 0否 1是 |
| greeting_card | VARCHAR(50) | 贺卡祝福语内容 |
| tracking_node | VARCHAR(20) | 订单追踪节点（E6）: 0已采摘 1已打包 2已发货 3已送达 |
| logistics_company | VARCHAR(50) | 物流公司 |
| logistics_no | VARCHAR(50) | 物流单号 |
| created_at | DATETIME | 创建时间 |

#### 订单商品表 (order_items)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| order_id | BIGINT | 订单ID |
| product_id | BIGINT | 商品ID |
| product_name | VARCHAR(100) | 商品名称 |
| product_image | VARCHAR(255) | 商品图片 |
| price | DECIMAL(10,2) | 单价 |
| quantity | INT | 数量 |
| total_price | DECIMAL(10,2) | 小计 |

#### 收货地址表 (addresses)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| user_id | BIGINT | 用户ID |
| name | VARCHAR(50) | 收货人 |
| phone | VARCHAR(20) | 手机号 |
| province | VARCHAR(50) | 省份 |
| city | VARCHAR(50) | 城市 |
| district | VARCHAR(50) | 区县 |
| detail | VARCHAR(255) | 详细地址 |
| is_default | TINYINT | 是否默认 |

#### 商品分类表 (categories)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| name | VARCHAR(50) | 分类名称 |
| icon | VARCHAR(255) | 图标 |
| sort | INT | 排序 |

#### 购物车表 (cart_items)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| user_id | BIGINT | 用户ID |
| product_id | BIGINT | 商品ID |
| quantity | INT | 数量（重复添加时叠加） |
| selected | TINYINT | 是否选中 |

#### 商家后台用户表 (admin_users)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| username | VARCHAR(50) | 登录用户名（唯一） |
| password_hash | VARCHAR(255) | 密码哈希（bcrypt） |
| nickname | VARCHAR(50) | 商家昵称 |
| role | VARCHAR(20) | 角色：admin/super_admin |
| created_at | DATETIME | 创建时间 |

#### 优惠券表 (coupons)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| code | VARCHAR(64) | 优惠券码（UUID，不可枚举） |
| user_id | BIGINT | 所属用户ID |
| type | TINYINT | 类型：1满减券 |
| discount | DECIMAL(10,2) | 优惠金额 |
| min_amount | DECIMAL(10,2) | 最低消费门槛（满¥39可用） |
| status | TINYINT | 状态：0未使用 1已使用 2已过期 |
| expires_at | DATETIME | 过期时间 |
| created_at | DATETIME | 创建时间 |

#### 邀请记录表 (invites)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| inviter_id | BIGINT | 邀请人用户ID |
| invitee_id | BIGINT | 被邀请人用户ID |
| invite_code | VARCHAR(64) | 邀请码（UUID） |
| order_id | BIGINT | 产生奖励的订单ID |
| coupon_sent | TINYINT | 是否已发放优惠券 0否 1是 |
| created_at | DATETIME | 创建时间 |

#### Banner配置表 (banner_configs)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| type | VARCHAR(20) | 类型：growth_status（生长状态） |
| title | VARCHAR(100) | 标题 |
| content | TEXT | 内容（支持图片URL） |
| status | TINYINT | 状态：0关闭 1开启 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

#### 商品扩展表 (product_extras)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | BIGINT | 主键 |
| product_id | BIGINT | 商品ID |
| harvest_date | DATE | 采蜜日期（蜂蜜专用，E2） |
| variety_info | TEXT | 品种信息（苹果专用，E3品种对比图） |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### 4.2 索引设计

为保证查询性能，在 MySQL 阶段添加以下索引：

| 表名 | 索引名 | 字段 | 类型 | 说明 |
|------|--------|------|------|------|
| users | idx_uid | uid | UNIQUE | 用户唯一标识查询 |
| users | idx_openid | openid | UNIQUE | 微信登录查询 |
| orders | idx_user_status | (user_id, status) | INDEX | 用户订单列表查询 |
| orders | idx_order_no | order_no | UNIQUE | 订单号查询（支付回调） |
| orders | idx_created | created_at | INDEX | 后台时间范围查询 |
| order_items | idx_order_id | order_id | INDEX | 订单商品关联查询 |
| order_items | idx_product_id | product_id | INDEX | 商品销量统计 |
| addresses | idx_user_id | user_id | INDEX | 用户地址列表 |
| cart_items | idx_user_id | user_id | INDEX | 用户购物车查询 |
| cart_items | idx_user_product | (user_id, product_id) | UNIQUE | 防止重复添加购物车 |
| coupons | idx_code | code | UNIQUE | 优惠码查询 |
| coupons | idx_user_status | (user_id, status) | INDEX | 用户优惠券列表 |
| invites | idx_inviter | inviter_id | INDEX | 邀请人记录查询 |
| invites | idx_invitee | invitee_id | INDEX | 被邀请人记录查询 |
| admin_users | idx_username | username | UNIQUE | 登录用户名唯一约束 |
| products | idx_category | category_id | INDEX | 分类商品列表 |
| product_extras | idx_product_id | product_id | UNIQUE | 商品扩展信息一对一 |

### 4.3 外键约束（MySQL 阶段）

微信云开发阶段不加强制外键约束，数据一致性由应用层保证。迁移到 MySQL 后添加以下外键：

| 外键名 | 从表 | 字段 | 主表 | 字段 | 说明 |
|--------|------|------|------|------|------|
| fk_order_user | orders | user_id | users | id | 订单所属用户 |
| fk_order_item_order | order_items | order_id | orders | id | 订单项所属订单 |
| fk_order_item_product | order_items | product_id | products | id | 订单项商品 |
| fk_address_user | addresses | user_id | users | id | 地址所属用户 |
| fk_cart_user | cart_items | user_id | users | id | 购物车所属用户 |
| fk_cart_product | cart_items | product_id | products | id | 购物车商品 |
| fk_coupon_user | coupons | user_id | users | id | 优惠券所属用户 |
| fk_invite_inviter | invites | inviter_id | users | id | 邀请人 |
| fk_invite_invitee | invites | invitee_id | users | id | 被邀请人 |
| fk_invite_order | invites | order_id | orders | id | 产生奖励的订单 |
| fk_extra_product | product_extras | product_id | products | id | 扩展所属商品 |

### 4.4 雪花算法 ID 实现

#### ID 结构（64-bit）
```
+--------------------------------------------------------------------------+
| 1bit reserved | 41bit timestamp | 10bit machine_id | 12bit sequence     |
+--------------------------------------------------------------------------+
```

- **timestamp**: 毫秒级时间戳，使用 Twitter 雪花算法 epoch (2020-01-01)
- **machine_id**: 机器标识，单机部署固定为 1；分布式部署需要从 etcd/Redis 协调分配
- **sequence**: 每毫秒内的序列号，支持每节点每毫秒 4096 个 ID

#### Python 实现

```python
# 使用 snowflake 库
# pip install snowflake

from snowflake import Snowflake

# 单机模式
snowflake = Snowflake(
    epoch=1577836800000,  # 2020-01-01 00:00:00 UTC
    machine_id=1          # 单机部署固定为 1
)

# 生成 ID
user_uid = snowflake.next_id()      # 用户 uid
order_no = snowflake.next_id()       # 订单号 order_no
```

#### 注意事项
- `snowflake` 库生成的 ID 是整数（INT），存储时转为字符串或直接存 BIGINT
- order_no 和 uid 都是数字类型，不需要 base62 转换
- 分布式部署时，machine_id 需要唯一分配，使用 Redis INCR 原子操作获取

---

## 五、项目目录结构

```
gwp-shop/
├── frontend/                 # 前端 uni-app 项目
│   ├── pages/                # 页面
│   │   ├── index/            # 首页
│   │   ├── category/         # 分类
│   │   ├── product/          # 商品
│   │   ├── cart/             # 购物车
│   │   ├── order/            # 订单
│   │   │   ├── list/         # 订单列表
│   │   │   ├── detail/       # 订单详情
│   │   │   ├── pay/          # 订单支付
│   │   │   └── tracking/     # 订单追踪（E6）
│   │   ├── user/             # 用户中心
│   │   └── coupon/           # 优惠券（E5）
│   ├── components/           # 组件
│   ├── api/                  # API接口
│   ├── utils/                # 工具函数
│   ├── static/               # 静态资源
│   ├── store/                # Pinia 状态管理
│   │   ├── user.js           # 用户状态
│   │   ├── cart.js          # 购物车状态
│   │   └── order.js         # 订单状态
│   ├── uni_modules/          # uni-app插件
│   └── package.json
│
├── admin/                    # 商家后台 H5 项目（独立部署）
│   ├── pages/
│   │   ├── login/           # 登录页
│   │   ├── dashboard/        # 数据统计
│   │   ├── products/        # 商品管理
│   │   ├── orders/          # 订单管理
│   │   └── banners/         # Banner配置（E1）
│   ├── components/
│   ├── api/
│   └── package.json
│
├── backend/                  # Python后端
│   ├── app/                  # 应用代码
│   │   ├── api/              # 路由
│   │   ├── models/           # 数据模型
│   │   ├── schemas/          # Pydantic模式
│   │   ├── services/         # 业务逻辑
│   │   ├── core/             # 核心配置
│   │   └── main.py           # 入口文件
│   ├── alembic/              # 数据库迁移
│   ├── tests/                # 测试
│   ├── .env                  # 环境变量
│   └── requirements.txt
│
├── database/                 # 数据库脚本
│   ├── schema.sql            # 建表脚本
│   └── seed.sql              # 初始数据
│
└── docs/                     # 文档
    └── api.md
```

---

## 六、API接口设计

### 6.0 通用规范

#### 统一响应格式
所有 API 响应统一使用以下 JSON 格式：

成功响应：
```json
{
  "code": 0,
  "message": "success",
  "data": { ... }
}
```

错误响应：
```json
{
  "code": 1001,
  "message": "库存不足",
  "data": null
}
```

#### 错误码定义

| 错误码 | 说明 | HTTP Status |
|--------|------|-------------|
| 0 | 成功 | 200 |
| 1001 | 参数错误 | 400 |
| 1002 | 签名验证失败 | 401 |
| 1003 | 无访问权限 | 403 |
| 1004 | 资源不存在 | 404 |
| 2001 | 库存不足 | 400 |
| 2002 | 订单不存在 | 404 |
| 2003 | 订单状态不允许此操作 | 400 |
| 2004 | 支付失败 | 400 |
| 3001 | 用户不存在 | 404 |
| 3002 | 登录凭证过期 | 401 |
| 4001 | 优惠券不存在 | 404 |
| 4002 | 优惠券已过期 | 400 |
| 4003 | 优惠券已使用 | 400 |
| 4004 | 不满足使用条件 | 400 |
| 5001 | 商家后台权限不足 | 403 |

#### 分页响应
列表类 API 支持分页，响应添加 `pagination` 字段：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "list": [...],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 100,
      "total_pages": 5
    }
  }
}
```

#### 认证方式
- 用户端 API：通过微信小程序 wx.login() 获取 code，后端通过 code 换取 openid/session
- 商家后台 API：通过用户名密码登录，获取 JWT token，后续请求携带 `Authorization: Bearer <token>`

### 6.1 商品接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/products` | 获取商品列表 |
| GET | `/api/products/:id` | 获取商品详情 |
| GET | `/api/categories` | 获取分类列表 |

### 6.2 购物车接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/cart` | 获取购物车 |
| POST | `/api/cart` | 添加商品 |
| PUT | `/api/cart/:id` | 更新数量 |
| DELETE | `/api/cart/:id` | 删除商品 |

### 6.3 订单接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/orders` | 创建订单 |
| GET | `/api/orders` | 订单列表 |
| GET | `/api/orders/:id` | 订单详情 |
| POST | `/api/orders/:id/pay` | 发起订单支付 |
| GET | `/api/orders/:id/tracking` | 查询追踪节点（E6） |

### 6.4 收货地址接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/addresses` | 收货地址列表 |
| POST | `/api/addresses` | 添加地址 |
| PUT | `/api/addresses/:id` | 更新地址 |
| DELETE | `/api/addresses/:id` | 删除地址 |
| PUT | `/api/addresses/:id/default` | 设为默认 |

### 6.5 商家后台接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/admin/login` | 商家登录 |
| GET | `/api/admin/stats` | 数据统计 |
| GET | `/api/admin/products` | 商品列表 |
| POST | `/api/admin/products` | 添加商品 |
| PUT | `/api/admin/products/:id` | 更新商品 |
| PUT | `/api/admin/products/:id/extras` | 更新商品扩展信息（采蜜日期/品种） |
| PUT | `/api/admin/products/:id/status` | 上下架 |
| GET | `/api/admin/orders` | 订单列表 |
| PUT | `/api/admin/orders/:id/ship` | 订单发货 |
| PUT | `/api/admin/orders/:id/tracking` | 更新追踪节点（E6） |
| GET | `/api/admin/banners` | Banner配置列表 |
| POST | `/api/admin/banners` | 创建Banner（E1生长状态） |
| PUT | `/api/admin/banners/:id` | 更新Banner |

### 6.6 优惠券与邀请接口（E5）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/coupons/claim` | 领取优惠券（通过邀请码） |
| GET | `/api/coupons` | 我的优惠券列表 |
| GET | `/api/coupons/apply` | 查询可用优惠券 |
| POST | `/api/invites/generate` | 生成邀请码 |
| GET | `/api/invites/history` | 邀请记录 |

### 6.7 营销内容接口（E1）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/banners/growth-status` | 获取生长状态Banner |

---

## 七、开发计划

### Phase 1: 基础框架搭建
- [ ] 项目目录结构
- [ ] 前端 uni-app 项目初始化
- [ ] 后端 FastAPI 项目初始化
- [ ] 数据库表创建

### Phase 2: 商品浏览模块
- [ ] 数据库商品表设计
- [ ] 商品列表、详情API
- [ ] 首页、分类页、商品详情页

### Phase 3: 购物车与订单
- [ ] 购物车功能
- [ ] 订单创建
- [ ] 订单列表、详情

### Phase 4: 商家后台
- [ ] 商品管理（上架、编辑）
- [ ] 订单管理（发货）
- [ ] 销量数据统计

---

## 八、可观测性与监控

### 8.1 日志方案

**技术选型：结构化日志 + ELK**

- 日志格式：JSON，包含 `timestamp`, `level`, `request_id`, `user_id`, `action`, `duration_ms`, `error` 等字段
- 日志收集：后端服务输出 JSON 日志，由 Filebeat/Logstash 收集至 Elasticsearch
- 日志查询：Kibana 可视化查询，支持按 request_id、user_id、action、时间段筛选
- 日志级别：DEBUG（开发）、INFO（正常）、WARNING（异常但可自愈）、ERROR（需关注）

### 8.2 监控告警

**技术选型：Prometheus + Grafana**

| 监控维度 | 指标 | 告警阈值建议 |
|----------|------|-------------|
| 服务可用性 | HTTP 5xx 率 | > 1% 持续 5 分钟 |
| 服务可用性 | 接口响应时间 P99 | > 2s |
| 系统资源 | CPU 使用率 | > 80% 持续 10 分钟 |
| 系统资源 | 内存使用率 | > 85% |
| 系统资源 | 磁盘使用率 | > 90% |
| 业务 | 订单支付失败率 | > 10% |
| 业务 | 微信支付回调超时 | > 5% |

### 8.3 小程序数据分析

使用微信官方小程序数据分析能力：

| 数据维度 | 说明 |
|----------|------|
| 访问分析 | 页面访问量、访问人数、访问时长 |
| 来源分析 | 分享次数、扫码次数 |
| 转化分析 | 下单转化率、支付转化率 |
| 用户画像 | 用户地域、性别、年龄段（需用户授权） |

### 8.4 商家后台监控

商家后台独立部署，监控指标：

- 登录失败次数（防暴力破解）
- API 请求 QPS
- 数据库连接池使用率

---

## 九、测试策略

### 9.1 测试金字塔

```
                    ┌─────────────┐
                    │   E2E 测试   │  ← 少量，关键用户路径
                    │  (Playwright) │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  集成测试   │  ← API 业务逻辑、数据库操作
                    │ (pytest)    │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  单元测试   │  ← 工具函数、数据校验
                    │ (pytest)   │
                    └─────────────┘
```

### 9.2 测试工具选型

| 测试类型 | 工具 | 说明 |
|----------|------|------|
| 单元测试 | pytest | Python 标准测试框架 |
| 异步测试 | pytest-asyncio | FastAPI 异步路由测试 |
| 并发压测 | pytest-xdist | 库存并发测试 |
| E2E 测试 | Playwright | 支持微信小程序模拟器 |
| API 测试 | FastAPI TestClient | 同步 API 测试 |

### 9.3 核心测试场景

| 测试场景 | 类型 | 说明 |
|----------|------|------|
| 库存原子扣减 | 并发压测 | pytest-xdist 多进程并发下单，验证超卖防护 |
| 微信支付回调 | 集成测试 | 模拟微信支付通知，验证签名校验和幂等性 |
| 购物车合并叠加 | 单元测试 | 相同商品重复添加，数量正确叠加 |
| 订单越权访问 | 集成测试 | 用户 A 无法访问用户 B 的订单 |
| 优惠券防刷 | 单元测试 | UUID 唯一性、每日上限校验 |
| 雪花算法 ID | 单元测试 | 并发生成 ID 不重复、趋势递增 |

### 9.4 覆盖率目标

| 模块 | 覆盖率目标 |
|------|-------------|
| 业务逻辑（services/） | ≥ 80% |
| 数据模型（models/） | ≥ 90% |
| API 路由（routes/） | ≥ 80% |
| 工具函数（utils/） | ≥ 95% |

---

## 十、UX 设计规范

### 10.1 页面状态设计

#### 购物车状态

| 状态 | 视觉表现 | 文案引导 |
|------|----------|----------|
| **空购物车** | 插画 + 主按钮 | "购物车是空的，去挑些新鲜水果吧" |
| **加载中** | 骨架屏 | — |
| **商品失效（已下架）** | 商品灰显 + 删除线 | "该商品已下架，是否删除？" |
| **库存不足** | 库存数字标红 | "库存不足，最多可购买 X 件" |
| **结算失败** | toast 提示 | "库存不足，请返回购物车修改" |

#### 订单追踪节点（E6）

以时间线形式展示在订单详情页底部：

```
┌─────────────────────────────────────┐
│ 订单追踪                             │
├─────────────────────────────────────┤
│ ● ● ● ○                             │
│ │   │   │                           │
│ ▼   ▼   ▼                           │
│ 已    已    待收货                   │
│ 采摘  发货                          │
│                                     │
│ 2024-03-15 08:00 已采摘             │
│ 2024-03-15 14:00 已打包发出         │
└─────────────────────────────────────┘
```

### 10.2 信息层级规范

#### 首页信息层级

```
┌─────────────────────────────┐
│ 轮播 Banner（自动轮播 3s）   │ ← 首屏
├─────────────────────────────┤
│ 快捷分类（横向滚动 6个）      │ ← 首屏
├─────────────────────────────┤
│ 热销推荐（横向滑动卡片）      │ ← 首屏
├─────────────────────────────┤
│ 商品列表（双列瀑布流）        │ ← 首屏
├─────────────────────────────┤
│ 店主故事（图文介绍）          │ ← 第二屏（情感补充）
└─────────────────────────────┘
```

#### 商品详情页信息层级

```
┌─────────────────────────────┐
│ 商品主图（可滑动）           │ ← 首屏
├─────────────────────────────┤
│ 价格 + 规格标签              │ ← 首屏
├─────────────────────────────┤
│ 商品名称 + 销量              │ ← 首屏
├─────────────────────────────┤
│ 规格选择（如：500g / 1000g） │ ← 首屏（E2）
├─────────────────────────────┤
│ 采蜜日期 / 品种信息（E2/E3） │ ← 第二屏
├─────────────────────────────┤
│ 商品详情图文                 │ ← 可滑动
├─────────────────────────────┤
│ 礼盒包装 □ + 贺卡祝福语输入  │ ← E4，商品详情页可选
├─────────────────────────────┤
│ [加入购物车] [立即购买]      │ ← 底部悬浮
└─────────────────────────────┘
```

### 10.3 交互规范

| 场景 | 交互行为 |
|------|----------|
| 规格选择 | 点击规格按钮，选中态高亮，支持多规格组合 |
| 加入购物车 | 按钮缩放动画 + 数字角标 +1 |
| 礼盒勾选 | 勾选后展开贺卡输入框，最多 50 字 |
| 优惠券领取 | 领取成功 toast，优惠券入账个人中心 |
| 结算页 | 自动选中可用最优券，提示已节省 X 元 |

### 10.4 响应式规范

微信小程序需适配不同机型：

| 机型 | 适配策略 |
|------|----------|
| iPhone SE | 商品卡片单列，文字缩小 |
| iPhone 14/15 | 双列瀑布流 |
| 大屏安卓 | 双列 + 更大点击区域 |

---

## 十一、初始数据

### 商品分类
| id | name | sort |
|----|------|------|
| 1 | 新鲜苹果 | 1 |
| 2 | 天然蜂蜜 | 2 |
| 3 | 组合套餐 | 3 |

### 示例商品
| 名称 | 价格 | 分类 |
|------|------|------|
| 红富士苹果 5斤装 | 39.9 | 苹果 |
| 红富士苹果 10斤装 | 69.9 | 苹果 |
| 天然槐花蜜 500g | 59.9 | 蜂蜜 |
| 天然枣花蜜 500g | 69.9 | 蜂蜜 |

---

## 十二、品牌视觉规范（设计评审补充）

> v1.0 设计评审完成 — 2026-05-07
> 补充人：plan-design-review

### 12.1 品牌色彩系统

| 角色 | 色值 | 取意 |
|------|------|------|
| **主色（苹果红）** | `#E54D2E` 或 `#D4451D` | 取自苹果表皮的自然红色 |
| **辅助色（蜂蜜琥珀）** | `#F5A623` 或 `#E8973D` | 取自天然蜂蜜的琥珀色 |
| **背景色（米白）** | `#FBF8F4` 或 `#FFF9F0` | 暖白底色，不刺眼 |
| **文字主色** | `#333333` | 深灰，保证可读性 |
| **文字辅助色** | `#666666` | 中灰，次要信息 |
| **文字弱色** | `#999999` | 浅灰，占位、说明文字 |
| **分割线色** | `#EEEEEE` | 极浅灰，分割线专用 |

> 注：以上色值为推荐方向，具体色值需设计师确认后填入。避免使用纯黑(#000000)和纯白(#FFFFFF)。

### 12.2 字体规范

| 用途 | 字体方案 | 说明 |
|------|---------|------|
| **标题** | 轻量自定义字体（如思源黑体变体/站酷系列等） | 手工感/品牌调性，需压缩至50-150KB |
| **正文** | 系统字体栈：`PingFang SC`（iOS）/ `Roboto`（Android） | 保证可读性和加载速度 |

> 注：微信小程序自定义字体有加载限制（文件<2MB，首次加载延迟）。建议仅标题使用自定义字体，正文保持系统字体。

### 12.3 图片风格标准

#### 商品主图规格

| 项目 | 规格 |
|------|------|
| 尺寸 | 800×800px（最小） |
| 比例 | 1:1（正方形）或 4:3 |
| 数量 | 至少5张（主图+4张角度图） |
| 质量 | 不压缩原图上传（微信会自动压缩） |
| 背景 | 纯色或透明底，商品占图80%以上 |
| 禁止 | 文字水印、边框、马赛克 |

#### 商品详情图规格

| 项目 | 规格 |
|------|------|
| 宽度 | 统一宽度（不超过750px） |
| 风格 | 暖色调、生活场景、不摆拍 |
| 要求 | 至少1张细节图（如苹果表皮特写、蜂蜜拉丝图） |

#### 农户头像规格

| 项目 | 规格 |
|------|------|
| 尺寸 | 200×200px（最小） |
| 比例 | 1:1 或 3:4（竖向） |
| 风格 | 真实照片（非艺术照），建议户外果园场景 |

### 12.4 间距与布局系统

基于4px基准的间距系统：

| 标记 | 值 | 使用场景 |
|------|-----|---------|
| xs | 4px | 标签内文字间距、紧凑列表 |
| sm | 8px | 组件内部元素间距（图标+文字） |
| md | 16px | 卡片内边距、组件间距 |
| lg | 24px | 区块间距、屏幕左右留白（移动端） |
| xl | 32px | 大区块间距、段落间距 |
| xxl | 48px | 页面顶部/底部与内容的间距 |

**关键布局规则：**

| 规则 | 值 |
|------|---|
| 页面左右留白 | 16px（小屏）/ 24px（大屏） |
| 卡片内边距 | 16px |
| 卡片间距（双列瀑布流） | 12px |
| 卡片间距（单列） | 16px |
| 底部悬浮按钮高度 | 48px（触控友好） |
| 最小可点击区域 | 44px × 44px |

### 12.5 关键UI元素视觉约束（防AI slop）

| 元素 | 差异化方向 | 避免 |
|------|-----------|------|
| 热销推荐 | 用具体数字（如"已售4823件"），不用百分比标签 | 通用商品卡片 |
| 店主故事 | 真实照片 + 手写风格字体，不用库存图 | 摆拍商业图 |
| 订单追踪 | 用农产品相关的进度指示（如苹果/蜂蜜图标），不用通用圆点 | 通用时间线圆点 |
| 礼盒选项 | 手绘风格插图 | 商业摄影图 |

---

## 十三、用户旅程与情感弧线（设计评审补充）

### 13.1 用户情感旅程地图

| 步骤 | 用户行为 | 用户感受 | 计划是否有支持内容 |
|------|---------|---------|------------------|
| 1 | 打开小程序 | 这是什么？新鲜感 | 首页Banner + Slogan ✓ |
| 2 | 刷到商品 | 看起来不错 | 商品图质量标准 ✓（本节定义） |
| 3 | 看商品详情 | 真的可信吗？ | 生长状态Banner ✓ + 农户简介模块（本节定义） |
| 4 | 加入购物车 | 正在决策 | 礼盒贺卡选项（E4）✓ |
| 5 | 下单 | 放心吗？ | 微信支付信任背书 ✓ |
| 6 | 等待 | 焦急/期待 | 订单追踪节点（E6）✓ |
| 7 | 收到包裹 | 符合预期？ | 商品评价体系（本节定义）✓ |

### 13.2 农户简介模块规格

```
┌─────────────────────────────────────┐
│ [头像 80×80 圆形]  农户昵称          │
│ "一句话价值主张"                      │
├─────────────────────────────────────┤
│ 种植/养殖年限：X年    [展开更多]      │
└─────────────────────────────────────┘
```

| 项目 | 规格 |
|------|------|
| 头像 | 80×80px，圆形裁剪，居左 |
| 昵称 | 16px，加粗，颜色=主色 |
| 价值主张 | 14px，常规，颜色=深灰 |
| 年限信息 | 14px，颜色=浅灰，放在折叠区内 |
| 折叠区 | 默认收起，点击"展开更多"展开 |
| 展开内容上限 | 100字（超出截断） |

---

## 十四、完整交互状态矩阵（设计评审补充）

### 14.1 各功能模块状态定义

```
FEATURE              | LOADING          | EMPTY                | ERROR               | SUCCESS              | PARTIAL
---------------------|------------------|----------------------|---------------------|---------------------|--------
商品详情              | 骨架屏+占位图    | "暂无商品信息"        | toast网络错误       | 正常展示商品信息     | 商品已售罄见备注
订单列表              | 骨架屏           | "暂无订单，去逛逛吧"  | toast刷新失败+重试按钮 | 订单卡片列表       | 有取消/退款中订单
结算页                | 按钮loading态    | —                    | toast提示具体错误   | 跳转支付页           | 优惠券不可用（灰显提示）
个人中心              | 用户信息骨架屏   | 无订单/无优惠券占位图 | —                   | 正常展示            | 未登录态（跳转登录页）
商家后台-数据概览     | 数字骨架屏       | "暂无数据"            | 刷新按钮+错误说明    | 数据卡片展示        | 数据加载中
```

**备注：商品售罄状态处理**
- 保留购买入口（按钮显示"到货通知"而非隐藏）
- 文案："该商品已售罄，预计X天补货，可先收藏"
- 点击"到货通知"：记录用户手机号/推送订阅，到货后通知

---

## 十五、商品评价体系（设计评审补充）

### 15.1 评价功能规格

| 功能 | 说明 |
|------|------|
| 评分 | 5星制（必须） |
| 图片评价 | 可上传1-3张实物图（加强真实性） |
| 评价列表 | 按时间倒序，支持筛选（全部/有图/好评/差评） |
| 差评展示 | 正常展示，不折叠 |
| 匿名评价 | 默认不匿名，展示昵称和头像 |

### 15.2 评价展示样式

```
┌─────────────────────────────────────┐
│ [头像] 昵称          ⭐⭐⭐⭐⭐       │
│ 2024-03-15                           │
│ 商品描述：红富士苹果，收到个头均匀...  │
│ [图片1] [图片2]                       │
└─────────────────────────────────────┘
```

### 15.3 商家介入机制

- 商家可以回复评价（展示在评价下方）
- 差评（1-2星）触发客服通知，24小时内主动联系用户
- 因天然特性产生的差评（如"苹果太小"），由客服沟通解释，不删除评价

---

## 十六、商家后台移动端策略（设计评审补充）

### 16.1 决策

商家后台专注PC端使用，移动端仅通过**微信服务号/模板消息**推送订单通知。

### 16.2 移动端覆盖场景

| 场景 | 解决方案 |
|------|---------|
| 新订单通知 | 微信模板消息推送 |
| 订单状态变更通知 | 微信模板消息推送 |
| 查看订单（偶尔） | 商家H5可在移动端浏览（不保证美观） |
| 处理订单/发货 | 必须在PC端完成 |

---

## 十七、设计评审结论

### 17.1 评审前后对比

| 维度 | 评审前 | 评审后 |
|------|-------|-------|
| 信息架构 | 5/10 | 6/10 |
| 交互状态 | 5/10 | 6/10 |
| 用户旅程 | 3/10 | 5/10 |
| AI Slop风险 | 6/10 | 7/10 |
| 设计系统 | 2/10 | 6/10 |
| 响应式 | 4/10 | 6/10 |
| **总分** | **4/10** | **6/10** |

### 17.2 本次评审做出的设计决策

| # | 决策内容 |
|---|---------|
| 1 | 首页情感内容（店主故事）置于商品列表之后 |
| 2 | 商品售罄时保留购买入口 + 补货预期提示 |
| 3 | 商品详情页增加农户/产地简介模块（头像+昵称+一句话+可折叠详情） |
| 4 | 品牌色彩 = 苹果红 + 蜂蜜琥珀 + 米白背景（大地色系） |
| 5 | 标题用轻量自定义字体，正文用系统字体 |
| 6 | 图片质量标准（商品主图800×800×5张起，农户头像200×200真实照片） |
| 7 | 4px基准间距系统 |
| 8 | 农户简介模块规格（80px圆形头像+可折叠详情） |
| 9 | 商品评价体系（5星+图评+商家回复+差评24h客服介入） |
| 10 | 商家后台专注PC端，移动端仅做微信通知 |

### 17.3 后续建议

1. **设计师介入**：以上色值和字体方案需要设计师确认/优化，形成正式的DESIGN.md
2. **UI组件库选型**：建议在uView Plus基础上定制品牌色变量，而非完全自建组件库
3. **实现前复核**：正式开发前，建议用本设计文档与UI设计师对齐，避免理解偏差

---

## 十八、架构评审结论（plan-eng-review）

> v1.0 架构评审完成 — 2026-05-07
> 评审人：plan-eng-review

### 18.1 评审问题汇总

| # | 问题 | 严重度 | 决策 | 选项 |
|---|------|--------|------|------|
| 1A | 异步任务队列 | P1 | Celery + Redis | A |
| 1B | 商家后台 JWT 方案 | P1 | access_token 15min + refresh_token 7天，Redis存储 | A |
| 1C | 微信登录 session_key 处理 | P1 | session_key Redis存，7天过期，unionid按需转 | A |
| 1D | 微信支付回调安全 | P0 | 签名验证 + IP白名单 + 乐观锁 + 幂等键 | A |
| 1E | Redis 缓存策略 | P1 | 统一规范 + TTL + Cache-Aside + 穿透保护 | A |
| 1F | BackgroundTasks 模块名重名 | P2 | 改名 celery_tasks | A |
| 1G | 库存扣减无原子性 | P0 | 原子 UPDATE + 失败重试3次 | C |
| 1H | 订单状态机不完整 | P1 | 补充完整状态机 + 副作用定义 | A |
| 1I | 支付流程缺少关键步骤 | P1 | 补充预支付订单接口 + 回调通知接口 | A |
| 1J | 商家后台无操作日志 | P2 | 加 admin_operate_logs 审计表 | A |
| 1K | 雪花算法 machine_id 矛盾 | P3 | 文档注明单机限制，扩展时改用Redis分配 | A |
| 2A | 前后端分离不清 | P1 | 统一后端 + `/api/admin/` 前缀 | A |
| 2B | 错误码缺少 5xx 范围 | P2 | 补充 5xxx server-side 错误码 | A |
| 3A | 订单超时取消测试缺失 | P1 | 补充 Celery 定时任务测试 | A |
| 4A | 商品列表无分页 | P1 | 加分页 + 缓存策略 | A |
| 4B | 数据库连接池配置缺失 | P1 | 补充 pool_size=20 + max_overflow=10 | A |
| 4C | 小程序包体积未规划 | P1 | 规划分包策略（主包 + 分包） | A |

### 18.2 架构评审决策详情

#### 1A — 异步任务队列

采用 **Celery + Redis** 替代 FastAPI BackgroundTasks：
- 进程重启任务不丢失
- 多实例部署任务可分发
- 内置重试机制（`max_retries=3`）
- Flower 监控面板

```
Redis → Celery Broker → Celery Worker
                         ├── 订单超时检查（celery beat）
                         ├── 库存回滚任务
                         └── 微信支付回调处理
```

#### 1B — 商家后台 JWT 方案

- access_token：有效期 15 分钟，存内存
- refresh_token：有效期 7 天，存 Redis（key = `refresh:{user_id}`）
- 前端每次请求自动用 refresh_token 刷新（静默刷新）
- 登出时删除 Redis 中的 refresh_token（Token 立即失效）
- 商家后台所有 `/api/admin/` 接口校验 access_token

#### 1C — 微信登录 session_key 处理

- 小程序调用 `wx.login()` → 拿到 code → 传给后端
- 后端通过微信 API 换取 `openid` + `session_key`
- `session_key` 只存 Redis（不落 MySQL），7 天过期
- 支付时从 Redis 取 session_key 调用微信解密用户手机号
- unionid 通过微信官方接口按需转换，不主动存储

#### 1D — 微信支付回调安全

回调接口设计（`POST /api/pay/notify`）：
1. 验证微信签名（使用 `wxpay_signature`）
2. 验证请求 IP 在微信服务器 IP 白名单内
3. 使用订单号作为幂等键（idempotency_key），防止重复处理
4. 订单状态更新使用乐观锁（version 字段）
5. 处理成功后返回 `<xml><return_code><![CDATA[SUCCESS]]></return_code></xml>`

#### 1E — Redis 缓存策略

Key 命名规范：`{entity}:{id}:{field}`

| 缓存场景 | Key 示例 | TTL | 更新策略 |
|----------|----------|-----|----------|
| 用户 Session | `session:{openid}` | 7天 | 登录时创建，删除时清理 |
| 商家 Token | `refresh:{admin_id}` | 7天 | 刷新时更新，登录时删除 |
| 商品详情 | `product:{id}` | 5分钟 | Cache-Aside（读时填充） |
| 热门商品 | `products:hot:{category_id}` | 5分钟 | 定时刷新（Celery beat） |
| Banner配置 | `banner:growth_status` | 10分钟 | 写时删除（变更时主动清理） |

穿透保护：商品 ID 用布隆过滤器检查，存在才查 DB。

#### 1G — 库存扣减原子性

```python
# 原子扣减 + 乐观锁
for attempt in range(3):
    affected = db.execute(
        "UPDATE products SET stock = stock - :qty, version = version + 1 "
        "WHERE id = :id AND stock >= :qty AND version = :ver",
        {"qty": quantity, "id": product_id, "ver": current_version}
    )
    if affected > 0:
        return True  # 扣减成功
    db.refresh(product)  # 重新加载，重试
return False  # 库存不足或乐观锁冲突
```

#### 1H — 订单状态机

```
                    ┌─────────────────────────────┐
                    │  0 待付款                    │
                    │  （下单后开始计时 30分钟）    │
                    └──────────┬──────────────────┘
                               │
              ┌────────────────┴────────────────┐
              ▼                                  ▼
    ┌─────────────────┐               ┌─────────────────┐
    │  4 已取消        │               │  1 待发货        │
    │  （超时/主动取消） │               │  （支付成功）     │
    │  库存回滚✓       │               └────────┬────────┘
    │  优惠券退回✓     │                        │
    └─────────────────┘               ┌────────┴────────┐
                                       ▼                 ▼
                             ┌─────────────────┐  ┌─────────────────┐
                             │  2 待收货        │  │  6 退款中        │
                             │  （已发货）      │  │  （申请退款）     │
                             └────────┬────────┘  └────────┬────────┘
                                      │                      │
                           ┌──────────┴──────────┐            │
                           ▼                      ▼            ▼
                 ┌─────────────────┐   ┌─────────────────┐  ┌─────────────────┐
                 │  3 已完成        │   │  6 退款中→4已取消│  │  5 已退款        │
                 │  （确认收货）    │   │  （拒绝退款）   │  │  （退款成功）    │
                 └─────────────────┘   └─────────────────┘  └─────────────────┘
```

状态转换副作用：
- 0→4：库存回滚、优惠券退回、发送微信消息通知买家
- 0→1：库存正式扣减（乐观锁）、冻结优惠券
- 1→6：标记退款申请、暂停发货流程
- 2→5：触发微信退款 API、原路退回
- 4→5：检查是否已发货，已发货走退款流程

#### 1I — 支付流程补充

```
Step 1: 前端创建订单
  POST /api/orders → 返回 order_id + order_no

Step 2: 前端发起支付
  POST /api/pay/prepare {order_id}
    → 调用微信统一下单 API
    → 返回 {prepay_id, nonce_str, sign, timeStamp, package}
  
Step 3: 前端调起微信支付
  wx.requestPayment({prepay_id, ...})

Step 4: 微信服务器回调
  POST /api/pay/notify
    → 签名验证 → 幂等处理 → 更新订单状态 → 库存扣减 → 发送通知
    → 返回 SUCCESS

Step 5: 前端轮询确认
  GET /api/orders/:id → 返回最终支付状态
```

新增 API：
- `POST /api/pay/prepare` — 预支付订单创建
- `POST /api/pay/notify` — 微信支付回调

#### 2A — API 前缀统一

所有商家后台 API 使用 `/api/admin/` 前缀，与用户端 API 在同一 FastAPI 实例：

```
用户端：  GET /api/products
商家后台：GET /api/admin/products
```

#### 3A — 订单超时取消 Celery 任务

```python
@celery_app.task
def cancel_expired_orders():
    """Celery beat 每分钟执行：取消超时订单"""
    expired = orders.filter(
        status=0,  # 待付款
        created_at < datetime.utcnow() - timedelta(minutes=30)
    ).all()
    for order in expired:
        order.status = 4  # 已取消
        restore_stock.delay(order.id)  # 回滚库存
        release_coupon.delay(order.user_id, order.coupon_id)  # 退回优惠券
        send_cancel_notification.delay(order.id)  # 微信消息通知
```

### 18.3 NOT in scope

以下在本计划中明确不包含：

|  deferred | 原因 |
|-----------|------|
| 分布式雪花算法 machine_id 分配 | Phase 1-4 单机部署，暂时不需要 |
| 微信分账/退款对账脚本 | 退款量小，先手动处理 |
| 小程序数据分析后台 | 使用微信官方数据分析即可 |
| 商家后台移动端完整适配 | 只有微信通知，H5 可浏览不保证美观 |
| 短信服务接入 | 目前不需要，微信消息已够用 |
| 阿里云/腾讯云具体配置 | 需要实际部署时再定 |

### 18.4 What Already Exists

| 已有内容 | 是否复用 | 说明 |
|----------|----------|------|
| 雪花算法 Python 实现 | ✓ 重用 | `app/utils/snowflake.py` |
| SQLAlchemy 模型 | ✓ 重用 | 补充新字段（version, session_key） |
| uView Plus 组件库 | ✓ 重用 | 在此基础上定制品牌变量 |
| ELK 日志方案 | ✓ 重用 | 完整方案，无需改动 |
| Prometheus + Grafana 监控 | ✓ 重用 | 补充 Celery 监控指标 |
| pytest 测试框架 | ✓ 重用 | 新增 Celery + 微信支付测试 |

### 18.5 实施并行化策略

| Lane | 步骤 | 涉及模块 | 依赖 |
|------|------|----------|------|
| A | 后端基础设施（JWT/Celery/Redis） | backend/app/core/ | 无 |
| A | 数据库新表和字段（admin_operate_logs/version/idempotency） | database/schema.sql | A 完成后 |
| B | 支付流程（预下单/回调/幂等） | backend/app/api/pay/ | A |
| B | 订单超时 Celery Beat 定时任务 | backend/app/tasks/ | A |
| C | 商家后台 API（带审计日志） | backend/app/api/admin/ | B（支付相关） |
| D | 小程序分包策略实施 | frontend/ | 无 |
| D | 商品列表分页 + 缓存 | backend/app/api/products/ | A |

**Lane A 可独立启动，B 和 D 可在 A 完成后并行。**

### 18.6 架构评审前后对比

| 维度 | 评审前 | 评审后 |
|------|--------|--------|
| 异步任务 | BackgroundTasks（内存） | Celery + Redis（持久化） |
| 商家认证 | JWT 无刷新 | access_token 15m + refresh_token 7d |
| 微信登录 | 无 session_key 处理 | Redis 存 7 天过期 |
| 支付安全 | 空白 | 签名+IP白名单+幂等+乐观锁 |
| 库存扣减 | 读-改-写分离 | 原子 UPDATE + 乐观锁 + 重试 |
| 订单状态机 | 5 状态无转换规则 | 完整状态机 + 副作用定义 |
| 缓存策略 | 空白 | 统一 key + TTL + Cache-Aside |
| 审计日志 | 空白 | admin_operate_logs 表 |
| API 前缀 | 模糊 | `/api/admin/` 统一前缀 |
| 错误码 | 缺少 5xx | 5xxx server-side 补充 |
| 商品列表 | 无分页无缓存 | 分页 + 缓存策略 |
| 连接池 | 默认值 | pool_size=20 + max_overflow=10 |
| 小程序分包 | 无规划 | 主包 + 分包策略 |

---

## 十九、测试计划（eng-review 补充）

> plan-eng-review 补充测试场景

### 核心测试场景（必须覆盖）

| 测试场景 | 类型 | 工具 | 覆盖要求 |
|----------|------|------|----------|
| 库存原子扣减（并发） | 并发压测 | pytest-xdist | 100并发不超卖，≥3次 |
| 微信支付回调幂等 | 集成测试 | pytest + mock | 同一订单号两次回调，状态不变 |
| 微信支付回调签名 | 集成测试 | pytest + mock | 伪造签名被拒绝 |
| 订单超时取消 + 库存回滚 | Celery 任务测试 | pytest-celery | 30分钟后订单取消，库存恢复 |
| 乐观锁冲突重试 | 单元测试 | pytest | version 不匹配时自动重试 |
| 商家后台 JWT 刷新 | 集成测试 | TestClient | access_token 过期静默刷新 |
| session_key 过期处理 | 集成测试 | mock Redis | session_key 过期后静默重新登录 |
| 订单越权访问 | 集成测试 | TestClient | 用户 A 无法访问用户 B 订单 |
| 库存回滚一致性 | 集成测试 | pytest | 订单取消后库存数据一致 |
| Celery 任务重试 | 单元测试 | pytest-mock | 微信回调失败自动重试 3 次 |

### 覆盖率目标（eng-review 补充）

| 模块 | 覆盖率目标 | 补充 |
|------|-----------|------|
| services/order.py | ≥ 90% | 含状态机每个转换分支 |
| services/pay.py | ≥ 95% | 支付回调为最高风险，必须接近全覆盖 |
| tasks/celery_tasks.py | ≥ 80% | 定时任务每个分支 |
| middleware/auth.py | ≥ 90% | JWT 刷新逻辑 |

---

## 二十、架构评审结论

| 项目 | 数值 |
|------|------|
| Step 0 Scope Challenge | scope accepted（复杂度警告已处理） |
| Architecture Review | 11 issues found, all resolved |
| Code Quality Review | 2 issues found, all resolved |
| Test Review | coverage diagram produced, 10 gaps identified |
| Performance Review | 3 issues found, all resolved |
| NOT in scope | 6 items documented |
| What Already Exists | 6 items documented |
| TODOS.md updates | 0 items proposed |
| Failure modes | 3 critical gaps (库存超卖、支付回调伪造、session_key泄露) |
| Parallelization | 4 lanes, A runs solo, B+D parallel after A |
| Lake Score | 17/17 chose complete option (A/B) |
