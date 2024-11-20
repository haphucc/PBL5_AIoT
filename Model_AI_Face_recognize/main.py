import face_recognition
import cv2
import numpy as np
import csv
from datetime import datetime, timedelta
import os
import mysql.connector
import time
import requests
import serial

# Biến toàn cục để lưu trữ encodings và tên
known_face_encodings = []
known_face_names = []
last_attendance_time = {}
attendance_status = {}

# Trạng thái chụp ảnh
is_capturing = False
capture_count = 0
MAX_CAPTURES = 10
current_capture_name = ""

# Trạng thái camera
camera_active = False

# Thời gian chờ trước khi tắt camera (giây)
CAMERA_TIMEOUT = 60
last_detection_time = None

# Khởi tạo file CSV
now = datetime.now()
current_date = now.strftime("%d-%m-%Y")
f_in = open(current_date + '_in.csv', 'w+', newline='')
lnwriter_in = csv.writer(f_in)
f_out = open(current_date + '_out.csv', 'w+', newline='')
lnwriter_out = csv.writer(f_out)


def create_person_folder(name):
    """
    Tạo thư mục cho người mới nếu chưa tồn tại
    """
    folder_path = os.path.join("Face_img", name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path


def capture_face(frame, name):
    """
    Chụp và lưu ảnh khuôn mặt
    """
    global capture_count

    face_locations = face_recognition.face_locations(frame)

    if len(face_locations) == 1:
        folder_path = create_person_folder(name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}_{capture_count + 1}.jpg"
        file_path = os.path.join(folder_path, filename)

        top, right, bottom, left = face_locations[0]
        padding = 50
        height, width = frame.shape[:2]

        top = max(top - padding, 0)
        bottom = min(bottom + padding, height)
        left = max(left - padding, 0)
        right = min(right + padding, width)

        face_image = frame[top:bottom, left:right]
        cv2.imwrite(file_path, face_image)

        capture_count += 1
        print(f"Đã chụp ảnh {capture_count}/{MAX_CAPTURES} cho {name}")
        return True
    return False


def load_training_data():
    """
    Load và encode tất cả ảnh từ thư mục Face_img
    """
    global known_face_encodings, known_face_names

    known_face_encodings = []
    known_face_names = []

    base_dir = "Face_img"
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        return

    person_folders = [d for d in os.listdir(base_dir)
                      if os.path.isdir(os.path.join(base_dir, d))]

    for person_folder in person_folders:
        folder_path = os.path.join(base_dir, person_folder)

        valid_extensions = ['.jpg', '.jpeg', '.png']
        image_files = [f for f in os.listdir(folder_path)
                       if os.path.splitext(f)[1].lower() in valid_extensions]

        for image_file in image_files:
            image_path = os.path.join(folder_path, image_file)
            try:
                image = face_recognition.load_image_file(image_path)
                face_encodings = face_recognition.face_encodings(image)

                if len(face_encodings) > 0:
                    known_face_encodings.append(face_encodings[0])
                    known_face_names.append(person_folder)
                else:
                    print(f"Không tìm thấy khuôn mặt trong ảnh: {image_file}")

            except Exception as e:
                print(f"Lỗi khi xử lý ảnh {image_file}: {str(e)}")

    print("\nĐã hoàn thành việc load dữ liệu training:")
    for name in set(known_face_names):
        print(f"- Số lượng encodings cho {name}: {known_face_names.count(name)}")
    print()


def get_latest_text_data():
    """
    Truy vấn lấy dữ liệu text mới nhất từ bảng text_data
    """
    try:
        if not hasattr(get_latest_text_data, 'last_timestamp'):
            db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="esp32cam_db"
            )
            cursor = db.cursor()

            cursor.execute("SELECT timestamp FROM text_data ORDER BY timestamp DESC LIMIT 1")
            result = cursor.fetchone()

            if result:
                get_latest_text_data.last_timestamp = result[0]
            else:
                get_latest_text_data.last_timestamp = datetime.now()

            cursor.close()
            db.close()
            return None

        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="esp32cam_db"
        )
        cursor = db.cursor()

        cursor.execute("SELECT timestamp, text_content FROM text_data ORDER BY timestamp DESC LIMIT 1")
        result = cursor.fetchone()

        cursor.close()
        db.close()

        if result:
            current_timestamp = result[0]

            if current_timestamp != get_latest_text_data.last_timestamp:
                get_latest_text_data.last_timestamp = current_timestamp
                text_content = result[1]
                print(f"Dữ liệu text mới từ ESP32: {text_content}")
                return text_content

        return None

    except Exception as e:
        print(f"Lỗi khi truy vấn dữ liệu text: {str(e)}")
        return None


def send_attendance_to_server(name, status):
    """
    Gửi thông tin điểm danh lên web server
    """
    try:
        url = "http://192.168.1.10:82/esp32_employee_attendance/postdemo.php"
        data = {
            "employee_name": name,
            "status": status
        }

        response = requests.post(url, data=data)

        if response.text.strip() == "success":
            print(f"Đã gửi dữ liệu điểm danh thành công lên server cho {name}\n")
        else:
            print(f"Lỗi khi gửi dữ liệu lên server: {response.text}")

    except Exception as e:
        print(f"Lỗi kết nối đến server: {str(e)}")


