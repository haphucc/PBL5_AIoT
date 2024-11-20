<?php
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "esp32cam_db";

// Tạo kết nối
$conn = new mysqli($servername, $username, $password);

// Kiểm tra kết nối
if ($conn->connect_error) {
    die("Kết nối thất bại: " . $conn->connect_error);
}

// Tạo database
$sql = "CREATE DATABASE IF NOT EXISTS $dbname";
if ($conn->query($sql) === TRUE) {
    echo "Database đã được tạo thành công<br><br>";
} else {
    echo "Lỗi khi tạo database: " . $conn->error . "<br><br>";
}

// Chọn database
$conn->select_db($dbname);

// Tạo bảng images
$sql = "CREATE TABLE IF NOT EXISTS images (
    id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    image_data LONGBLOB NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)";

if ($conn->query($sql) === TRUE) {
    echo "Bảng images đã được tạo thành công<br><br>";
} else {
    echo "Lỗi khi tạo bảng: " . $conn->error . "<br><br>";
}

// Tạo bảng text_data
$sql = "CREATE TABLE IF NOT EXISTS text_data (
    id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    text_content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)";
if ($conn->query($sql) === TRUE) {
    echo "Bảng text_data đã được tạo thành công<br><br>";
} else {
    echo "Lỗi khi tạo bảng text_data: " . $conn->error . "<br><br>";
}

$conn->close();
?>