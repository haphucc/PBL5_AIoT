<!DOCTYPE html>
<html>
<head>
	<meta http-equiv="refresh" content="2">
    <title>Bảng chấm công nhân viên</title>
    <meta charset="UTF-8">
    <style>
        table {
            border-collapse: collapse;
            width: 100%;
            margin-top: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #4CAF50;
            color: white;
        }
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        .debug {
            background: #f8f9fa;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
        }
        .empty-row td {
            text-align: center;
            color: #999;
            padding: 20px 8px;
        }
    </style>
</head>
<body>
    <h1 style="text-align: center;">Bảng chấm công nhân viên</h1>
    <div class="debug">
    <?php
    $servername = "localhost";
    $username = "root";
    $password = "";
    $dbname = "employee_attendance";

    

    // Tạo kết nối
    $conn = new mysqli($servername, $username, $password, $dbname);

    // Kiểm tra kết nối
    if ($conn->connect_error) {
        echo "Lỗi kết nối database: " . $conn->connect_error;
        die();
    } else {
        echo "<i>Kết nối database: $dbname thành công<br></i>";
    }

    // Lấy dữ liệu từ database
    //$sql = "SELECT * FROM attendance ORDER BY timestamp DESC";
	$sql = "SELECT * FROM (SELECT * FROM attendance ORDER BY id DESC LIMIT 10) AS latest_logs ORDER BY id ASC";

    $result = $conn->query($sql);

    ?>
    </div>

    <!-- Luôn hiển thị bảng, bất kể có dữ liệu hay không -->
    <table>
        <tr>
            <th>ID</th>
            <th>Tên nhân viên</th>
            <th>Trạng thái</th>
            <th>Thời gian</th>
        </tr>
        <?php
        if ($result && $result->num_rows > 0) {
            while($row = $result->fetch_assoc()) {
                echo "<tr>
                        <td>" . $row["id"] . "</td>
                        <td>" . $row["employee_name"] . "</td>
                        <td>" . $row["status"] . "</td>
                        <td>" . $row["timestamp"] . "</td>
                      </tr>";
            }
        } else {
            // Hiển thị 5 hàng trống khi không có dữ liệu
            for ($i = 0; $i < 5; $i++) {
                echo "<tr class='empty-row'>
                        <td>-</td>
                        <td>-</td>
                        <td>-</td>
                        <td>-</td>
                      </tr>";
            }
        }
        ?>
    </table>

    <?php
    $conn->close();
    ?>
	<script>
		setTimeout(function() {
			window.scrollTo(0, document.body.scrollHeight);
		}, 50);
	</script>
	
</body>
</html>