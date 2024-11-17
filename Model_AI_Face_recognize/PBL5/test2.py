# OK CAM LAPTOP - NOT CLASS - BASIC
import face_recognition
import cv2
import numpy as np
import csv
from datetime import datetime, timedelta
import serial

# Cấu hình serial
ser = serial.Serial('COM3', 115200)
while ser.in_waiting > 0:
    startup_data = ser.readline().decode('utf-8', errors='ignore').strip()

video_capture = cv2.VideoCapture(0)

# Load a sample picture and learn how to recognize it.
messi_image = face_recognition.load_image_file("Face_img/messi.jpg")
messi_face_encoding = face_recognition.face_encodings(messi_image)[0]

# Load a second sample picture and learn how to recognize it.
ronaldo_image = face_recognition.load_image_file("Face_img/Ronaldo/ronaldo.jpg")
ronaldo_face_encoding = face_recognition.face_encodings(ronaldo_image)[0]

# Create arrays of known face encodings and their names
known_face_encodings = [
    messi_face_encoding,
    ronaldo_face_encoding
]
known_face_names = [
    "Phuc",
    "Ronaldo"
]

while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_frame = np.ascontiguousarray(frame[:, :, ::-1])

    # Find all the faces and face enqcodings in the frame of video
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    # Loop through each face in this frame of video
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

        name = "Unknown"

        # If a match was found in known_face_encodings, just use the first one.
        # if True in matches:
        #     first_match_index = matches.index(True)
        #     name = known_face_names[first_match_index]

        # Or instead, use the known face with the smallest distance to the new face
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Attendance Face Recognition', frame)

    # Hit 'q' on the keyboard to quit!
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    # if ser.in_waiting > 0:
    serial_input = ser.readline().decode('utf-8', errors='ignore').strip()
    if cv2.waitKey(1) & 0xFF == ord(serial_input[0]):
            break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()