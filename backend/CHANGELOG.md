# 更新日志

## 2026-06-07

### 修复 — 后端测试 4 项修复（271/271 全绿）
- `app/models/cart_item.py` — 添加 `created_at` 列，修复 CartItemResponse 字段缺失错误
- `app/models/invite.py` — `invitee_id` 和 `order_id` 改为 `nullable=True`，修复生成邀请码时 NOT NULL 约束失败
- `app/models/order.py` — 添加 `pay_time`、`discount_amount`、`updated_at` 列，修复响应用 `order.pay_time` 时 AttributeError 和 `discount_amount` 无效参数错误
- `app/api/routes/order.py` — `snowflake.next_id()` → `snowflake()`（`generate_order_no` 是函数而非对象），修复 TypeError

### 统一 — 小程序 API 路径对齐后端路由
- `frontend/mini-app/src/api/request.ts` — 将旧 `/api/v1/...` 路径批量修正为后端实际路由：
  - 商品：`/api/products`、`/api/products/{id}`、`/api/categories`
  - 购物车：`/api/cart`（GET/POST/PUT/DELETE）、`/api/cart/select-all`
  - 订单：`/api/orders`（GET/POST）、`/api/orders/{order_no}`、`/api/orders/{order_no}/cancel`、`/api/orders/{order_no}/confirm`、`/api/orders/{order_no}/refund`
  - 地址：`/api/addresses`（GET/POST/PUT/DELETE）、`/api/addresses/default`、`/api/addresses/{id}/default`
  - 优惠券：`/api/coupons`、`/api/coupons/claim`
  - 用户：`/api/user/info`、`/api/user/update`
  - 首页：`/api/home/data`
  - 邀请：`POST /api/invites/generate`
- `frontend/mini-app/src/pages/cart/index.js` — `removeCart([id])` → `removeCart(id)` 适配新接口
- 所有 API 路径已与后端真实路由完全对齐

### 新增 — 缺失的后端接口（Step 3）
- `app/api/routes/user.py` — `GET /api/user/info`、`POST /api/user/update`（Bearer Token 认证）
- `app/api/routes/home.py` — `GET /api/home/data`（公开，聚合 banners/categories/products/growth_status）
- `app/api/routes/cart.py` — 新增 `POST /api/cart/select-all`（批量全选/取消全选）
- `app/api/routes/order.py` — 新增 `POST /api/orders/{order_no}/cancel`（状态 0→4+回滚库存）、`POST /api/orders/{order_no}/confirm`（状态 2→3）、`POST /api/orders/{order_no}/refund`（状态 1→6）
- `app/api/routes/address.py` — 新增 `GET /api/addresses/default`（返回用户默认地址）
- `tests/test_api/test_user_home.py` — 新增 5 个测试（用户信息+首页）
- `tests/test_api/test_cart.py` — 新增 3 个测试（全选）
- `tests/test_api/test_order.py` — 新增 12 个测试（取消/确认/退款+越权检查）
- `tests/test_api/test_address.py` — 新增 4 个测试（默认地址）
- **测试结果：295 passed，0 failed**

### 新增 — 微信支付闭环（P0-3）
- `app/utils/wxpay.py` — 微信支付公共工具
  - `build_sign(params, key)` — MD5 签名生成（自动排除 sign 和空值字段）
  - `verify_sign(params, key)` — 签名验证（大小写不敏感）
  - `dict_to_xml(d)` / `xml_to_dict(xml)` — 微信 XML 互转（统一 CDATA 包装）
  - `wx_unified_order(payload)` — 调用微信统一下单 HTTP API
- `app/schemas/pay.py` — `PrepareRequest{order_no}`、`PrepareData{timeStamp,nonceStr,package,signType,paySign}`
- `app/services/pay_service.py`：
  - `create_prepay_order(db, user_id, order_no)` — 预下单流程：订单校验 → 微信统一下单 → 生成前端 wx.requestPayment 所需 5 元素
  - `handle_pay_notify(db, xml_body)` — 回调处理：解析 → 验签 → 幂等检查 → 订单状态 0→1
  - 幂等约定：已付款订单二次回调直接返回 SUCCESS；已取消订单回 SUCCESS 防重试；签名错误/订单不存在返回 FAIL 让微信重试
