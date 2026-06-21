#!/bin/bash
# ============================================
# GWP小店 数据库重置脚本
# 用法: ./reset_db.sh
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

echo -e "${RED}========================================${NC}"
echo -e "${RED}  警告: 数据库重置操作${NC}"
echo -e "${RED}========================================${NC}"
echo -e "${YELLOW}这将删除 ${DB_NAME} 数据库中的所有数据！${NC}"
echo -e "${YELLOW}所有表将被重新创建并插入初始数据${NC}"
echo ""
read -p "确定要继续吗？(yes/no): " -r
if [[ ! $REPLY =~ ^yes$ ]]; then
    echo -e "${GREEN}已取消操作${NC}"
    exit 0
fi

# 构建 MySQL 连接命令
MYSQL_CMD="mysql -h${DB_HOST} -P${DB_PORT} -u${DB_USER}"
if [ -n "${DB_PASSWORD}" ]; then
    MYSQL_CMD="${MYSQL_CMD} -p${DB_PASSWORD}"
fi

echo -e "\n${YELLOW}[1/3]${NC} 删除旧数据库..."
${MYSQL_CMD} -e "DROP DATABASE IF EXISTS ${DB_NAME};"
echo -e "${GREEN}✓${NC} 旧数据库已删除"

echo -e "\n${YELLOW}[2/3]${NC} 重新创建数据库和表..."
${MYSQL_CMD} < "${SCRIPT_DIR}/schema.sql"
echo -e "${GREEN}✓${NC} 数据库重建完成"

echo -e "\n${YELLOW}[3/3]${NC} 插入初始数据..."
${MYSQL_CMD} < "${SCRIPT_DIR}/seed.sql"
echo -e "${GREEN}✓${NC} 初始数据插入完成"

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  数据库重置成功！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "数据库: ${DB_NAME}"
echo -e "管理员账号: admin"
echo -e "管理员密码: admin123"
