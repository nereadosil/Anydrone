-- 1. Tabla de Usuarios (Clientes y Propietarios de Drones)
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    correo TEXT UNIQUE NOT NULL,
    contraseña TEXT NOT NULL,
    tipo_usuario TEXT CHECK(tipo_usuario IN ('propietario', 'cliente')) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabla de Drones
CREATE TABLE IF NOT EXISTS drones (
    id_drone INTEGER PRIMARY KEY AUTOINCREMENT,
    id_propietario INTEGER NOT NULL,
    modelo TEXT NOT NULL,
    fabricante TEXT NOT NULL,
    calidad_camara TEXT NOT NULL,
    capacidad_carga REAL NOT NULL,  -- Kg
    autonomia_vuelo INTEGER NOT NULL,  -- Minutos
    estado TEXT CHECK(estado IN ('disponible', 'ocupado', 'mantenimiento')) NOT NULL DEFAULT 'disponible',
    FOREIGN KEY (id_propietario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

-- 3. Tabla de Servicios
CREATE TABLE IF NOT EXISTS servicios (
    id_servicio INTEGER PRIMARY KEY AUTOINCREMENT,
    id_cliente INTEGER NOT NULL,
    id_drone INTEGER NOT NULL,
    tipo_servicio TEXT CHECK(tipo_servicio IN ('fotografía', 'topografía', 'envío', 'inspección')) NOT NULL,
    ubicacion_origen TEXT NOT NULL,  -- 'latitud,longitud'
    ubicacion_destino TEXT,  -- 'latitud,longitud'
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_servicio DATETIME,
    estado TEXT CHECK(estado IN ('pendiente', 'en progreso', 'completado', 'cancelado')) NOT NULL DEFAULT 'pendiente',
    costo_estimado REAL NOT NULL,
    costo_final REAL,
    FOREIGN KEY (id_cliente) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_drone) REFERENCES drones(id_drone) ON DELETE CASCADE
);

-- 4. Tabla de Precios Dinámicos
CREATE TABLE IF NOT EXISTS precios (
    id_precio INTEGER PRIMARY KEY AUTOINCREMENT,
    id_servicio INTEGER NOT NULL,
    factor_calidad REAL NOT NULL,
    factor_distancia REAL NOT NULL,
    precio_final REAL NOT NULL,
    FOREIGN KEY (id_servicio) REFERENCES servicios(id_servicio) ON DELETE CASCADE
);

-- 5. Tabla de Historial de Vuelos (Remote ID)
CREATE TABLE IF NOT EXISTS vuelos (
    id_vuelo INTEGER PRIMARY KEY AUTOINCREMENT,
    id_drone INTEGER NOT NULL,
    fecha_vuelo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ubicacion_inicial TEXT NOT NULL,  -- 'latitud,longitud'
    ubicacion_final TEXT,  -- 'latitud,longitud'
    altitud_maxima REAL NOT NULL,
    velocidad_promedio REAL NOT NULL,
    estado_vuelo TEXT CHECK(estado_vuelo IN ('en curso', 'completado', 'fallido')) NOT NULL DEFAULT 'en curso',
    FOREIGN KEY (id_drone) REFERENCES drones(id_drone) ON DELETE CASCADE
);

-- 6. Tabla de Reseñas
CREATE TABLE IF NOT EXISTS resenas (
    id_resena INTEGER PRIMARY KEY AUTOINCREMENT,
    id_servicio INTEGER NOT NULL,
    id_revisor INTEGER NOT NULL,
    puntuacion REAL CHECK(puntuacion BETWEEN 0 AND 5) NOT NULL,
    comentario TEXT,
    fecha_resena TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_servicio) REFERENCES servicios(id_servicio) ON DELETE CASCADE,
    FOREIGN KEY (id_revisor) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

-- 7. Tabla de Pagos y Transacciones
CREATE TABLE IF NOT EXISTS pagos (
    id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
    id_servicio INTEGER NOT NULL,
    id_cliente INTEGER NOT NULL,
    monto REAL NOT NULL,
    estado TEXT CHECK(estado IN ('pendiente', 'pagado', 'fallido')) NOT NULL DEFAULT 'pendiente',
    metodo_pago TEXT CHECK(metodo_pago IN ('tarjeta', 'paypal', 'transferencia')) NOT NULL,
    fecha_pago TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_servicio) REFERENCES servicios(id_servicio) ON DELETE CASCADE,
    FOREIGN KEY (id_cliente) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);
