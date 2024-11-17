#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>

// Cấu hình WiFi
const char* ssid = "LUN 1";
const char* password = "Xomtro179";

// URL của server
const char* serverUrl = "http://192.168.1.13:82/esp32cam/postdata.php";
// URL mới cho việc gửi text
const char* textServerUrl = "http://192.168.1.13:82/esp32cam/posttext.php"; 

// Biến để theo dõi thời gian
unsigned long previousMillis = 0;
bool previousControlValue = 0;

#define input_control 4

void setup() {
  Serial.begin(115200);
  pinMode(input_control, INPUT_PULLUP);
  Serial.println();
  
  // Cấu hình camera
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = 5;
  config.pin_d1 = 18;
  config.pin_d2 = 19;
  config.pin_d3 = 21;
  config.pin_d4 = 36;
  config.pin_d5 = 39;
  config.pin_d6 = 34;
  config.pin_d7 = 35;
  config.pin_xclk = 0;
  config.pin_pclk = 22;
  config.pin_vsync = 25;
  config.pin_href = 23;
  config.pin_sscb_sda = 26;
  config.pin_sscb_scl = 27;
  config.pin_pwdn = 32;
  config.pin_reset = -1;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  // Cấu hình chất lượng hình ảnh
  if(psramFound()){
    config.frame_size = FRAMESIZE_VGA; // 640x480
    config.jpeg_quality = 10;  //0-63 (số càng thấp chất lượng càng cao)
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }

  // Khởi tạo camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Khởi tạo Camera thất bại với error 0x%x", err);
    return;
  }

  // Kết nối WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi đã kết nối");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
}

// Hàm gửi chuỗi text
void sendText() {
  HTTPClient http;
  http.begin(textServerUrl);
  http.addHeader("Content-Type", "text/plain");
  
  int httpResponseCode = http.POST("ADD_NV");
  
  if(httpResponseCode > 0) {
    String response = http.getString();
    Serial.println("Text HTTP Response code: " + String(httpResponseCode));
    Serial.println(response);
  } else {
    Serial.print("Text Error code: ");
    Serial.println(httpResponseCode);
  }
  
  http.end();
}

void loop() {
  // Kiểm tra kết nối WiFi
  if(WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi mất kết nối!");
    return;
  }

  // Kiểm tra thời gian để gửi text
  // unsigned long currentMillis = millis();
  // if (currentMillis - previousMillis >= textInterval) {
  //   previousMillis = currentMillis;
  //   sendText();
  // }
  int control_value = digitalRead(input_control);
  if (millis() - previousMillis >= 500 && control_value == 1 && previousControlValue == 0) {
    sendText();
    previousMillis = millis(); // Cập nhật thời gian
  }
  previousControlValue = control_value;

  /*
    khi chưa nhấn thì control_value = 0 (sai), previousControlValue = 0 (thỏa)
    khi nhấn lần 1 thì control_value = 1 (thỏa), previousControlValue = 0 (thỏa)
             lúc thả ra thì control_value = 0 (sai), previousControlValue = 0 (thỏa)
    khi nhấn lần 2 thì control_value = 1 (thỏa), previousControlValue = 0 (thỏa)
    chỉ gửi tin nhắn khi trạng thái thay đổi từ 0 sang 1
    chỉ gửi tin nhắn khi nút được nhấn từ trạng thái thả trước đó
  */

  // Chụp ảnh
  camera_fb_t * fb = esp_camera_fb_get();
  if(!fb) {
    Serial.println("Chụp ảnh thất bại");
    return;
  }

  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "image/jpeg");
  
  // Gửi hình ảnh lên server
  int httpResponseCode = http.POST(fb->buf, fb->len);
  
  if(httpResponseCode > 0) {
    String response = http.getString();
    Serial.println("Image HTTP Response code: " + String(httpResponseCode));
    Serial.println(response);
    Serial.println(" ");
  } else {
    Serial.print("Image Error code: ");
    Serial.println(httpResponseCode);
  }
  
  // Giải phóng bộ nhớ
  esp_camera_fb_return(fb);
  http.end();

  // Delay giữa các lần chụp và gửi
  delay(50); // Điều chỉnh tốc độ stream tại đây
}