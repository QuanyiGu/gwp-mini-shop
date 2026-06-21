-- ============================================
-- GWP小店 数据库初始化数据
-- MySQL 8.0+ 兼容
-- ============================================

USE gwp_shop;

-- ============================================
-- 1. 管理员账号
-- 注意: bcrypt哈希密码为 admin123
-- 哈希值: $2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4z9W5dL4dH5H5O3W
-- ============================================
INSERT INTO `admin_users` (`username`, `password_hash`, `nickname`, `role`, `created_at`) VALUES
('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4z9W5dL4dH5H5O3W', '管理员', 'super_admin', NOW());

-- ============================================
-- 2. 商品分类
-- ============================================
INSERT INTO `categories` (`name`, `icon`, `sort`) VALUES
('水果', 'https://img.yzcdn.cn/vant/cat.png', 1),
('蔬菜', 'https://img.yzcdn.cn/vant/cat.png', 2),
('粮油', 'https://img.yzcdn.cn/vant/cat.png', 3),
('禽蛋', 'https://img.yzcdn.cn/vant/cat.png', 4),
('肉类', 'https://img.yzcdn.cn/vant/cat.png', 5);

-- ============================================
-- 3. 商品数据
-- ============================================
INSERT INTO `products` (`category_id`, `name`, `main_image`, `images`, `description`, `price`, `original_price`, `stock`, `sales`, `status`, `created_at`, `updated_at`) VALUES
-- 水果类 (category_id=1)
(1, '红富士苹果 5斤装', 'https://img.yzcdn.cn/vant/apple-1.jpg', '["https://img.yzcdn.cn/vant/apple-1.jpg","https://img.yzcdn.cn/vant/apple-2.jpg"]', '自家果园产红富士苹果，香甜多汁，脆爽可口', 39.90, 49.90, 100, 52, 1, NOW(), NOW()),
(1, '水晶红富士 4斤装', 'https://img.yzcdn.cn/vant/apple-2.jpg', '["https://img.yzcdn.cn/vant/apple-2.jpg"]', '透明感水晶红富士，甜度更高，口感更脆', 45.80, 58.00, 80, 35, 1, NOW(), NOW()),
(1, '阳光玫瑰葡萄 2斤装', 'https://img.yzcdn.cn/vant/grape-1.jpg', '["https://img.yzcdn.cn/vant/grape-1.jpg"]', '阳光玫瑰，香甜可口，带有淡淡玫瑰香', 68.00, 88.00, 50, 20, 1, NOW(), NOW()),
(1, '香水柠檬 6个装', 'https://img.yzcdn.cn/vant/lemon-1.jpg', '["https://img.yzcdn.cn/vant/lemon-1.jpg"]', '海南香水柠檬，皮薄多汁，清香四溢', 19.90, 25.00, 120, 45, 1, NOW(), NOW()),
(1, '新疆库尔勒香梨 4斤装', 'https://img.yzcdn.cn/vant/pear-1.jpg', '["https://img.yzcdn.cn/vant/pear-1.jpg"]', '正宗新疆库尔勒香梨，皮薄核小，甘甜如蜜', 36.00, 45.00, 60, 28, 1, NOW(), NOW()),

-- 蔬菜类 (category_id=2)
(2, '贝贝南瓜 5斤装', 'https://img.yzcdn.cn/vant/pumpkin-1.jpg', '["https://img.yzcdn.cn/vant/pumpkin-1.jpg"]', '正宗贝贝南瓜，粉糯香甜，辅食首选', 24.90, 32.00, 90, 40, 1, NOW(), NOW()),
(2, '普罗旺斯番茄 3斤装', 'https://img.yzcdn.cn/vant/tomato-1.jpg', '["https://img.yzcdn.cn/vant/tomato-1.jpg"]', '普罗旺斯番茄，自然成熟，沙瓤多汁', 28.00, 36.00, 70, 30, 1, NOW(), NOW()),

