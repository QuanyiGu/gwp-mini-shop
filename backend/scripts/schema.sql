-- ============================================
-- GWP小店 数据库建表脚本
-- MySQL 8.0+ 兼容
-- ============================================

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS gwp_shop
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE gwp_shop;

-- ============================================
-- 1. users - 用户表
-- ============================================
CREATE TABLE IF NOT EXISTS `users` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '用户ID',
    `uid` VARCHAR(32) NOT NULL COMMENT '用户UID',
    `openid` VARCHAR(64) NULL COMMENT '微信openid',
    `unionid` VARCHAR(64) NULL COMMENT '微信unionid',
    `nickname` VARCHAR(128) NULL COMMENT '昵称',
    `avatar_url` VARCHAR(512) NULL COMMENT '头像URL',
    `phone` VARCHAR(32) NULL COMMENT '手机号',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_uid` (`uid`),
    UNIQUE KEY `uk_openid` (`openid`),
    UNIQUE KEY `uk_unionid` (`unionid`),
    KEY `ix_users_openid` (`openid`),
    KEY `ix_users_unionid` (`unionid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ============================================
-- 2. categories - 商品分类表
-- ============================================
CREATE TABLE IF NOT EXISTS `categories` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '分类ID',
    `name` VARCHAR(64) NOT NULL COMMENT '分类名称',
    `icon` VARCHAR(512) NULL COMMENT '分类图标',
    `sort` INT NULL COMMENT '排序值',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品分类表';

-- ============================================
-- 3. admin_users - 商家后台用户表
-- ============================================
CREATE TABLE IF NOT EXISTS `admin_users` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '管理员ID',
    `username` VARCHAR(64) NOT NULL COMMENT '用户名',
    `password_hash` VARCHAR(256) NOT NULL COMMENT '密码哈希',
    `nickname` VARCHAR(64) NOT NULL COMMENT '昵称',
    `role` VARCHAR(32) NOT NULL COMMENT '角色: super_admin/admin',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`),
    KEY `ix_admin_users_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商家后台用户表';

-- ============================================
-- 4. products - 商品表
-- ============================================
CREATE TABLE IF NOT EXISTS `products` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '商品ID',
    `category_id` BIGINT NOT NULL COMMENT '分类ID',
    `name` VARCHAR(256) NOT NULL COMMENT '商品名称',
    `main_image` VARCHAR(512) NOT NULL DEFAULT '' COMMENT '主图URL',
    `images` TEXT NULL COMMENT '图片列表(JSON数组)',
    `description` TEXT NULL COMMENT '商品描述',
    `price` DECIMAL(10,2) NOT NULL COMMENT '售价',
    `original_price` DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT '原价',
    `stock` INT NOT NULL DEFAULT 0 COMMENT '库存',
    `sales` INT NOT NULL DEFAULT 0 COMMENT '销量',
    `status` INT NOT NULL DEFAULT 1 COMMENT '状态: 1=上架 0=下架',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `ix_products_category_id` (`category_id`),
    CONSTRAINT `fk_products_category` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品表';

-- ============================================
-- 5. admin_operate_logs - 管理员操作日志表
-- ============================================
CREATE TABLE IF NOT EXISTS `admin_operate_logs` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '日志ID',
    `admin_id` BIGINT NOT NULL COMMENT '管理员ID',
    `action` VARCHAR(64) NOT NULL COMMENT '操作类型',
    `target_type` VARCHAR(64) NOT NULL COMMENT '操作对象类型',
    `target_id` BIGINT NOT NULL COMMENT '操作对象ID',
    `detail` TEXT NULL COMMENT '操作详情',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    PRIMARY KEY (`id`),
    KEY `ix_admin_operate_logs_admin_id` (`admin_id`),
    CONSTRAINT `fk_admin_logs_admin` FOREIGN KEY (`admin_id`) REFERENCES `admin_users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='管理员操作日志表';

-- ============================================
-- 6. addresses - 收货地址表
-- ============================================
CREATE TABLE IF NOT EXISTS `addresses` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '地址ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `name` VARCHAR(64) NOT NULL COMMENT '收货人姓名',
    `phone` VARCHAR(32) NOT NULL COMMENT '手机号',
    `province` VARCHAR(64) NOT NULL COMMENT '省份',
    `city` VARCHAR(64) NOT NULL COMMENT '城市',
    `district` VARCHAR(64) NOT NULL COMMENT '区县',
    `detail` VARCHAR(512) NOT NULL COMMENT '详细地址',
    `is_default` INT NULL DEFAULT 0 COMMENT '是否默认: 1=是 0=否',
    PRIMARY KEY (`id`),
    KEY `ix_addresses_user_id` (`user_id`),
    CONSTRAINT `fk_addresses_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='收货地址表';

-- ============================================
-- 7. coupons - 优惠券表
-- ============================================
CREATE TABLE IF NOT EXISTS `coupons` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '优惠券ID',
    `code` VARCHAR(64) NOT NULL COMMENT '优惠券码',
    `user_id` BIGINT NOT NULL COMMENT '所属用户ID: 0=未领取',
    `type` INT NOT NULL DEFAULT 1 COMMENT '类型: 1=满减券',
    `discount` DECIMAL(10,2) NOT NULL COMMENT '优惠金额',
    `min_amount` DECIMAL(10,2) NOT NULL DEFAULT 0 COMMENT '最低消费金额',
    `status` INT NOT NULL DEFAULT 0 COMMENT '状态: 0=未使用 1=已使用 2=已过期',
    `expires_at` DATETIME NOT NULL COMMENT '过期时间',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_code` (`code`),
    KEY `ix_coupons_code` (`code`),
    KEY `ix_coupons_user_id` (`user_id`),
    CONSTRAINT `fk_coupons_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='优惠券表';

