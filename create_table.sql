CREATE DATABASE IF NOT EXISTS tempat_favorit;

USE tempat_favorit;

CREATE TABLE IF NOT EXISTS places (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    photo VARCHAR(100)
);
