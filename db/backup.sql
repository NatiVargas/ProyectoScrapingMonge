CREATE TABLE productos (
    id SERIAL PRIMARY KEY,
    titulo TEXT,
    precio TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE archivos (
    id SERIAL PRIMARY KEY,
    archivo TEXT,
    hash TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);