import face_recognition
import cv2
import numpy as np
import csv
from datetime import datetime, timedelta

video_cap = cv2.VideoCapture(0)

Messi_image = face_recognition.load_image_file("Face_img/messi2.jpg")
Messi_encoding = face_recognition.face_encodings(Messi_image)[0]

Ronaldo_image = face_recognition.load_image_file("Face_img/Ronaldo/ronaldo1.jpg")
Ronaldo_encoding = face_recognition.face_encodings(Ronaldo_image)[0]

# Danh sách các mã hóa khuôn mặt đã biết
known_face_encoding = [
    Messi_encoding,
    Ronaldo_encoding
]
known_faces_names = [
    "Phuc",
    "Ronaldo"
]

last_attendance_time = {}           # Biến lưu thời gian điểm danh gần nhất của mỗi người

attendance_status = {}              # Biến kiểm soát lần điểm danh thứ hai

face_locations = []
face_encodings = []
face_names = []

now = datetime.now()
current_date = now.strftime("%d-%m-%Y")

f_in = open(current_date + '_in.csv', 'w+', newline='')             # Mở file CSV để lưu kết quả điểm danh
lnwriter_in = csv.writer(f_in)

f_out = open(current_date + '_out.csv', 'w+', newline='')           # Mở file CSV thứ hai để lưu kết quả điểm danh ra
lnwriter_out = csv.writer(f_out)

while True:
    ret, frame = video_cap.read()
    if not ret:
        print("Không thể nhận khung hình từ ESP32-CAM. Kiểm tra kết nối.")
        break
    frame = cv2.flip(frame, 1)
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)           # Resize khung hình xuống 1/4 để tăng tốc độ xử lý

    rgb_small_frame = small_frame[:, :, ::-1]                  # Chuyển đổi khung hình thành RGB (đảo trục màu)
    rgb_small_frame = cv2.cvtColor(rgb_small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small_frame)           # Nhận diện vị trí và mã hóa khuôn mặt trong khung hình đã thu nhỏ
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
    face_names = []

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encoding, face_encoding)
        face_distance = face_recognition.face_distance(known_face_encoding, face_encoding)
        best_match_index = np.argmin(face_distance)
        name = " "

        if matches[best_match_index]:
            name = known_faces_names[best_match_index]

        face_names.append(name)

        if name in known_faces_names:           # Ghi nhận nếu khuôn mặt được nhận diện là một trong những người đã biết
            now = datetime.now()

            if name not in last_attendance_time or (now - last_attendance_time[name]) > timedelta(seconds=30):          # Chỉ điểm danh nếu đã qua 30 giây kể từ lần cuối
                last_attendance_time[name] = now
                current_time = now.strftime("%H:%M:%S")
                current_date = now.strftime("%d-%m-%Y")

                if name not in attendance_status or not attendance_status[name]:        # Kiểm tra xem người đã điểm danh trước đó chưa
                    lnwriter_in.writerow([name, current_date, current_time])
                    attendance_status[name] = True
                    print(f"{name} đã điểm danh VÀO lúc {current_date} {current_time}")
                else:
                    lnwriter_out.writerow([name, current_date, current_time])
                    f_out.flush()
                    attendance_status[name] = False
                    print(f"{name} đã điểm danh RA lúc {current_date} {current_time}")

    cv2.imshow("attendance system", frame)
    if cv2.waitKey(1) == ord("q"):
        break

video_cap.release()
cv2.destroyAllWindows()
f_in.close()
f_out.close()
