-- This script defines the structure for the 'users' and 'items' tables.
-- It is designed for a MySQL database.

-- Drop tables if they already exist to ensure a clean setup
DROP TABLE IF EXISTS `items`;
DROP TABLE IF EXISTS `users`;

-- Create the 'users' table to store student and admin login information
CREATE TABLE `users` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `username` VARCHAR(80) UNIQUE NOT NULL,
  `password` VARCHAR(120) NOT NULL,
  `role` VARCHAR(20) NOT NULL DEFAULT 'student' COMMENT 'Can be ''student'' or ''admin'''
);

-- Create the 'items' table to store details of lost and found items
CREATE TABLE `items` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `item_type` VARCHAR(10) NOT NULL COMMENT 'Can be ''lost'' or ''found''',
  `description` TEXT NOT NULL,
  `location` VARCHAR(100),
  `image_path` VARCHAR(200),
  
  -- Fields for Student Details --
  `student_name` VARCHAR(100),
  `department` VARCHAR(100),
  `roll_no` VARCHAR(50),
  
  -- Field for tracking status --
  `status` VARCHAR(20) NOT NULL DEFAULT 'not_found' COMMENT 'e.g., not_found, found_by_owner',
  
  `report_date` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE
);