-- ============================================================================
-- PLATAFORMA SIGEPSI - SISTEMA DE GESTIÓN DE CENTROS DE SALUD MENTAL
-- MODELO DE DATOS FÍSICO DDL - POSTGRESQL 16 (ARQUITECTURA MULTI-TENANT)
-- MODELO ACUMULADO E ITERATIVO: SPRINT 0 + SPRINT 1
-- Total: 17 Tablas Relacionales (3 Globales 'public' + 14 en Esquema 'tenant')
-- ============================================================================

-- 0. EXTENSIONES DEL SISTEMA
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================================
-- 1. ESQUEMA GLOBAL: public (CONSOLIDADO SPRINT 0)
-- Gestión de Centros Suscritos (Tenants), Subdominios y SuperAdministradores
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.tenants_tenant (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    schema_name VARCHAR(63) NOT NULL UNIQUE,
    plan VARCHAR(20) NOT NULL DEFAULT 'PROFESIONAL' CHECK (plan IN ('BASICO', 'PROFESIONAL', 'ENTERPRISE')),
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE public.tenants_tenant IS 'Registro central de centros psicológicos suscritos a la plataforma SaaS.';
COMMENT ON COLUMN public.tenants_tenant.schema_name IS 'Nombre del esquema de PostgreSQL asignado exclusivamente a este centro.';

CREATE TABLE IF NOT EXISTS public.tenants_dominio (
    id SERIAL PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES public.tenants_tenant(id) ON DELETE CASCADE,
    dominio VARCHAR(253) NOT NULL UNIQUE,
    es_primario BOOLEAN NOT NULL DEFAULT TRUE
);

COMMENT ON TABLE public.tenants_dominio IS 'Enrutamiento de subdominios o dominios personalizados vinculados a cada centro.';

CREATE TABLE IF NOT EXISTS public.accounts_superadmin (
    id SERIAL PRIMARY KEY,
    email VARCHAR(254) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    apellido VARCHAR(150) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE public.accounts_superadmin IS 'Cuentas con privilegios globales de superadministrador sobre toda la plataforma.';


-- ============================================================================
-- 2. ESQUEMA AISLADO POR TENANT (EJEMPLO: tenant_centro_san_martin)
-- Cada centro psicológico contiene sus propias tablas de configuración,
-- usuarios, psicólogos, pacientes, citas y teleconsultas en su esquema.
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS tenant_centro_san_martin;
SET search_path TO tenant_centro_san_martin, public;

-- ----------------------------------------------------------------------------
-- 2.1 TABLAS BASE INSTITUCIONALES Y SEGURIDAD RBAC (CONSOLIDADO SPRINT 0)
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS core_centro (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(200) NOT NULL,
    direccion VARCHAR(255),
    telefono VARCHAR(30),
    email VARCHAR(254),
    logo VARCHAR(255),
    horarios_atencion JSONB DEFAULT '{"lunes_a_viernes": "08:00 - 20:00", "sabados": "08:00 - 13:00"}'::jsonb,
    configuracion JSONB DEFAULT '{"duracion_cita_defecto": 50, "cancelacion_anticipacion_horas": 24, "moneda": "BOB"}'::jsonb,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE core_centro IS 'Configuración institucional y operativa del centro psicológico.';

CREATE TABLE IF NOT EXISTS accounts_rol (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    descripcion TEXT
);

COMMENT ON TABLE accounts_rol IS 'Catálogo de roles institucionales bajo control de acceso RBAC.';

CREATE TABLE IF NOT EXISTS accounts_permiso (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    codigo VARCHAR(100) NOT NULL UNIQUE,
    modulo VARCHAR(50) NOT NULL,
    descripcion TEXT
);

COMMENT ON TABLE accounts_permiso IS 'Permisos atómicos del sistema por módulo funcional.';

CREATE TABLE IF NOT EXISTS accounts_rol_permiso (
    id SERIAL PRIMARY KEY,
    rol_id INTEGER NOT NULL REFERENCES accounts_rol(id) ON DELETE CASCADE,
    permiso_id INTEGER NOT NULL REFERENCES accounts_permiso(id) ON DELETE CASCADE,
    CONSTRAINT uq_rol_permiso UNIQUE (rol_id, permiso_id)
);

COMMENT ON TABLE accounts_rol_permiso IS 'Matriz de asignación de permisos a roles.';

CREATE TABLE IF NOT EXISTS accounts_usuario (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(254) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    apellido VARCHAR(150) NOT NULL,
    telefono VARCHAR(30),
    rol_id INTEGER NOT NULL REFERENCES accounts_rol(id) ON DELETE RESTRICT,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ultimo_login TIMESTAMP WITH TIME ZONE
);

COMMENT ON TABLE accounts_usuario IS 'Cuentas de usuario pertenecientes al centro (Admin, Psicólogo, Recepcionista, Paciente).';

CREATE TABLE IF NOT EXISTS accounts_token_recuperacion (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID NOT NULL REFERENCES accounts_usuario(id) ON DELETE CASCADE,
    token VARCHAR(100) NOT NULL UNIQUE,
    fecha_expiracion TIMESTAMP WITH TIME ZONE NOT NULL,
    usado BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE accounts_token_recuperacion IS 'Tokens unívocos y temporales para restablecimiento seguro de contraseñas.';


-- ----------------------------------------------------------------------------
-- 2.2 MÓDULO CLÍNICO, AGENDA Y TELECONSULTA (INCREMENTO SPRINT 1)
-- ----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS clinica_especialidad (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT
);

COMMENT ON TABLE clinica_especialidad IS 'Catálogo de especialidades clínicas de psicología en el centro.';

CREATE TABLE IF NOT EXISTS clinica_psicologo (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID NOT NULL UNIQUE REFERENCES accounts_usuario(id) ON DELETE CASCADE,
    numero_colegiado VARCHAR(50) NOT NULL UNIQUE,
    biografia TEXT,
    modalidad VARCHAR(20) NOT NULL DEFAULT 'MIXTA' CHECK (modalidad IN ('PRESENCIAL', 'VIRTUAL', 'MIXTA')),
    tarifa_base DECIMAL(10,2) NOT NULL DEFAULT 150.00 CHECK (tarifa_base >= 0),
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_ingreso DATE NOT NULL DEFAULT CURRENT_DATE
);

COMMENT ON TABLE clinica_psicologo IS 'Perfil profesional y arancelario de psicólogos vinculado a su cuenta de usuario.';

CREATE TABLE IF NOT EXISTS clinica_psicologo_especialidad (
    id SERIAL PRIMARY KEY,
    psicologo_id UUID NOT NULL REFERENCES clinica_psicologo(id) ON DELETE CASCADE,
    especialidad_id INTEGER NOT NULL REFERENCES clinica_especialidad(id) ON DELETE CASCADE,
    CONSTRAINT uq_psicologo_especialidad UNIQUE (psicologo_id, especialidad_id)
);

COMMENT ON TABLE clinica_psicologo_especialidad IS 'Relación muchos a muchos entre terapeutas y sus especialidades acreditadas.';

CREATE TABLE IF NOT EXISTS clinica_disponibilidad (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    psicologo_id UUID NOT NULL REFERENCES clinica_psicologo(id) ON DELETE CASCADE,
    dia_semana SMALLINT NOT NULL CHECK (dia_semana BETWEEN 0 AND 6), -- 0=Domingo, 1=Lunes, ..., 6=Sábado
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    duracion_bloque_min SMALLINT NOT NULL DEFAULT 50 CHECK (duracion_bloque_min > 0),
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT chk_rango_horario CHECK (hora_fin > hora_inicio)
);

COMMENT ON TABLE clinica_disponibilidad IS 'Franjas horarias semanales de atención configuradas por cada psicólogo.';

CREATE TABLE IF NOT EXISTS clinica_paciente (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID NOT NULL UNIQUE REFERENCES accounts_usuario(id) ON DELETE CASCADE,
    codigo_expediente VARCHAR(30) NOT NULL UNIQUE,
    ci VARCHAR(20) NOT NULL UNIQUE,
    fecha_nacimiento DATE NOT NULL,
    genero VARCHAR(1) NOT NULL CHECK (genero IN ('M', 'F', 'O')),
    contacto_emergencia_nombre VARCHAR(120),
    contacto_emergencia_telf VARCHAR(25),
    tutor_legal_nombre VARCHAR(120),
    tutor_legal_ci VARCHAR(20),
    fecha_registro DATE NOT NULL DEFAULT CURRENT_DATE
);

COMMENT ON TABLE clinica_paciente IS 'Expediente sociodemográfico del paciente registrado en la clínica.';

CREATE TABLE IF NOT EXISTS agenda_cita (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paciente_id UUID NOT NULL REFERENCES clinica_paciente(id) ON DELETE RESTRICT,
    psicologo_id UUID NOT NULL REFERENCES clinica_psicologo(id) ON DELETE RESTRICT,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    modalidad VARCHAR(20) NOT NULL DEFAULT 'PRESENCIAL' CHECK (modalidad IN ('PRESENCIAL', 'VIRTUAL')),
    estado VARCHAR(25) NOT NULL DEFAULT 'PROGRAMADA' CHECK (estado IN ('PROGRAMADA', 'CONFIRMADA', 'REALIZADA', 'CANCELADA', 'INASISTENCIA')),
    motivo_consulta TEXT,
    costo DECIMAL(10,2) NOT NULL DEFAULT 150.00 CHECK (costo >= 0),
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_cita_horario CHECK (hora_fin > hora_inicio)
);

COMMENT ON TABLE agenda_cita IS 'Sesión psicológica concertada entre paciente y terapeuta.';

CREATE TABLE IF NOT EXISTS agenda_teleconsulta (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cita_id UUID NOT NULL UNIQUE REFERENCES agenda_cita(id) ON DELETE CASCADE,
    sala_id VARCHAR(150) NOT NULL UNIQUE,
    jwt_room_token TEXT,
    hora_inicio_real TIMESTAMP WITH TIME ZONE,
    hora_fin_real TIMESTAMP WITH TIME ZONE,
    duracion_segundos INTEGER DEFAULT 0 CHECK (duracion_segundos >= 0)
);

COMMENT ON TABLE agenda_teleconsulta IS 'Parámetros técnicos de sala Jitsi Meet y registro de duración real de videollamada.';

CREATE TABLE IF NOT EXISTS agenda_alerta (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paciente_id UUID NOT NULL REFERENCES clinica_paciente(id) ON DELETE CASCADE,
    tipo VARCHAR(50) NOT NULL CHECK (tipo IN ('INASISTENCIA_REITERADA', 'RIESGO_DESERCION', 'URGENCIA_CLINICA')),
    severidad VARCHAR(20) NOT NULL DEFAULT 'MEDIA' CHECK (severidad IN ('BAJA', 'MEDIA', 'ALTA', 'CRITICA')),
    descripcion TEXT NOT NULL,
    resuelta BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_resolucion TIMESTAMP WITH TIME ZONE
);

COMMENT ON TABLE agenda_alerta IS 'Alertas clínicas automáticas por ausentismo reiterado o riesgo de deserción.';


-- ============================================================================
-- 3. ÍNDICES DE RENDIMIENTO Y OPTIMIZACIÓN DE CONSULTAS
-- ============================================================================

-- Índices en Esquema Public
CREATE INDEX IF NOT EXISTS idx_tenants_slug ON public.tenants_tenant(slug);
CREATE INDEX IF NOT EXISTS idx_tenants_schema ON public.tenants_tenant(schema_name);
CREATE INDEX IF NOT EXISTS idx_tenants_dominio_tenant ON public.tenants_dominio(tenant_id);

-- Índices en Esquema Tenant
CREATE INDEX IF NOT EXISTS idx_usuarios_rol ON accounts_usuario(rol_id);
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON accounts_usuario(email);
CREATE INDEX IF NOT EXISTS idx_psicologo_usuario ON clinica_psicologo(usuario_id);
CREATE INDEX IF NOT EXISTS idx_disponibilidad_psico_dia ON clinica_disponibilidad(psicologo_id, dia_semana) WHERE activo = TRUE;
CREATE INDEX IF NOT EXISTS idx_paciente_ci ON clinica_paciente(ci);
CREATE INDEX IF NOT EXISTS idx_paciente_expediente ON clinica_paciente(codigo_expediente);
CREATE INDEX IF NOT EXISTS idx_citas_psicologo_fecha ON agenda_cita(psicologo_id, fecha, hora_inicio);
CREATE INDEX IF NOT EXISTS idx_citas_paciente_fecha ON agenda_cita(paciente_id, fecha);
CREATE INDEX IF NOT EXISTS idx_citas_estado ON agenda_cita(estado);
CREATE INDEX IF NOT EXISTS idx_teleconsulta_sala ON agenda_teleconsulta(sala_id);
CREATE INDEX IF NOT EXISTS idx_alertas_paciente_resuelta ON agenda_alerta(paciente_id, resuelta);


-- ============================================================================
-- 4. POBLACIÓN DE DATOS SEMILLA (SEED DATA DEMOSTRATIVO)
-- ============================================================================

-- A. Inserción en Esquema Public
INSERT INTO public.tenants_tenant (id, nombre, slug, schema_name, plan, activo)
VALUES 
    ('11111111-1111-1111-1111-111111111111', 'Centro Psicológico San Martín', 'sanmartin', 'tenant_centro_san_martin', 'ENTERPRISE', TRUE)
ON CONFLICT (slug) DO NOTHING;

INSERT INTO public.tenants_dominio (tenant_id, dominio, es_primario)
VALUES 
    ('11111111-1111-1111-1111-111111111111', 'sanmartin.sigepsi.com', TRUE)
ON CONFLICT (dominio) DO NOTHING;

INSERT INTO public.accounts_superadmin (email, password_hash, nombre, apellido, activo)
VALUES 
    ('superadmin@sigepsi.com', crypt('SuperSecret2026!', gen_salt('bf')), 'Super', 'Administrador', TRUE)
ON CONFLICT (email) DO NOTHING;

-- B. Inserción en Esquema Tenant (Roles y Permisos Base)
INSERT INTO accounts_rol (id, nombre, descripcion)
VALUES 
    (1, 'Administrador del Centro', 'Control total sobre configuración institucional, usuarios y reportes.'),
    (2, 'Psicólogo / Terapeuta', 'Gestión de agenda propia, disponibilidad, sesiones y expedientes clínicos.'),
    (3, 'Recepcionista', 'Programación y confirmación de citas, derivación de pacientes y cobros.'),
    (4, 'Paciente', 'Acceso a reservas de citas, teleconsulta virtual y visualización de perfil.')
ON CONFLICT (id) DO NOTHING;

INSERT INTO accounts_permiso (id, nombre, codigo, modulo, descripcion)
VALUES 
    (1, 'Ver Usuarios', 'accounts.view_usuario', 'accounts', 'Permite listar los usuarios del centro'),
    (2, 'Crear Usuarios', 'accounts.add_usuario', 'accounts', 'Permite crear nuevos usuarios en el centro'),
    (3, 'Ver Psicólogos', 'clinica.view_psicologo', 'clinica', 'Permite listar psicólogos y especialidades'),
    (4, 'Editar Disponibilidad', 'clinica.change_disponibilidad', 'clinica', 'Permite actualizar franjas horarias'),
    (5, 'Ver Pacientes', 'clinica.view_paciente', 'clinica', 'Permite consultar expedientes de pacientes'),
    (6, 'Crear Pacientes', 'clinica.add_paciente', 'clinica', 'Permite registrar nuevos pacientes'),
    (7, 'Agendar Cita', 'agenda.add_cita', 'agenda', 'Permite reservar turnos en el calendario'),
    (8, 'Acceder Teleconsulta', 'agenda.access_teleconsulta', 'agenda', 'Permite unirse a la sala de videoconferencia Jitsi Meet')
ON CONFLICT (id) DO NOTHING;

-- C. Especialidades Clínicas Base
INSERT INTO clinica_especialidad (id, nombre, descripcion)
VALUES 
    (1, 'Terapia Cognitivo-Conductual (TCC)', 'Enfoque orientado a la reestructuración de pensamientos y patrones de conducta disfuncionales.'),
    (2, 'Psicología Clínica y de la Salud', 'Evaluación, diagnóstico y tratamiento de trastornos emocionales y del estado de ánimo.'),
    (3, 'Terapia Familiar y de Pareja', 'Intervención sistémica orientada a mejorar la comunicación y resolver conflictos vinculares.'),
    (4, 'Neuropsicología y Rehabilitación', 'Evaluación y estimulación de funciones cognitivas en infantes, adultos y adultos mayores.')
ON CONFLICT (id) DO NOTHING;
