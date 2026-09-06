-- =================================================================================
-- SCRIPT DE BASE DE DATOS - SIGEPSI (SPRINT 0)
-- Arquitectura: Multi-Tenant (Esquemas separados)
-- Motor de Base de Datos: PostgreSQL
-- =================================================================================

-- ---------------------------------------------------------------------------------
-- 1. ESQUEMA PÚBLICO (Datos compartidos y enrutamiento)
-- ---------------------------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS public;
SET search_path TO public;

-- Tabla: CENTRO (Equivalente al Tenant)
CREATE TABLE public.centros (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    schema_name VARCHAR(63) NOT NULL UNIQUE, -- Nombre del esquema aislado en BD
    email_contacto VARCHAR(255) NOT NULL,
    telefono VARCHAR(50),
    estado VARCHAR(20) DEFAULT 'ACTIVO',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: DOMINIO (Para enrutamiento del Tenant)
CREATE TABLE public.dominios (
    id SERIAL PRIMARY KEY,
    domain VARCHAR(253) NOT NULL UNIQUE, -- Ej: clinica-esperanza.sigepsi.com
    is_primary BOOLEAN DEFAULT TRUE,
    tenant_id INTEGER NOT NULL,
    CONSTRAINT fk_centro_dominio FOREIGN KEY (tenant_id) 
        REFERENCES public.centros(id) ON DELETE CASCADE
);


-- ---------------------------------------------------------------------------------
-- 2. ESQUEMA DEL TENANT (Plantilla que se replica por cada Centro Psicológico)
-- Nota: 'tenant_schema' representa el schema_name dinámico (ej: schema_clinica1)
-- ---------------------------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS tenant_schema;
SET search_path TO tenant_schema;

-- Tabla: CONFIGURACION
CREATE TABLE tenant_schema.configuracion (
    id SERIAL PRIMARY KEY,
    logo_url VARCHAR(255),
    color_primario VARCHAR(20) DEFAULT '#0056b3',
    color_secundario VARCHAR(20) DEFAULT '#f8f9fa',
    zona_horaria VARCHAR(100) DEFAULT 'America/La_Paz',
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: USUARIO (Aislado al Centro)
CREATE TABLE tenant_schema.usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    estado VARCHAR(20) DEFAULT 'ACTIVO',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: ROL
CREATE TABLE tenant_schema.roles (
    id SERIAL PRIMARY KEY,
    nombre_rol VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: PERMISO
CREATE TABLE tenant_schema.permisos (
    id SERIAL PRIMARY KEY,
    nombre_permiso VARCHAR(100) NOT NULL UNIQUE,
    modulo VARCHAR(50) NOT NULL
);

-- Tabla Intermedia: USUARIO_ROL
CREATE TABLE tenant_schema.usuario_rol (
    usuario_id INTEGER NOT NULL,
    rol_id INTEGER NOT NULL,
    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (usuario_id, rol_id),
    CONSTRAINT fk_ur_usuario FOREIGN KEY (usuario_id) 
        REFERENCES tenant_schema.usuarios(id) ON DELETE CASCADE,
    CONSTRAINT fk_ur_rol FOREIGN KEY (rol_id) 
        REFERENCES tenant_schema.roles(id) ON DELETE CASCADE
);

-- Tabla Intermedia: ROL_PERMISO
CREATE TABLE tenant_schema.rol_permiso (
    rol_id INTEGER NOT NULL,
    permiso_id INTEGER NOT NULL,
    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (rol_id, permiso_id),
    CONSTRAINT fk_rp_rol FOREIGN KEY (rol_id) 
        REFERENCES tenant_schema.roles(id) ON DELETE CASCADE,
    CONSTRAINT fk_rp_permiso FOREIGN KEY (permiso_id) 
        REFERENCES tenant_schema.permisos(id) ON DELETE CASCADE
);

-- =================================================================================
-- FIN DEL SCRIPT SPRINT 0
-- =================================================================================
