-- 1. 创建商品表
CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '商品ID',
    name VARCHAR(100) NOT NULL COMMENT '商品名称',
    category VARCHAR(50) NOT NULL COMMENT '商品类别'
) COMMENT '商品信息表';

-- 2. 创建订单表
CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '订单ID',
    product_id INT NOT NULL COMMENT '商品ID',
    quantity INT NOT NULL COMMENT '购买数量',
    order_date DATE NOT NULL COMMENT '订单日期',
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
) COMMENT '订单记录表';

-- 插入商品数据
INSERT INTO products (name, category) VALUES
('小米手机', '电子产品'),
('华为手机', '电子产品'),
('苹果手机', '电子产品'),
('联想笔记本', '电子产品'),
('耐克运动鞋', '服装'),
('阿迪达斯运动鞋', '服装'),
('格力空调', '家电'),
('美的冰箱', '家电');

-- 插入订单数据
INSERT INTO orders (product_id, quantity, order_date) VALUES
(1, 2, '2024-01-15'),
(2, 1, '2024-01-16'),
(3, 3, '2024-01-20'),
(1, 1, '2024-02-01'),
(4, 2, '2024-02-05'),
(5, 5, '2024-02-10'),
(3, 2, '2024-02-15'),
(2, 1, '2024-03-01'),
(6, 3, '2024-03-05'),
(7, 1, '2024-03-10'),
(8, 2, '2024-03-12'),
(3, 1, '2024-03-15');