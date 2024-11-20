<?php
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "employee_attendance";

// Tạo kết nối
$conn = new mysqli($servername, $username, $password);

// Kiểm tra kết nối
if ($conn->connect_error) {
    die("Kết nối thất bại: " . $conn->connect_error);
}

// Tạo database
$sql = "CREATE DATABASE IF NOT EXISTS $dbname";
if ($conn->query($sql) === TRUE) {
    echo "Database đã được tạo thành công<br>";
} else {
    echo "Lỗi khi tạo database: " . $conn->error;
}

// Chọn database
$conn->select_db($dbname);

// Tạo bảng attendance
$sql = "CREATE TABLE IF NOT EXISTS attendance (
    id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    employee_name VARCHAR(50) NOT NULL,
    status VARCHAR(10) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)";

if ($conn->query($sql) === TRUE) {
    echo "Bảng attendance đã được tạo thành công";
} else {
    echo "Lỗi khi tạo bảng: " . $conn->error;
}

$conn->close();
?>