-- ============================================
-- 8. cart_items - 购物车表
-- ============================================
CREATE TABLE IF NOT EXISTS `cart_items` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '购物车项ID',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `product_id` BIGINT NOT NULL COMMENT '商品ID',
    `quantity` INT NOT NULL DEFAULT 1 COMMENT '数量',
    `selected` INT NULL DEFAULT 1 COMMENT '是否选中: 1=选中 0=未选中',
    PRIMARY KEY (`id`),
    KEY `ix_cart_items_user_id` (`user_id`),
    KEY `ix_cart_items_product_id` (`product_id`),
    CONSTRAINT `fk_cart_items_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
    CONSTRAINT `fk_cart_items_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='购物车表';

-- ============================================
-- 9. orders - 订单表
-- ============================================
CREATE TABLE IF NOT EXISTS `orders` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '订单ID',
    `order_no` VARCHAR(64) NOT NULL COMMENT '订单号',
    `user_id` BIGINT NOT NULL COMMENT '用户ID',
    `total_amount` DECIMAL(10,2) NOT NULL COMMENT '商品总价',
    `pay_amount` DECIMAL(10,2) NOT NULL COMMENT '实付金额',
    `address_name` VARCHAR(64) NOT NULL COMMENT '收货人姓名',
    `address_phone` VARCHAR(32) NOT NULL COMMENT '收货人电话',
    `address_detail` VARCHAR(512) NOT NULL COMMENT '收货地址',
    `status` INT NOT NULL DEFAULT 0 COMMENT '状态: 0=待付款 1=待发货 2=待收货 3=已完成 4=已取消 5=已退款 6=退款中',
    `gift_package` INT NULL DEFAULT 0 COMMENT '礼盒包装: 0=否 1=是',
    `greeting_card` TEXT NULL COMMENT '留言卡片',
    `tracking_node` TEXT NULL COMMENT '物流追踪节点(JSON数组)',
    `logistics_company` VARCHAR(64) NULL COMMENT '物流公司',
    `logistics_no` VARCHAR(128) NULL COMMENT '物流单号',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_order_no` (`order_no`),
    KEY `ix_orders_order_no` (`order_no`),
    KEY `ix_orders_user_id` (`user_id`),
    CONSTRAINT `fk_orders_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单表';

-- ============================================
-- 10. order_items - 订单商品表
-- ============================================
CREATE TABLE IF NOT EXISTS `order_items` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '订单项ID',
    `order_id` BIGINT NOT NULL COMMENT '订单ID',
    `product_id` BIGINT NOT NULL COMMENT '商品ID',
    `product_name` VARCHAR(256) NOT NULL COMMENT '商品名称(快照)',
    `product_image` VARCHAR(512) NOT NULL COMMENT '商品图片(快照)',
    `price` DECIMAL(10,2) NOT NULL COMMENT '商品单价(快照)',
    `quantity` INT NOT NULL COMMENT '购买数量',
    `total_price` DECIMAL(10,2) NOT NULL COMMENT '小计金额',
    PRIMARY KEY (`id`),
    KEY `ix_order_items_order_id` (`order_id`),
    KEY `ix_order_items_product_id` (`product_id`),
    CONSTRAINT `fk_order_items_order` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`),
    CONSTRAINT `fk_order_items_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单商品表';

-- ============================================
-- 11. invites - 邀请记录表
-- ============================================
CREATE TABLE IF NOT EXISTS `invites` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '邀请记录ID',
    `inviter_id` BIGINT NOT NULL COMMENT '邀请人用户ID',
    `invitee_id` BIGINT NOT NULL COMMENT '被邀请人用户ID',
    `invite_code` VARCHAR(32) NOT NULL COMMENT '邀请码',
    `order_id` BIGINT NOT NULL COMMENT '关联订单ID',
    `coupon_sent` INT NULL DEFAULT 0 COMMENT '是否已发优惠券: 0=否 1=是',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '邀请时间',
    PRIMARY KEY (`id`),
    KEY `ix_invites_inviter_id` (`inviter_id`),
    KEY `ix_invites_invitee_id` (`invitee_id`),
    KEY `ix_invites_invite_code` (`invite_code`),
    KEY `ix_invites_order_id` (`order_id`),
    CONSTRAINT `fk_invites_inviter` FOREIGN KEY (`inviter_id`) REFERENCES `users` (`id`),
    CONSTRAINT `fk_invites_invitee` FOREIGN KEY (`invitee_id`) REFERENCES `users` (`id`),
    CONSTRAINT `fk_invites_order` FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='邀请记录表';

-- ============================================
-- 12. product_extras - 商品扩展表
-- ============================================
CREATE TABLE IF NOT EXISTS `product_extras` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '扩展信息ID',
    `product_id` BIGINT NOT NULL COMMENT '商品ID',
    `harvest_date` DATE NULL COMMENT '采摘日期',
    `variety_info` VARCHAR(256) NULL COMMENT '品种信息',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_product_id` (`product_id`),
    KEY `ix_product_extras_product_id` (`product_id`),
    CONSTRAINT `fk_product_extras_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='商品扩展表';

-- ============================================
-- 13. banner_configs - Banner配置表
-- ============================================
CREATE TABLE IF NOT EXISTS `banner_configs` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT 'Banner配置ID',
    `type` VARCHAR(64) NOT NULL COMMENT '类型: growth_status等',
    `title` VARCHAR(256) NOT NULL COMMENT '标题',
    `content` TEXT NOT NULL COMMENT '内容(支持富文本)',
    `status` INT NOT NULL DEFAULT 0 COMMENT '状态: 1=显示 0=隐藏',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `ix_banner_configs_type` (`type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Banner配置表';

-- ============================================
-- 建表完成
-- ============================================
