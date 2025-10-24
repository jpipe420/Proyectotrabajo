-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS dbcrud;

USE dbcrud;

-- ====================================
-- TABLA DE ROLES
-- ====================================
CREATE TABLE IF NOT EXISTS roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ====================================
-- TABLA DE USUARIOS (Mejorada)
-- ====================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL UNIQUE,
    correo VARCHAR(255) NOT NULL UNIQUE,
    user_passw VARCHAR(255) NOT NULL,
    rol_id INT NOT NULL DEFAULT 3,
    telefono VARCHAR(20),
    avatar_url VARCHAR(500),
    estado ENUM('activo', 'inactivo', 'bloqueado') DEFAULT 'activo',
    email_verificado BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (rol_id) REFERENCES roles(id)
);

-- ====================================
-- TABLA DE CATEGORÍAS
-- ====================================
CREATE TABLE IF NOT EXISTS categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    slug VARCHAR(100) NOT NULL UNIQUE,
    imagen_url VARCHAR(500),
    parent_id INT NULL,
    estado ENUM('activo', 'inactivo') DEFAULT 'activo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categorias(id) ON DELETE SET NULL
);

-- ====================================
-- TABLA DE PRODUCTOS
-- ====================================
CREATE TABLE IF NOT EXISTS productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10, 2) NOT NULL,
    precio_oferta DECIMAL(10, 2) NULL,
    stock INT NOT NULL DEFAULT 0,
    sku VARCHAR(100) UNIQUE,
    categoria_id INT NOT NULL,
    vendedor_id INT NOT NULL,
    imagen_principal VARCHAR(500),
    estado ENUM('activo', 'inactivo', 'agotado') DEFAULT 'activo',
    peso DECIMAL(8, 2) COMMENT 'Peso en kg',
    dimensiones VARCHAR(100) COMMENT 'Alto x Ancho x Largo en cm',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id),
    FOREIGN KEY (vendedor_id) REFERENCES users(id)
);

-- ====================================
-- TABLA DE IMÁGENES DE PRODUCTOS
-- ====================================
CREATE TABLE IF NOT EXISTS producto_imagenes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT NOT NULL,
    imagen_url VARCHAR(500) NOT NULL,
    orden INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE
);

-- ====================================
-- TABLA DE DIRECCIONES
-- ====================================
CREATE TABLE IF NOT EXISTS direcciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    nombre_contacto VARCHAR(255) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    direccion_linea1 VARCHAR(255) NOT NULL,
    direccion_linea2 VARCHAR(255),
    ciudad VARCHAR(100) NOT NULL,
    departamento VARCHAR(100) NOT NULL,
    codigo_postal VARCHAR(20),
    pais VARCHAR(100) DEFAULT 'Colombia',
    es_principal BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ====================================
-- TABLA DE ÓRDENES
-- ====================================
CREATE TABLE IF NOT EXISTS ordenes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT NOT NULL,
    direccion_id INT NOT NULL,
    numero_orden VARCHAR(50) UNIQUE NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    impuestos DECIMAL(10, 2) DEFAULT 0,
    costo_envio DECIMAL(10, 2) DEFAULT 0,
    total DECIMAL(10, 2) NOT NULL,
    estado ENUM('pendiente', 'confirmada', 'en_proceso', 'enviada', 'entregada', 'cancelada') DEFAULT 'pendiente',
    metodo_pago VARCHAR(50),
    estado_pago ENUM('pendiente', 'pagado', 'fallido', 'reembolsado') DEFAULT 'pendiente',
    notas TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (cliente_id) REFERENCES users(id),
    FOREIGN KEY (direccion_id) REFERENCES direcciones(id)
);

-- ====================================
-- TABLA DE DETALLES DE ORDEN
-- ====================================
CREATE TABLE IF NOT EXISTS orden_detalles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    orden_id INT NOT NULL,
    producto_id INT NOT NULL,
    vendedor_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10, 2) NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (orden_id) REFERENCES ordenes(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id),
    FOREIGN KEY (vendedor_id) REFERENCES users(id)
);

-- ====================================
-- TABLA DE CARRITO
-- ====================================
CREATE TABLE IF NOT EXISTS carrito (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_producto (user_id, producto_id)
);

-- ====================================
-- TABLA DE RESEÑAS
-- ====================================
CREATE TABLE IF NOT EXISTS resenas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    producto_id INT NOT NULL,
    user_id INT NOT NULL,
    calificacion INT NOT NULL CHECK (calificacion BETWEEN 1 AND 5),
    comentario TEXT,
    estado ENUM('pendiente', 'aprobada', 'rechazada') DEFAULT 'pendiente',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ====================================
-- TABLA DE FAVORITOS/WISHLIST
-- ====================================
CREATE TABLE IF NOT EXISTS favoritos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    producto_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_producto (user_id, producto_id)
);

