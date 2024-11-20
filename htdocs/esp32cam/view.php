<?php
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

// Lấy hình ảnh mới nhất từ database
$sql = "SELECT image_data, timestamp FROM images ORDER BY timestamp DESC LIMIT 1";
$result = $conn->query($sql);

$latest_image = null;
$timestamp = null;
if ($result->num_rows > 0) {
    $row = $result->fetch_assoc();
    $latest_image = base64_encode($row['image_data']);
    $timestamp = $row['timestamp'];
}

$conn->close();
?>

<!DOCTYPE html>
<html>
<head>
    <title>ESP32-CAM Stream</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f0f0f0;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .stream-container {
            width: 100%;
            text-align: center;
            margin-top: 20px;
        }
        #stream-image {
            max-width: 640px;
            width: 100%;
            height: auto;
            border: 1px solid #ddd;
        }
        .timestamp {
            text-align: center;
            color: #666;
            margin-top: 10px;
        }
        h1 {
            text-align: center;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>ESP32-CAM Stream</h1>
        <div class="stream-container">
            <?php if ($latest_image): ?>
                <img id="stream-image" src="data:image/jpeg;base64,<?php echo $latest_image; ?>" alt="ESP32-CAM Stream">
                <p class="timestamp">Cập nhật lúc: <?php echo $timestamp; ?></p>
            <?php else: ?>
                <p>Chưa có hình ảnh nào được ghi nhận</p>
            <?php endif; ?>
        </div>
    </div>

    <script>
        // Tự động làm mới trang sau mỗi 1 giây
        setTimeout(function() {
            location.reload();
        }, 1000);
    </script>
</body>
</html>