-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS dbcrud;

USE dbcrud;

-- Crear la tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL UNIQUE,
    correo VARCHAR(255) NOT NULL,
    user_passw VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar usuarios de ejemplo (opcional)
-- Las contraseñas están hasheadas, puedes agregar usuarios aquí si quieres