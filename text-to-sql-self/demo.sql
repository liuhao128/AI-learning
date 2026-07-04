-- ============================================
-- 创建数据库
-- ============================================
CREATE DATABASE IF NOT EXISTS demo DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE demo;

-- ============================================
-- 1. 用户表
-- ============================================
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL COMMENT '姓名',
    age INT COMMENT '年龄',
    gender VARCHAR(10) COMMENT '性别',
    city VARCHAR(50) COMMENT '所在城市',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间'
) COMMENT '用户表';

-- ============================================
-- 2. 商品表
-- ============================================
CREATE TABLE products (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '商品名称',
    category VARCHAR(50) COMMENT '商品分类',
    price DECIMAL(10,2) NOT NULL COMMENT '单价',
    stock INT DEFAULT 0 COMMENT '库存数量'
) COMMENT '商品表';

-- ============================================
-- 3. 订单表
-- ============================================
CREATE TABLE orders (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '下单时间',
    status VARCHAR(20) DEFAULT '已完成' COMMENT '订单状态：已完成/已取消/待发货',
    FOREIGN KEY (user_id) REFERENCES users(id)
) COMMENT '订单表';

-- ============================================
-- 4. 订单明细表
-- ============================================
CREATE TABLE order_items (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL COMMENT '订单ID',
    product_id INT NOT NULL COMMENT '商品ID',
    quantity INT NOT NULL COMMENT '购买数量',
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
) COMMENT '订单明细表';

-- ============================================
-- 插入用户数据
-- ============================================
INSERT INTO users (name, age, gender, city) VALUES
('张三', 25, '男', '杭州'),
('李四', 30, '男', '北京'),
('王五', 22, '女', '上海'),
('赵六', 28, '女', '杭州'),
('孙七', 35, '男', '深圳'),
('周八', 19, '女', '广州'),
('吴九', 40, '男', '北京'),
('郑十', 27, '女', '上海');

-- ============================================
-- 插入商品数据
-- ============================================
INSERT INTO products (name, category, price, stock) VALUES
('iPhone 15', '手机', 5999.00, 100),
('MacBook Air', '电脑', 8999.00, 50),
('AirPods Pro', '耳机', 1799.00, 200),
('小米手环', '穿戴设备', 249.00, 500),
('iPad mini', '平板', 3799.00, 80),
('索尼耳机', '耳机', 2499.00, 120),
('机械键盘', '外设', 399.00, 300),
('显示器', '外设', 1599.00, 60);

-- ============================================
-- 插入订单数据
-- ============================================
INSERT INTO orders (user_id, order_date, status) VALUES
(1, '2026-06-01 10:30:00', '已完成'),
(2, '2026-06-03 14:20:00', '已完成'),
(3, '2026-06-05 09:15:00', '已完成'),
(1, '2026-06-10 16:45:00', '待发货'),
(4, '2026-06-12 11:00:00', '已完成'),
(5, '2026-06-15 08:30:00', '已取消'),
(6, '2026-06-18 13:50:00', '已完成'),
(7, '2026-06-20 17:20:00', '已完成'),
(2, '2026-06-22 10:10:00', '已完成'),
(8, '2026-06-25 15:30:00', '待发货');

-- ============================================
-- 插入订单明细数据
-- ============================================
INSERT INTO order_items (order_id, product_id, quantity) VALUES
(1, 1, 1),    -- 张三买了1台 iPhone 15
(1, 3, 1),    -- 张三买了1副 AirPods Pro
(2, 2, 1),    -- 李四买了1台 MacBook Air
(2, 7, 1),    -- 李四买了1个机械键盘
(3, 4, 2),    -- 王五买了2个小米手环
(3, 5, 1),    -- 王五买了1台 iPad mini
(4, 6, 1),    -- 张三买了1副索尼耳机
(5, 1, 1),    -- 赵六买了1台 iPhone 15
(5, 8, 2),    -- 赵六买了2个显示器
(6, 2, 1),    -- 孙七买了1台 MacBook Air（已取消）
(7, 3, 1),    -- 周八买了1副 AirPods Pro
(7, 4, 1),    -- 周八买了1个小米手环
(8, 5, 1),    -- 吴九买了1台 iPad mini
(9, 7, 2),    -- 李四买了2个机械键盘
(10, 1, 1);   -- 郑十买了1台 iPhone 15