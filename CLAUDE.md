# GWP小店 - 开发上下文

## 产品概述
- **产品名称**：GWP的小店
- **产品Slogan**：自然好味，从田间到舌尖
- **目标用户**：注重健康饮食的城市家庭，追求天然无添加食品的消费者
- **核心价值**：提供自家产的优质苹果和蜂蜜，直连农户与消费者

## 技术栈

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| 用户端小程序 | Vue 3 + uni-app | 跨端框架，可发布到微信小程序、H5等 |
| 状态管理 | Pinia | uni-app 官方推荐状态管理库 |
| UI组件库 | uView Plus | uni-app生态最完善的UI组件库 |
| 商家后台H5 | Vue 3 + Vite + Element Plus | 独立部署的H5管理后台 |
| 后端语言 | Python 3.9+ | |
| Web框架 | FastAPI | 高性能异步框架 |
| 数据库 | MySQL 8.0+ | 关系型数据库 |
| ORM | SQLAlchemy 2.0 | Python ORM框架 |
| 缓存 | Redis | 会话、数据缓存 |
| 任务队列 | Celery + Redis | 异步任务处理 |

## 开发要求

### 严格遵循设计文档
- 所有功能必须按照 `GWP小店产品设计文档.md` 实现
- 不擅自增加或减少功能
- API接口必须与文档完全一致

### 测试驱动开发 (TDD)
遵循 RED-GREEN-REFACTOR 周期：
1. **RED**: 先写失败的测试
2. **GREEN**: 编写最小代码通过测试
3. **REFACTOR**: 重构优化

### 测试命令
```bash
# 运行所有测试
pytest tests/ -q

# 运行单个测试文件
pytest tests/test_feature.py -v

# 带覆盖率运行
pytest tests/ --cov=app --cov-report=term-missing
```

### 覆盖率目标
- 业务逻辑 (services/) ≥ 80%
- 数据模型 (models/) ≥ 90%
- API路由 (routes/) ≥ 80%
- 工具函数 (utils/) ≥ 95%

## 项目结构

```
/home/myproject01/
├── GWP小店产品设计文档.md      # 设计文档
├── frontend/                    # 前端 uni-app 项目
│   └── mini-app/              # 小程序代码
├── admin/                      # 商家后台 H5 项目
├── backend/                    # Python后端
│   ├── app/
│   │   ├── api/              # 路由
│   │   ├── models/           # 数据模型
│   │   ├── schemas/          # Pydantic模式
│   │   ├── services/         # 业务逻辑
│   │   ├── core/             # 核心配置
│   │   ├── tasks/           # Celery任务
│   │   └── utils/           # 工具函数
│   ├── alembic/              # 数据库迁移
│   ├── tests/                # 测试
│   ├── .env                  # 环境变量
│   └── requirements.txt
├── database/                   # 数据库脚本
│   ├── schema.sql            # 建表脚本
│   └── seed.sql              # 初始数据
└── docs/                      # 文档
```

## 数据库表 (13张)

1. **users** - 用户表
2. **products** - 商品表
3. **orders** - 订单表
4. **order_items** - 订单商品表
5. **addresses** - 收货地址表
6. **categories** - 商品分类表
7. **cart_items** - 购物车表
8. **admin_users** - 商家后台用户表
9. **coupons** - 优惠券表
10. **invites** - 邀请记录表
11. **banner_configs** - Banner配置表
12. **product_extras** - 商品扩展表
13. **admin_operate_logs** - 管理员操作日志表

## 核心API接口

### 用户端API
- `GET /api/products` - 商品列表
- `GET /api/products/:id` - 商品详情
- `GET /api/categories` - 分类列表
- `GET /api/cart` - 获取购物车
- `POST /api/cart` - 添加商品
- `PUT /api/cart/:id` - 更新数量
- `DELETE /api/cart/:id` - 删除商品
- `POST /api/orders` - 创建订单
- `GET /api/orders` - 订单列表
- `GET /api/orders/:id` - 订单详情
- `POST /api/orders/:id/pay` - 发起订单支付
- `GET /api/orders/:id/tracking` - 查询追踪节点
- `GET /api/addresses` - 收货地址列表
- `POST /api/addresses` - 添加地址
- `PUT /api/addresses/:id` - 更新地址
- `DELETE /api/addresses/:id` - 删除地址
- `PUT /api/addresses/:id/default` - 设为默认
- `POST /api/coupons/claim` - 领取优惠券
- `GET /api/coupons` - 我的优惠券列表
- `GET /api/coupons/apply` - 查询可用优惠券
- `POST /api/invites/generate` - 生成邀请码
- `GET /api/invites/history` - 邀请记录
- `GET /api/banners/growth-status` - 获取生长状态Banner

### 商家后台API (前缀: /api/admin/)
- `POST /api/admin/login` - 商家登录
- `GET /api/admin/stats` - 数据统计
- `GET /api/admin/products` - 商品列表
- `POST /api/admin/products` - 添加商品
- `PUT /api/admin/products/:id` - 更新商品
- `PUT /api/admin/products/:id/extras` - 更新商品扩展信息
- `PUT /api/admin/products/:id/status` - 上下架
- `GET /api/admin/orders` - 订单列表
- `PUT /api/admin/orders/:id/ship` - 订单发货
- `PUT /api/admin/orders/:id/tracking` - 更新追踪节点
- `GET /api/admin/banners` - Banner配置列表
- `POST /api/admin/banners` - 创建Banner
- `PUT /api/admin/banners/:id` - 更新Banner

### 支付API
- `POST /api/pay/prepare` - 预支付订单创建
- `POST /api/pay/notify` - 微信支付回调

## 订单状态机

```
0 待付款 → 1 待发货 → 2 待收货 → 3 已完成
    ↓           ↓           ↓
  4 已取消    6 退款中    5 已退款
              ↓
          4 已取消 (拒绝退款)
```

状态转换副作用：
- 0→4：库存回滚、优惠券退回、发送微信消息通知买家
- 0→1：库存正式扣减（乐观锁）、冻结优惠券
- 1→6：标记退款申请、暂停发货流程
- 2→5：触发微信退款API、原路退回

## 雪花算法ID

使用 snowflake 库生成唯一ID：
```python
from snowflake import Snowflake
snowflake = Snowflake(epoch=1577836800000, machine_id=1)
user_uid = snowflake.next_id()
order_no = snowflake.next_id()
```

## 错误码

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1001 | 参数错误 |
| 1002 | 签名验证失败 |
| 1003 | 无访问权限 |
| 1004 | 资源不存在 |
| 2001 | 库存不足 |
| 2002 | 订单不存在 |
| 2003 | 订单状态不允许此操作 |
| 2004 | 支付失败 |
| 3001 | 用户不存在 |
| 3002 | 登录凭证过期 |
| 4001 | 优惠券不存在 |
| 4002 | 优惠券已过期 |
| 4003 | 优惠券已使用 |
| 4004 | 不满足使用条件 |
| 5001 | 商家后台权限不足 |
| 5002 | 服务器内部错误 |

## 关键测试场景

1. **库存原子扣减（并发）** - pytest-xdist 多进程并发下单，验证超卖防护
2. **微信支付回调幂等** - 同一订单号两次回调，状态不变
3. **订单超时取消 + 库存回滚** - Celery beat 30分钟后订单取消，库存恢复
4. **乐观锁冲突重试** - version不匹配时自动重试
5. **商家后台 JWT 刷新** - access_token过期静默刷新
6. **订单越权访问** - 用户A无法访问用户B订单