- `app/api/routes/pay.py` — `POST /api/pay/prepare`（需要 Bearer Token）、`POST /api/pay/notify`（无认证，验签即认证），并在 `routes/__init__.py` 注册
- `app/core/config.py` 新增 `WX_PAY_MCH_ID / WX_PAY_KEY / WX_PAY_NOTIFY_URL / WX_PAY_SPBILL_IP`，`.env` 同步加占位
- `tests/test_services_pay.py` — 17 个 service 测试（签名/XML 工具 6 个 + 预下单 5 个 + 回调 6 个，含微信失败/幂等/已取消订单等场景）
- `tests/test_api/test_pay.py` — 4 个 API 集成测试（含 token 鉴权验证）
- 覆盖率：pay_service **93%**、routes/pay **90%**、wxpay **79%**、core/security **83%**（get_current_user 现已被覆盖）

### 改进 — 小程序端支付对接
- `frontend/mini-app/src/api/request.ts`（修正 wxpayApi）：
  - `prepay()` 路径从 `/api/v1/wxpay/prepay` → `/api/pay/prepare`
  - 不再前端传 user_id，由 Bearer Token 自动注入
  - 返回类型升级为 wx.requestPayment 所需的 5 字段（与后端契约一致）

### 新增 — 微信登录与 Token 刷新（P0-2）
- `app/schemas/auth.py` — `WxLoginRequest / WxLoginData / UserInfoBrief / TokenRefreshRequest / TokenRefreshData`
- `app/services/auth_service.py`：
  - `code2session(code)` — 调用微信 `https://api.weixin.qq.com/sns/jscode2session` 工具函数（用 httpx）
  - `WxLoginError` — 微信 errcode 异常封装
  - `wx_login(db, code, nickname, avatar_url)` — 主登录流程：参数校验 → code2session → get_or_create_user_by_openid → 签发 access+refresh token
  - `refresh_access_token(db, refresh_token)` — refresh_token 换取新 access_token，强校验 type=refresh、用户存在
- `app/api/routes/auth.py` — `POST /api/auth/wxlogin`、`POST /api/auth/refresh`，并在 `routes/__init__.py` 注册到 router
- `app/core/security.py` 新增 `get_current_user(authorization, db)` FastAPI 依赖：从 `Authorization: Bearer <token>` 解析当前登录用户，失败 raise HTTPException(401)
- `tests/test_services_auth.py` — 11 个 service 测试用例（mock 微信 API，覆盖新老用户、空 code、微信 errcode、refresh 各分支）
- `tests/test_api/test_auth.py` — 7 个 API 集成测试用例
- 覆盖率：auth_service **92%**、routes/auth **100%**、schemas/auth **100%**

### 新增 — 小程序端登录闭环
- `frontend/mini-app/src/api/auth.ts`（新建）— `wxLogin(extra?)`、`refreshAccessToken()`，自动写入 `token / refresh_token / userInfo` 到 storage
- `frontend/mini-app/src/api/request.ts`（增强）：
  - 401 自动调用 `/api/auth/refresh` 并重试原请求一次
  - 并发 401 场景下用队列防止重复刷新
  - 修正 `userApi.wxLogin` 路径：`/api/v1/user/wx-login` → `/api/auth/wxlogin`
- `frontend/mini-app/src/app.js`（增强）— `checkLogin()` 无登录态时静默调 `wxLogin()` 自动登录；401 处理同步清除 `refresh_token`

### 重构
- 修正项目目录结构：将微信小程序代码从 `backend/mini-app/` 整体迁移至 `frontend/mini-app/`，符合 `CLAUDE.md` 中规定的项目结构（前后端分离）。
  - 影响范围：仅文件物理位置变更，不涉及代码内容修改
  - 验证：`frontend/mini-app/src/app.json`、`project.config.json` 路径正常

## 2026-05-10

### 新增
- `app/services/product_service.py` — 商品服务层，包含以下5个函数：
  - `get_products(db, category_id, status, page, page_size)` — 商品列表分页查询，支持按分类和状态筛选
  - `get_product(db, product_id)` — 商品详情查询，不存在返回 NOT_FOUND
  - `create_product(db, data)` — 创建商品
  - `update_product(db, product_id, data)` — 更新商品信息，不存在返回 NOT_FOUND
  - `update_stock(db, product_id, delta_quantity)` — 库存增减（正加负减），库存不足返回 STOCK_NOT_ENOUGH