def process_attendance(name):
    """
    Xử lý ghi nhận điểm danh vào/ra cho người dùng
    """
    global last_attendance_time, attendance_status, last_detection_time

    now = datetime.now()
    last_detection_time = now  # Cập nhật thời gian phát hiện cuối cùng

    if name not in last_attendance_time or \
            (now - last_attendance_time[name]) > timedelta(seconds=30):

        last_attendance_time[name] = now
        current_time = now.strftime("%H:%M:%S")
        current_date = now.strftime("%d-%m-%Y")

        if name not in attendance_status or not attendance_status[name]:
            lnwriter_in.writerow([name, current_date, current_time])
            attendance_status[name] = True
            print(f"{name} đã điểm danh VÀO lúc {current_date} {current_time}")
            send_attendance_to_server(name, "IN")
        else:
            lnwriter_out.writerow([name, current_date, current_time])
            f_out.flush()
            attendance_status[name] = False
            print(f"{name} đã điểm danh RA lúc {current_date} {current_time}")
            send_attendance_to_server(name, "OUT")


def get_latest_image_from_db():
    """
    Truy vấn lấy hình ảnh mới nhất từ cơ sở dữ liệu
    """
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="esp32cam_db"
        )
        cursor = db.cursor()

        cursor.execute("SELECT image_data FROM images ORDER BY timestamp DESC LIMIT 1")
        result = cursor.fetchone()

        cursor.close()
        db.close()

        if result:
            nparr = np.frombuffer(result[0], np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return frame

    except Exception as e:
        print(f"Lỗi kết nối database: {str(e)}")

    return None


def run_system():
    global is_capturing, capture_count, current_capture_name, camera_active, last_detection_time

    frame_count = 0
    try:
        while True:
            if not camera_active:
                # Chờ tín hiệu CHAM_CONG từ database
                text_data = get_latest_text_data()
                if text_data == "CHAM_CONG":
                    camera_active = True
                    last_detection_time = datetime.now()
                    print("Đã bật camera cho phiên làm việc mới")
                else:
                    time.sleep(1)
                    continue

            frame = get_latest_image_from_db()
            if frame is None:
                print("Không có hình ảnh trong database.")
                time.sleep(1)
                continue

            frame_count += 1

            # Xử lý phím nhấn
            key = cv2.waitKey(1) & 0xFF

            # Nhấn 'i' để bắt đầu chế độ chụp ảnh
            if key == ord('i') and not is_capturing:
                is_capturing = True
                capture_count = 0
                current_capture_name = input("Nhập tên người cần thêm: ")
                print(f"Bắt đầu chụp ảnh cho {current_capture_name}")
                last_detection_time = datetime.now()
                continue

            # Nhấn 'q' để thoát
            elif key == ord('q'):
                break

            # Chế độ chụp ảnh
            if is_capturing:
                cv2.putText(frame, f"Capturing: {capture_count}/{MAX_CAPTURES}",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                if frame_count % 30 == 0:
                    if capture_face(frame, current_capture_name):
                        if capture_count >= MAX_CAPTURES:
                            print(f"Đã chụp đủ {MAX_CAPTURES} ảnh cho {current_capture_name}")
                            time.sleep(5)
                            is_capturing = False
                            camera_active = False
                            # time.sleep(5)
                            cv2.destroyAllWindows()
                            load_training_data()
                            print("Camera đã tắt. Đang chờ tín hiệu CHAM_CONG mới...")
                            continue

            # Chế độ nhận diện bình thường
            else:
                if frame_count % 3 != 0:
                    continue

                scale_factor = 0.25
                small_frame = cv2.resize(frame, (0, 0), fx=scale_factor, fy=scale_factor)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                # Kiểm tra timeout nếu không phát hiện khuôn mặt
                if len(face_locations) == 0 and last_detection_time is not None:
                    if (datetime.now() - last_detection_time).seconds > CAMERA_TIMEOUT:
                        print("Không phát hiện khuôn mặt trong 40 giây. Tắt camera.")
                        camera_active = False
                        cv2.destroyAllWindows()
                        print("Camera đã tắt. Đang chờ tín hiệu CHAM_CONG mới...")
                        continue

                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

                    name = "Unknown"

                    if True in matches:
                        best_match_index = np.argmin(face_distances)
                        if matches[best_match_index]:
                            name = known_face_names[best_match_index]
                            process_attendance(name)

                            # Tắt camera sau khi nhận diện thành công
                            print("Đã hoàn thành chấm công. Tắt camera sau 5 giây...")
                            time.sleep(5)
                            camera_active = False
                            cv2.destroyAllWindows()
                            print("Camera đã tắt. Đang chờ tín hiệu CHAM_CONG mới...")
                            continue

                    top = int(top / scale_factor)
                    right = int(right / scale_factor)
                    bottom = int(bottom / scale_factor)
                    left = int(left / scale_factor)

                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.6, (255, 255, 255), 1)

            # Hiển thị frame khi camera đang hoạt động
            if camera_active:
                cv2.imshow('Attendance Face Recognition System', frame)

    except Exception as e:
        print(f"Lỗi xử lý video: {str(e)}")

    finally:
        cv2.destroyAllWindows()
        f_in.close()
        f_out.close()


# Chạy hệ thống
if __name__ == "__main__":
    load_training_data()
    run_system()
