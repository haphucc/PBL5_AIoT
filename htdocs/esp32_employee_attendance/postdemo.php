<?php
header('Content-Type: application/json');
$servername = "localhost";
$username = "root";
$password = "";
$dbname = "employee_attendance";

// Tạo kết nối
$conn = new mysqli($servername, $username, $password, $dbname);

// Kiểm tra kết nối
if ($conn->connect_error) {
    die(json_encode(array("error" => "Kết nối thất bại: " . $conn->connect_error)));
}

// Xử lý POST request (lưu dữ liệu)
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $employee_name = $_POST["employee_name"];
    $status = $_POST["status"];
    
    $sql = "INSERT INTO attendance (employee_name, status) 
            VALUES ('$employee_name', '$status')";
    
    if ($conn->query($sql) === TRUE) {
        echo "success";
    } else {
        echo "error";
    }
}
// Xử lý GET request (lấy dữ liệu)
else if ($_SERVER["REQUEST_METHOD"] == "GET") {
    $sql = "SELECT employee_name, status, timestamp FROM attendance ORDER BY timestamp DESC LIMIT 10";
    $result = $conn->query($sql);
    
    $data = array();
    if ($result->num_rows > 0) {
        while($row = $result->fetch_assoc()) {
            $data[] = $row;
        }
    }
    
    // Debug: in ra JSON để kiểm tra
    $json_output = json_encode($data);
    if (json_last_error() !== JSON_ERROR_NONE) {
        echo json_encode(array("error" => "JSON encoding error: " . json_last_error_msg()));
    } else {
        echo $json_output;
    }
}

$conn->close();
?>