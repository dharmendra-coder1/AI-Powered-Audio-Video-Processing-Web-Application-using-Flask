CREATE TABLE uploaded_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_type VARCHAR(255),
    file_name VARCHAR(255),
    file_path VARCHAR(255),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
