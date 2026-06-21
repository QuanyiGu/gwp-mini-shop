"""Initial migration - 创建所有表

Revision ID: 001
Revises:
Create Date: 2026-05-11 08:40:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 用户表
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('uid', sa.String(length=32), nullable=False),
        sa.Column('openid', sa.String(length=64), nullable=True),
        sa.Column('unionid', sa.String(length=64), nullable=True),
        sa.Column('nickname', sa.String(length=128), nullable=True),
        sa.Column('avatar_url', sa.String(length=512), nullable=True),
        sa.Column('phone', sa.String(length=32), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uid'),
        sa.UniqueConstraint('openid'),
        sa.UniqueConstraint('unionid'),
    )
    op.create_index(op.f('ix_users_uid'), 'users', ['uid'], unique=True)
    op.create_index(op.f('ix_users_openid'), 'users', ['openid'], unique=True)
    op.create_index(op.f('ix_users_unionid'), 'users', ['unionid'], unique=True)

    # 商品分类表
    op.create_table(
        'categories',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('icon', sa.String(length=512), nullable=True),
        sa.Column('sort', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # 商家后台用户表
    op.create_table(
        'admin_users',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('username', sa.String(length=64), nullable=False),
        sa.Column('password_hash', sa.String(length=256), nullable=False),
        sa.Column('nickname', sa.String(length=64), nullable=False),
        sa.Column('role', sa.String(length=32), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
    )
    op.create_index(op.f('ix_admin_users_username'), 'admin_users', ['username'], unique=True)

    # 商品表
    op.create_table(
        'products',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('category_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=256), nullable=False),
        sa.Column('main_image', sa.String(length=512), nullable=False),
        sa.Column('images', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('original_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('stock', sa.Integer(), nullable=False),
        sa.Column('sales', sa.Integer(), nullable=False),
        sa.Column('status', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_products_category_id'), 'products', ['category_id'], unique=False)

    # 管理员操作日志表
    op.create_table(
        'admin_operate_logs',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('admin_id', sa.BigInteger(), nullable=False),
        sa.Column('action', sa.String(length=64), nullable=False),
        sa.Column('target_type', sa.String(length=64), nullable=False),
        sa.Column('target_id', sa.BigInteger(), nullable=False),
        sa.Column('detail', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['admin_id'], ['admin_users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_admin_operate_logs_admin_id'), 'admin_operate_logs', ['admin_id'], unique=False)

    # 收货地址表
    op.create_table(
        'addresses',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('phone', sa.String(length=32), nullable=False),
        sa.Column('province', sa.String(length=64), nullable=False),
        sa.Column('city', sa.String(length=64), nullable=False),
        sa.Column('district', sa.String(length=64), nullable=False),
        sa.Column('detail', sa.String(length=512), nullable=False),
        sa.Column('is_default', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_addresses_user_id'), 'addresses', ['user_id'], unique=False)

    # 优惠券表
    op.create_table(
        'coupons',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('type', sa.Integer(), nullable=False),
        sa.Column('discount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('min_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('status', sa.Integer(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
    )
    op.create_index(op.f('ix_coupons_code'), 'coupons', ['code'], unique=True)
    op.create_index(op.f('ix_coupons_user_id'), 'coupons', ['user_id'], unique=False)

    # 购物车表
    op.create_table(
        'cart_items',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('product_id', sa.BigInteger(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('selected', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_cart_items_user_id'), 'cart_items', ['user_id'], unique=False)
    op.create_index(op.f('ix_cart_items_product_id'), 'cart_items', ['product_id'], unique=False)

    # 订单表
    op.create_table(
        'orders',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('order_no', sa.String(length=64), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('pay_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('address_name', sa.String(length=64), nullable=False),
        sa.Column('address_phone', sa.String(length=32), nullable=False),
        sa.Column('address_detail', sa.String(length=512), nullable=False),
        sa.Column('status', sa.Integer(), nullable=False),
        sa.Column('gift_package', sa.Integer(), nullable=True),
        sa.Column('greeting_card', sa.Text(), nullable=True),
        sa.Column('tracking_node', sa.Text(), nullable=True),
        sa.Column('logistics_company', sa.String(length=64), nullable=True),
        sa.Column('logistics_no', sa.String(length=128), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_no'),
    )
    op.create_index(op.f('ix_orders_order_no'), 'orders', ['order_no'], unique=True)
    op.create_index(op.f('ix_orders_user_id'), 'orders', ['user_id'], unique=False)

    # 订单商品表
    op.create_table(
        'order_items',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('order_id', sa.BigInteger(), nullable=False),
        sa.Column('product_id', sa.BigInteger(), nullable=False),
        sa.Column('product_name', sa.String(length=256), nullable=False),
        sa.Column('product_image', sa.String(length=512), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('total_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_order_items_order_id'), 'order_items', ['order_id'], unique=False)
    op.create_index(op.f('ix_order_items_product_id'), 'order_items', ['product_id'], unique=False)

    # 邀请记录表
    op.create_table(
        'invites',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('inviter_id', sa.BigInteger(), nullable=False),
        sa.Column('invitee_id', sa.BigInteger(), nullable=False),
        sa.Column('invite_code', sa.String(length=32), nullable=False),
        sa.Column('order_id', sa.BigInteger(), nullable=False),
        sa.Column('coupon_sent', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['inviter_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['invitee_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_invites_inviter_id'), 'invites', ['inviter_id'], unique=False)
    op.create_index(op.f('ix_invites_invitee_id'), 'invites', ['invitee_id'], unique=False)
    op.create_index(op.f('ix_invites_invite_code'), 'invites', ['invite_code'], unique=False)
    op.create_index(op.f('ix_invites_order_id'), 'invites', ['order_id'], unique=False)

    # 商品扩展表
    op.create_table(
        'product_extras',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('product_id', sa.BigInteger(), nullable=False),
        sa.Column('harvest_date', sa.Date(), nullable=True),
        sa.Column('variety_info', sa.String(length=256), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('product_id'),
    )
    op.create_index(op.f('ix_product_extras_product_id'), 'product_extras', ['product_id'], unique=True)

    # Banner配置表
    op.create_table(
        'banner_configs',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('type', sa.String(length=64), nullable=False),
        sa.Column('title', sa.String(length=256), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('status', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_banner_configs_type'), 'banner_configs', ['type'], unique=False)


def downgrade() -> None:
    op.drop_table('banner_configs')
    op.drop_table('product_extras')
    op.drop_table('invites')
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('cart_items')
    op.drop_table('coupons')
    op.drop_table('addresses')
    op.drop_table('admin_operate_logs')
    op.drop_table('products')
    op.drop_table('admin_users')
    op.drop_table('categories')
    op.drop_table('users')
