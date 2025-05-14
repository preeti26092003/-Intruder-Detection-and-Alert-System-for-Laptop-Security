import cv2
import face_recognition
import pickle

IMG_PATH = "owner_face.jpg"
ENCODING_PATH = "owner_encoding.pkl"

# Use DirectShow backend to avoid MSMF errors
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    print("❌ Webcam not accessible.")
    exit()

print("📸 Press SPACE to capture your face, ESC to cancel.")

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        print("❌ Failed to capture frame from webcam.")
        break

    cv2.imshow("Register Owner", frame)
    key = cv2.waitKey(1)

    if key == 27:  # ESC
        print("❌ Cancelled.")
        break
    elif key == 32:  # SPACE key
        # Convert the frame to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Confirm the type and shape
        if rgb_frame.dtype != "uint8" or len(rgb_frame.shape) != 3 or rgb_frame.shape[2] != 3:
            print("❌ Invalid image format for face recognition.")
            continue

        face_locations = face_recognition.face_locations(rgb_frame)

        if len(face_locations) == 1:
            # Save the captured face image
            cv2.imwrite(IMG_PATH, frame)

            # Get the face encoding
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            if face_encodings:
                face_encoding = face_encodings[0]
                with open(ENCODING_PATH, "wb") as f:
                    pickle.dump(face_encoding, f)
                print("✅ Owner face saved and encoded.")
                break
            else:
                print("⚠️ Face encoding failed. Try again.")
        elif len(face_locations) == 0:
            print("⚠️ No face detected. Try again.")
        else:
            print("⚠️ Multiple faces detected. Please ensure only your face is visible.")

cap.release()
cv2.destroyAllWindows()