-- 禽蛋类 (category_id=4)
(4, '土鸡蛋 30枚装', 'https://img.yzcdn.cn/vant/egg-1.jpg', '["https://img.yzcdn.cn/vant/egg-1.jpg"]', '农家散养土鸡所产，蛋黄橙红，蛋香浓郁', 42.00, 52.00, 80, 38, 1, NOW(), NOW()),
(4, '绿壳鸡蛋 20枚装', 'https://img.yzcdn.cn/vant/egg-2.jpg', '["https://img.yzcdn.cn/vant/egg-2.jpg"]', '特色绿壳鸡蛋，营养价值更高', 48.00, 60.00, 50, 22, 1, NOW(), NOW()),

-- 肉类 (category_id=5)
(5, '五花肉 500g', 'https://img.yzcdn.cn/vant/meat-1.jpg', '["https://img.yzcdn.cn/vant/meat-1.jpg"]', '农家土猪肉，五花分明，肥瘦相间', 35.00, 42.00, 40, 25, 1, NOW(), NOW()),

-- 下架商品
(1, '测试下架商品', 'https://img.yzcdn.cn/vant/apple-1.jpg', '[]', '这是一个测试下架商品', 1.00, 1.00, 0, 0, 0, NOW(), NOW());

-- ============================================
-- 4. 商品扩展信息
-- ============================================
INSERT INTO `product_extras` (`product_id`, `harvest_date`, `variety_info`, `created_at`, `updated_at`) VALUES
(1, '2026-04-15', '红富士品种', NOW(), NOW()),
(2, '2026-04-20', '水晶红富士品种', NOW(), NOW()),
(3, '2026-05-01', '阳光玫瑰品种', NOW(), NOW()),
(4, '2026-04-25', '香水柠檬品种', NOW(), NOW()),
(5, '2026-03-20', '库尔勒香梨品种', NOW(), NOW()),
(6, '2026-04-10', '贝贝南瓜品种', NOW(), NOW()),
(7, '2026-05-05', '普罗旺斯番茄品种', NOW(), NOW()),
(8, '2026-04-28', '农家散养土鸡', NOW(), NOW()),
(9, '2026-04-28', '绿壳蛋鸡品种', NOW(), NOW()),
(10, '2026-05-08', '农家土猪', NOW(), NOW()),
(11, '2026-01-01', '测试品种', NOW(), NOW());

-- ============================================
-- 5. Banner配置
-- ============================================
INSERT INTO `banner_configs` (`type`, `title`, `content`, `status`, `created_at`, `updated_at`) VALUES
('growth_status', '🌱 阳光玫瑰葡萄生长日志', '<p>我们的阳光玫瑰葡萄正在茁壮成长中~</p><p>预计5月下旬上市，敬请期待！</p><p><img src="https://img.yzcdn.cn/vant/grape-growing.jpg" /></p>', 1, NOW(), NOW()),
('growth_status', '🍎 红富士苹果已成熟', '<p>2026年新果已采摘入库！</p><p>香甜多汁，错过等一年~</p>', 1, NOW(), NOW()),
('growth_status', '🥚 土鸡蛋新鲜到货', '<p>今日农家土鸡蛋已送达</p><p>数量有限，先到先得</p>', 1, NOW(), NOW());

-- ============================================
-- 6. 优惠券模板（未领取状态，user_id=0）
-- ============================================
INSERT INTO `coupons` (`code`, `user_id`, `type`, `discount`, `min_amount`, `status`, `expires_at`, `created_at`) VALUES
('WELCOME10', 0, 1, 10.00, 50.00, 0, DATE_ADD(NOW(), INTERVAL 30 DAY), NOW()),
('WELCOME20', 0, 1, 20.00, 100.00, 0, DATE_ADD(NOW(), INTERVAL 30 DAY), NOW()),
('SUMMER30', 0, 1, 30.00, 150.00, 0, DATE_ADD(NOW(), INTERVAL 7 DAY), NOW());

-- ============================================
-- 初始化完成
-- ============================================
