#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7735.h>

//Vcc=5V, LED=3.3V
#define TFT_CS         15  //chip select connect to pin 15
#define TFT_RST        12   //reset connect to pin 2
#define TFT_A0         2   //AO/DC connect to pin 4  
#define TFT_SDA        13  //Data = SDA/MOSI connect to pin 33
#define TFT_SCK        14  //Clock = SCK connect to pin 14

Adafruit_ST7735 tft = Adafruit_ST7735(TFT_CS, TFT_A0, TFT_SDA, TFT_SCK, TFT_RST);

//------------Dinh nghia mau sac----------------
#define BLACK 0x0000    
#define BLUE 0x001F    
#define RED 0xF800      
#define GREEN 0x07E0
#define CYAN 0x07FF
#define MAGENTA 0xF81F  
#define YELLOW 0xFFE0
#define WHITE 0xFFFF

// Cấu hình WiFi
const char* ssid = "LUN 1";
const char* password = "Xomtro179";

// URL của server
const char* serverUrl = "http://192.168.1.10:82/esp32cam/postdata.php";
const char* textServerUrl = "http://192.168.1.10:82/esp32cam/posttext.php"; 
const char* attendanceUrl = "http://192.168.1.10:82/esp32_employee_attendance/postdemo.php";

// Biến để theo dõi thời gian
unsigned long previousMillis = 0;
bool previousControlValue = 0;

// Biến cho hệ thống chấm công
String lastTimestamp = "";
bool isFirstRun = true;
unsigned long lastAttendanceCheck = 0;

#define input_control 4

void printText(char *text, uint16_t color, int x, int y,int textSize ){
  tft.setCursor(x, y);
  tft.setTextColor(color);
  tft.setTextSize(textSize);
  tft.print(text);
}

void setup() {
  Serial.begin(115200);
  tft.initR(INITR_BLACKTAB);      //Thiet lap LCD TFT
  tft.fillScreen(BLACK);          //Thiet lap mau nen LCD
  tft.setRotation(3);  // Giá trị 2 để xoay 180 độ

  printText("PBL5: CHUYEN NGANH", CYAN, 20, 20, 1);
  printText("KY THUAT DIEN TU", CYAN, 25, 35, 1);

  printText("Ha Phuoc Phuc 20DT2", WHITE, 17, 70, 1);
  printText("Dinh Van Quang 20DT1", WHITE, 15, 85, 1);
  delay(2000);

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

  if(psramFound()){
    config.frame_size = FRAMESIZE_VGA;
    config.jpeg_quality = 10;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Khởi tạo Camera thất bại với error 0x%x", err);
    return;
  }

  sensor_t * s = esp_camera_sensor_get();
  s->set_vflip(s, 1);
  s->set_hmirror(s, 1);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  tft.fillScreen(BLACK);
  printText("Ket noi WIFI.", YELLOW, 0, 58, 2);
  delay(1500);
  tft.fillScreen(BLACK);
  printText("Ket noi", YELLOW, 36, 42, 2);
  printText("DATABASE", YELLOW, 33, 63, 2);
  delay(1500);
  tft.fillScreen(BLACK);

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
  
  int httpResponseCode = http.POST("CHAM_CONG");
  
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

// Hàm kiểm tra dữ liệu chấm công
void checkAttendance() {
  HTTPClient http;
  http.begin(attendanceUrl);
  
  int httpResponseCode = http.GET();
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    
    StaticJsonDocument<2048> doc;
    DeserializationError error = deserializeJson(doc, response);
    
    if (error) {
      Serial.print("Lỗi parse JSON: ");
      Serial.println(error.c_str());
    } else {
      JsonArray array = doc.as<JsonArray>();
      
      if (array.size() > 0) {
        JsonObject latestRecord = array[0];
        String currentTimestamp = latestRecord["timestamp"].as<String>();
        
        if (isFirstRun) {
          lastTimestamp = currentTimestamp;
          isFirstRun = false;
          Serial.println("Đã bắt đầu theo dõi dữ liệu chấm công...");
          tft.fillScreen(BLACK);
          printText("Dang theo doi", CYAN, 0, 35, 2);
          printText("du lieu", CYAN, 0, 55, 2);
          printText("cham cong", CYAN, 0, 75, 2);
        }
        else if (currentTimestamp != lastTimestamp) {
          // Xóa màn hình trước khi hiển thị thông tin mới
          tft.fillScreen(BLACK);

          // Hiển thị tiêu đề
          printText("THONG TIN CHAM CONG", YELLOW, 23, 10, 1);
          printText("-------------------", WHITE, 23, 25, 1);

          // Hiển thị thông tin nhân viên
          String empName = latestRecord["employee_name"].as<String>();
          String status = latestRecord["status"].as<String>();
          
          printText("Nhan vien:", CYAN, 5, 41, 1);
          printText((char*)empName.c_str(), WHITE, 77, 37, 2);

          printText("Trang thai:", CYAN, 5, 62, 1);
          printText((char*)status.c_str(), RED, 77, 58, 2);
          // Hiển thị trạng thái với màu khác nhau
          // if(status == "CHECK IN") {
          //   printText((char*)status.c_str(), GREEN, 80, 75, 2);
          // } else {
          //   printText((char*)status.c_str(), RED, 80, 50, 2);
          // }

          // Tách và hiển thị thời gian
          int spaceIndex = currentTimestamp.indexOf(' ');
          String dateStr = currentTimestamp.substring(0, spaceIndex);
          String timeStr = currentTimestamp.substring(spaceIndex + 1);

          // Hiển thị thời gian
          printText("Thoi gian:", CYAN, 5, 83, 1);
          printText((char*)dateStr.c_str(), WHITE, 20, 95, 2);
          printText((char*)timeStr.c_str(), WHITE, 25, 114, 2);
          
          // In ra Serial để debug
          Serial.println("\n=== Dữ liệu chấm công mới ===");
          Serial.println("Nhân viên: " + empName);
          Serial.println("Trạng thái: " + status);
          Serial.println("Thời gian: " + currentTimestamp);
          Serial.println("-------------------");
          
          lastTimestamp = currentTimestamp;
        }
      }
    }
  } else {
    Serial.print("Lỗi HTTP request chấm công. Error code: ");
    Serial.println(httpResponseCode);
    // Hiển thị lỗi trên màn hình
    tft.fillScreen(BLACK);
    printText("Loi ket noi!", RED, 10, 60, 2);
  }
  
  http.end();
}

void loop() {
  if(WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi mất kết nối!");
    return;
  }

  // Xử lý nút nhấn
  int control_value = digitalRead(input_control);
  if (millis() - previousMillis >= 500 && control_value == 1 && previousControlValue == 0) {
    sendText();
    previousMillis = millis();
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

  // Kiểm tra dữ liệu chấm công mỗi 5 giây
  if (millis() - lastAttendanceCheck >= 5000) {
    checkAttendance();
    lastAttendanceCheck = millis();
  }

  // Chụp và gửi ảnh
  camera_fb_t * fb = esp_camera_fb_get();
  if(!fb) {
    Serial.println("Chụp ảnh thất bại");
    return;
  }

  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "image/jpeg");
  
  int httpResponseCode = http.POST(fb->buf, fb->len);
  
  if(httpResponseCode > 0) {
    String response = http.getString();
    // Serial.println("Image HTTP Response code: " + String(httpResponseCode));
    // Serial.println(response);
    // Serial.println(" ");
  } else {
    Serial.print("Image Error code: ");
    Serial.println(httpResponseCode);
  }
  
  esp_camera_fb_return(fb);
  http.end();

  delay(50);
}
