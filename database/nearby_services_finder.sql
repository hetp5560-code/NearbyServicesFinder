CREATE DATABASE IF NOT EXISTS nearby_services_finder;
USE nearby_services_finder;

-- Users Table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fullname VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Search History Table
CREATE TABLE search_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    category VARCHAR(50),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    radius_km INT,
    searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Saved Places Table
CREATE TABLE saved_places (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    place_name VARCHAR(255),
    category VARCHAR(50),
    address TEXT,
    rating DECIMAL(2,1),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Feedback Table
CREATE TABLE feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    message TEXT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE TABLE otp_verification (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    otp_code VARCHAR(255) NOT NULL,
    purpose VARCHAR(30) NOT NULL DEFAULT 'signup',
    expires_at DATETIME NOT NULL,
    attempts INT NOT NULL DEFAULT 0,
    verified TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
ALTER TABLE users
ADD COLUMN is_verified TINYINT(1) NOT NULL DEFAULT 0
AFTER password;