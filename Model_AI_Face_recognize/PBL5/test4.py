import face_recognition
import cv2
import numpy as np
import csv
from datetime import datetime, timedelta

class FaceRecognitionAttendance:
    def __init__(self):
        self.video_capture = cv2.VideoCapture(0)

        # Load và mã hóa ảnh khuôn mặt mẫu
        self.messi_image = face_recognition.load_image_file("Face_img/messi.jpg")
        self.messi_encoding = face_recognition.face_encodings(self.messi_image)[0]

        self.ronaldo_image = face_recognition.load_image_file("Face_img/Ronaldo/ronaldo.jpg")
        self.ronaldo_encoding = face_recognition.face_encodings(self.ronaldo_image)[0]

        # Tạo mảng chứa mã hóa khuôn mặt và tên tương ứng
        self.known_face_encodings = [
            self.messi_encoding,
            self.ronaldo_encoding
        ]
        self.known_face_names = [
            "Phuc",
            "Ronaldo"
        ]

        # Biến theo dõi điểm danh
        self.last_attendance_time = {}  # Lưu thời gian điểm danh gần nhất
        self.attendance_status = {}  # Kiểm soát trạng thái vào/ra

        # Khởi tạo file CSV
        now = datetime.now()
        self.current_date = now.strftime("%d-%m-%Y")
        self.f_in = open(self.current_date + '_in.csv', 'w+', newline='')
        self.lnwriter_in = csv.writer(self.f_in)
        self.f_out = open(self.current_date + '_out.csv', 'w+', newline='')
        self.lnwriter_out = csv.writer(self.f_out)

    def process_attendance(self, name):
        if name in self.known_face_names:
            now = datetime.now()

            # Kiểm tra khoảng thời gian giữa các lần điểm danh
            if name not in self.last_attendance_time or \
                    (now - self.last_attendance_time[name]) > timedelta(seconds=30):

                self.last_attendance_time[name] = now
                current_time = now.strftime("%H:%M:%S")
                current_date = now.strftime("%d-%m-%Y")

                # Xử lý điểm danh vào/ra
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
        while True:
            ret, frame = self.video_capture.read()
            if not ret:
                print("Không thể nhận khung hình từ camera. Kiểm tra kết nối.")
                break

            # Flip và resize frame để tối ưu hiệu suất
            frame = cv2.flip(frame, 1)
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # Nhận diện khuôn mặt
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            # Xử lý từng khuôn mặt được phát hiện
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)

                name = "Unknown"
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
                    # Xử lý điểm danh
                    self.process_attendance(name)

                # Vẽ khung và tên
                # Nhân 4 lại kích thước vì đã resize frame xuống 1/4
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                # Vẽ khung xung quanh khuôn mặt
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                # Vẽ nhãn tên bên dưới khuôn mặt
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.6, (255, 255, 255), 1)

            # Hiển thị frame
            cv2.imshow('Attendance Face Recognition System', frame)

            # Nhấn 'q' để thoát
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Giải phóng tài nguyên
        self.video_capture.release()
        cv2.destroyAllWindows()
        self.f_in.close()
        self.f_out.close()

if __name__ == "__main__":
    face_system = FaceRecognitionAttendance()
    face_system.run()