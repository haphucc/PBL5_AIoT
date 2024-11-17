# OK CAM ESP32 PHP - CLASS

import face_recognition
import cv2
import numpy as np
import csv
from datetime import datetime, timedelta
import os
import mysql.connector


class FaceRecognitionAttendance:
    def __init__(self):
        """
        Khởi tạo hệ thống nhận diện khuôn mặt
        """
        # Khởi tạo danh sách để lưu encodings và tên
        self.known_face_encodings = []
        self.known_face_names = []

        # Load ảnh và encode từ các thư mục
        self.load_training_data()

        self.last_attendance_time = {}
        self.attendance_status = {}

        # Khởi tạo file CSV
        now = datetime.now()
        self.current_date = now.strftime("%d-%m-%Y")
        self.f_in = open(self.current_date + '_in.csv', 'w+', newline='')
        self.lnwriter_in = csv.writer(self.f_in)
        self.f_out = open(self.current_date + '_out.csv', 'w+', newline='')
        self.lnwriter_out = csv.writer(self.f_out)

    def load_training_data(self):
        """
        Load và encode tất cả ảnh từ thư mục Face_img/Phuc và Face_img/Ronaldo
        """
        base_dir = "Face_img"
        for person_folder in ["Phuc", "Ronaldo"]:
            folder_path = os.path.join(base_dir, person_folder)
            if not os.path.exists(folder_path):
                print(f"Thư mục {folder_path} không tồn tại!")
                continue

            # Lấy tất cả file ảnh trong thư mục
            valid_extensions = ['.jpg', '.jpeg', '.png']
            image_files = [f for f in os.listdir(folder_path)
                           if os.path.splitext(f)[1].lower() in valid_extensions]

            for image_file in image_files:
                image_path = os.path.join(folder_path, image_file)
                try:
                    # Load ảnh
                    image = face_recognition.load_image_file(image_path)

                    # Tìm tất cả khuôn mặt trong ảnh
                    face_encodings = face_recognition.face_encodings(image)

                    if len(face_encodings) > 0:
                        # Lấy encoding đầu tiên nếu có nhiều khuôn mặt trong ảnh
                        self.known_face_encodings.append(face_encodings[0])
                        self.known_face_names.append(person_folder)
                    else:
                        print(f"Không tìm thấy khuôn mặt trong ảnh: {image_file}")

                except Exception as e:
                    print(f"Lỗi khi xử lý ảnh {image_file}: {str(e)}")

        print(f"\nĐã hoàn thành việc load dữ liệu training:")
        print(f"- Số lượng encodings cho Phuc: {self.known_face_names.count('Phuc')}")
        print(f"- Số lượng encodings cho Ronaldo: {self.known_face_names.count('Ronaldo')}\n")

    def get_latest_image_from_db(self):
        """
        Truy vấn lấy hình ảnh mới nhất từ cơ sở dữ liệu
        """
        # Kết nối database
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="esp32cam_db"
        )
        cursor = db.cursor()

        # Lấy hình ảnh mới nhất
        cursor.execute("SELECT image_data FROM images ORDER BY timestamp DESC LIMIT 1")
        result = cursor.fetchone()

        cursor.close()
        db.close()

        if result:
            # Chuyển đổi dữ liệu nhị phân thành numpy array
            nparr = np.frombuffer(result[0], np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return frame

        return None

    def process_attendance(self, name):
        if name in ["Phuc", "Ronaldo"]:  # Hoặc dùng set để kiểm tra nếu có nhiều người
            now = datetime.now()

            if name not in self.last_attendance_time or \
                    (now - self.last_attendance_time[name]) > timedelta(seconds=30):

                self.last_attendance_time[name] = now
                current_time = now.strftime("%H:%M:%S")
                current_date = now.strftime("%d-%m-%Y")

                if name not in self.attendance_status or not self.attendance_status[name]:
                    self.lnwriter_in.writerow([name, current_date, current_time])
                    self.attendance_status[name] = True
                    print(f"{name} đã điểm danh VÀO lúc {current_date} {current_time}")
                else:
                    self.lnwriter_out.writerow([name, current_date, current_time])
                    self.f_out.flush()
                    self.attendance_status[name] = False
                    print(f"{name} đã điểm danh RA lúc {current_date} {current_time}")

    def run(self):
        frame_count = 0
        try:
            while True:
                # Lấy hình ảnh mới nhất từ cơ sở dữ liệu
                frame = self.get_latest_image_from_db()
                if frame is None:
                    print("Không có hình ảnh trong database.")
                    continue

                frame_count += 1
                # Xử lý mỗi n frame để tăng hiệu suất
                if frame_count % 3 != 0:  # Xử lý 1/3 số frame
                    continue

                # Resize frame để tăng hiệu suất
                scale_factor = 0.25
                small_frame = cv2.resize(frame, (0, 0), fx=scale_factor, fy=scale_factor)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

                # Nhận diện khuôn mặt
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                # Xử lý từng khuôn mặt
                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    # So sánh với tất cả các encodings đã biết
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)

                    name = "Unknown"

                    if True in matches:
                        # Tìm encoding phù hợp nhất
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = self.known_face_names[best_match_index]
                            self.process_attendance(name)

                    # Scale back các tọa độ
                    top = int(top / scale_factor)
                    right = int(right / scale_factor)
                    bottom = int(bottom / scale_factor)
                    left = int(left / scale_factor)

                    # Vẽ khung và tên
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.6, (255, 255, 255), 1)

                cv2.imshow('Attendance Face Recognition System', frame)

                if cv2.waitKey(1000) & 0xFF == ord('q'):  # Đợi 1 giây trước khi lấy frame mới
                    break

        except Exception as e:
            print(f"Lỗi xử lý video: {str(e)}")

        finally:
            cv2.destroyAllWindows()
            self.f_in.close()
            self.f_out.close()


if __name__ == "__main__":
    face_system = FaceRecognitionAttendance()
    face_system.run()