-- ====================================
-- INSERTAR ROLES PREDEFINIDOS
-- ====================================
INSERT INTO roles (nombre, descripcion) VALUES
('admin', 'Administrador con acceso total al sistema'),
('vendedor', 'Vendedor que puede gestionar sus productos y ver sus órdenes'),
('cliente', 'Cliente que puede realizar compras')
ON DUPLICATE KEY UPDATE nombre=nombre;

-- ====================================
-- INSERTAR CATEGORÍAS DE EJEMPLO
-- ====================================
INSERT INTO categorias (nombre, descripcion, slug) VALUES
('Electrónica', 'Productos electrónicos y tecnología', 'electronica'),
('Ropa', 'Ropa y accesorios de moda', 'ropa'),
('Hogar', 'Artículos para el hogar', 'hogar'),
('Deportes', 'Equipamiento deportivo', 'deportes'),
('Libros', 'Libros y material de lectura', 'libros')
ON DUPLICATE KEY UPDATE nombre=nombre;

-- ====================================
-- INSERTAR USUARIOS DE EJEMPLO
-- ====================================
-- Contraseña: admin123 (debes hashearla en tu app)
INSERT INTO users (nombre, username, correo, user_passw, rol_id) VALUES
('Administrador', 'admin', 'admin@ecommerce.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GZVBnDAZnkUa', 1),
('Juan Vendedor', 'jvendedor', 'vendedor@ecommerce.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GZVBnDAZnkUa', 2),
('María Cliente', 'mcliente', 'cliente@ecommerce.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GZVBnDAZnkUa', 3)
ON DUPLICATE KEY UPDATE username=username;

-- ====================================
-- INSERTAR PRODUCTOS DE EJEMPLO
-- ====================================
INSERT INTO productos (nombre, descripcion, precio, stock, sku, categoria_id, vendedor_id) VALUES
('Laptop HP 15', 'Laptop HP con 8GB RAM y 256GB SSD', 1200000.00, 10, 'LAP-HP-001', 1, 2),
('Camiseta Deportiva', 'Camiseta para ejercicio de alta calidad', 45000.00, 50, 'CAM-DEP-001', 4, 2),
('Silla Ergonómica', 'Silla de oficina ergonómica', 380000.00, 15, 'SIL-ERG-001', 3, 2),
('Smartphone Samsung', 'Samsung Galaxy A54 128GB', 950000.00, 25, 'TEL-SAM-001', 1, 2),
('Zapatillas Running', 'Zapatillas profesionales para correr', 280000.00, 30, 'ZAP-RUN-001', 4, 2)
ON DUPLICATE KEY UPDATE sku=sku;

-- ====================================
-- CREAR ÍNDICES PARA MEJOR RENDIMIENTO
-- ====================================
CREATE INDEX idx_productos_categoria ON productos(categoria_id);
CREATE INDEX idx_productos_vendedor ON productos(vendedor_id);
CREATE INDEX idx_productos_estado ON productos(estado);
CREATE INDEX idx_ordenes_cliente ON ordenes(cliente_id);
CREATE INDEX idx_ordenes_estado ON ordenes(estado);
CREATE INDEX idx_carrito_user ON carrito(user_id);
CREATE INDEX idx_users_rol ON users(rol_id);
CREATE INDEX idx_users_estado ON users(estado);

-- ====================================
-- VISTAS ÚTILES
-- ====================================

-- Vista de productos con información completa
CREATE OR REPLACE VIEW vista_productos_completa AS
SELECT 
    p.id,
    p.nombre,
    p.descripcion,
    p.precio,
    p.precio_oferta,
    p.stock,
    p.sku,
    p.imagen_principal,
    p.estado,
    c.nombre AS categoria,
    u.nombre AS vendedor,
    u.username AS vendedor_username,
    COALESCE(AVG(r.calificacion), 0) AS calificacion_promedio,
    COUNT(DISTINCT r.id) AS total_resenas,
    p.created_at
FROM productos p
LEFT JOIN categorias c ON p.categoria_id = c.id
LEFT JOIN users u ON p.vendedor_id = u.id
LEFT JOIN resenas r ON p.id = r.producto_id AND r.estado = 'aprobada'
GROUP BY p.id;

-- Vista de órdenes con detalles
CREATE OR REPLACE VIEW vista_ordenes_resumen AS
SELECT 
    o.id,
    o.numero_orden,
    o.total,
    o.estado,
    o.estado_pago,
    u.nombre AS cliente,
    u.correo AS cliente_correo,
    COUNT(od.id) AS total_productos,
    o.created_at AS fecha_orden
FROM ordenes o
LEFT JOIN users u ON o.cliente_id = u.id
LEFT JOIN orden_detalles od ON o.id = od.orden_id
GROUP BY o.id;