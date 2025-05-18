-- Inicialización de base de datos para Nissan ML Platform

-- Crear extensión para UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Crear base de datos (se hace automáticamente por variables de entorno de PostgreSQL)
-- CREATE DATABASE nissan_ml;

-- Crear esquema principal
CREATE SCHEMA IF NOT EXISTS nissan_ml;

-- Crear usuario para la aplicación (se hace automáticamente por variables de entorno)
-- CREATE USER nissan_app WITH PASSWORD 'nissan_password';
-- GRANT ALL PRIVILEGES ON DATABASE nissan_ml TO nissan_app;
-- GRANT ALL PRIVILEGES ON SCHEMA nissan_ml TO nissan_app;

-- Establece el esquema por defecto
SET search_path TO nissan_ml;

-- Comentarios para la base de datos
COMMENT ON DATABASE nissan_ml IS 'Base de datos principal para la plataforma ML de Nissan';
COMMENT ON SCHEMA nissan_ml IS 'Esquema principal para tablas de la aplicación';