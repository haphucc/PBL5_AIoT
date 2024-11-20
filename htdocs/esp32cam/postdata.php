<?php
header('Content-Type: application/json');
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "esp32cam_db";

// Tạo kết nối
$conn = new mysqli($servername, $username, $password, $dbname);

// Kiểm tra kết nối
if ($conn->connect_error) {
    die("Kết nối thất bại: " . $conn->connect_error);
}

// Nhận dữ liệu hình ảnh từ ESP32-CAM
$image_data = file_get_contents('php://input');

if ($image_data) {
    // Chuẩn bị và thực thi câu lệnh SQL
    $stmt = $conn->prepare("INSERT INTO images (image_data) VALUES (?)");
    $stmt->bind_param("s", $image_data);
    
    if ($stmt->execute()) {
        echo json_encode(["status" => "success", "message" => "Đã lưu hình ảnh"]);
    } else {
        echo json_encode(["status" => "error", "message" => "Lỗi khi lưu hình ảnh"]);
    }
    
    $stmt->close();
} else {
    echo json_encode(["status" => "error", "message" => "Không nhận được dữ liệu"]);
}

$conn->close();
?>