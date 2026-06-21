#!/bin/bash
# ============================================
# GWP小店 数据库初始化脚本
# 用法: ./init_db.sh
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_NAME="${DB_NAME:-gwp_shop}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-3306}"
DB_USER="${DB_USER:-root}"
DB_PASSWORD="${DB_PASSWORD:-}"

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  GWP小店 数据库初始化${NC}"
echo -e "${YELLOW}========================================${NC}"

# 检查 MySQL 连接
echo -e "\n${YELLOW}[1/4]${NC} 检查 MySQL 连接..."
if ! command -v mysql &> /dev/null; then
    echo -e "${RED}错误: mysql 命令未找到，请安装 MySQL 客户端${NC}"
    exit 1
fi

# 构建 MySQL 连接命令
MYSQL_CMD="mysql -h${DB_HOST} -P${DB_PORT} -u${DB_USER}"
if [ -n "${DB_PASSWORD}" ]; then
    MYSQL_CMD="${MYSQL_CMD} -p${DB_PASSWORD}"
fi

# 测试连接
if ! ${MYSQL_CMD} -e "SELECT 1" &>/dev/null; then
    echo -e "${RED}错误: 无法连接到 MySQL，请检查连接参数${NC}"
    echo -e "  主机: ${DB_HOST}:${DB_PORT}"
    echo -e "  用户: ${DB_USER}"
    exit 1
fi
echo -e "${GREEN}✓${NC} MySQL 连接正常"

# 创建数据库
echo -e "\n${YELLOW}[2/4]${NC} 创建数据库..."
${MYSQL_CMD} -e "CREATE DATABASE IF NOT EXISTS ${DB_NAME} DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
echo -e "${GREEN}✓${NC} 数据库 ${DB_NAME} 已就绪"

# 执行 schema.sql
echo -e "\n${YELLOW}[3/4]${NC} 执行建表脚本..."
${MYSQL_CMD} ${DB_NAME} < "${SCRIPT_DIR}/schema.sql"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} 建表完成"
else
    echo -e "${RED}错误: 建表失败${NC}"
    exit 1
fi

# 执行 seed.sql
echo -e "\n${YELLOW}[4/4]${NC} 插入初始数据..."
${MYSQL_CMD} ${DB_NAME} < "${SCRIPT_DIR}/seed.sql"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} 初始数据插入完成"
else
    echo -e "${RED}错误: 数据插入失败${NC}"
    exit 1
fi

# 显示统计
echo -e "\n${YELLOW}========================================${NC}"
echo -e "${GREEN}  数据库初始化成功！${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""
echo -e "数据库: ${DB_NAME}"
echo -e "管理员账号: admin"
echo -e "管理员密码: admin123"
echo ""
${MYSQL_CMD} ${DB_NAME} -e "SELECT '管理员账号' as item, username, nickname, role FROM admin_users;
SELECT '商品分类' as item, COUNT(*) as count FROM categories;
SELECT '商品数量' as item, COUNT(*) as count FROM products WHERE status=1;
SELECT 'Banner配置' as item, COUNT(*) as count FROM banner_configs;
SELECT '优惠券' as item, COUNT(*) as count FROM coupons;" 2>/dev/null

echo ""
echo -e "${YELLOW}提示: ${NC}如需重新初始化，请运行 ./reset_db.sh"
