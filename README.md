12:42 PM 11/20/2024
## Mô hình chấm công nhân viên sử dụng Vân tay và Khuôn mặt - MCU ESP32 và ESP32CAM
### 1. Sơ đồ phần cứng gồm: 
- MCU ESP32, ESP32Cam - AI Thinker
- Sensor AS608
- LCD 20x04
- Keypad 4x4
- TFT LCD 1.8 inch
- Opto PC817, Resistor, LED,...

### 2. Mạch chính
<p align="center">
  <img src="PCB_Mach_Chinh/mach_chinh_schematic_pbl5.jpg" alt="Schematic Mạch chính" width="300">
  <img src="PCB_Mach_Chinh/mach_chinh_PCB_3D_pbl5.jpg" alt="PCB_3D Mạch chính" width="390">
</p>

### 3. Mạch nguồn
<p align="center">
  <img src="PCB_Mach_Nguon/mach_nguon_schematic_pbl5.jpg" alt="Schematic Mạch nguồn" width="300">
  <img src="PCB_Mach_Nguon/mach_nguon_PCB_3D_pbl5.jpg" alt="PCB_3D Mạch nguồn" width="370">
</p>

### 4. Nguyên lý hoạt động
- Chức năng thêm nhân viên: Thêm vân tay thành công -> ESP32 gửi tín hiệu điều khiển qua PC817 -> ESP32CAM nhận tín hiệu điều khiển và bật khung camera của ESP32CAM để thêm khuôn mặt -> Tắt Camera
- Chức năng chấm công nhân viên: Quét vân tay thành công -> ESP32 gửi tín hiệu điều khiển qua PC817 -> ESP32CAM nhận tín hiệu điều khiển và bật khung camera của ESP32CAM để quét khuôn mặt -> Chấm công thành công -> Gửi thông tin chấm công (tên, trạng thái, thời gian) lên Web server -> Tắt Camera
