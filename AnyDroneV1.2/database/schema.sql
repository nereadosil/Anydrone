-- 1. Tabla de Usuarios
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT NOT NULL,
    user_email_address TEXT UNIQUE NOT NULL,
    user_password TEXT NOT NULL
);

-- 2. Tabla de Drones
CREATE TABLE IF NOT EXISTS drones (
    drone_id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id INTEGER NOT NULL,
    model TEXT NOT NULL,
    manufacturer TEXT NOT NULL,
    camera_quality TEXT NOT NULL,
    max_load REAL NOT NULL,  -- Kg
    flight_time INTEGER NOT NULL,  -- Minuts
    FOREIGN KEY (owner_id) REFERENCES users(id_usuario) ON DELETE CASCADE
);

-- 3. Tabla de Reseñas
CREATE TABLE IF NOT EXISTS reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    drone_id INTEGER NOT NULL,
    review TEXT NOT NULL,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (drone_id) REFERENCES drone(drone_id)
);
