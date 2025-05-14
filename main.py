import cv2
import winsound
import face_recognition
import requests
import pickle
import time

# Paths
ENCODING_PATH = "owner_encoding.pkl"
IMAGE_PATH = "cam_capture.png"

# Load owner face encoding
with open(ENCODING_PATH, "rb") as f:
    owner_encoding = pickle.load(f)

# Telegram alert
def send_alert(image_path):
    try:
        with open(image_path, 'rb') as photo:
            files = {'photo': photo}
            response = requests.post(
                'https://api.telegram.org/bot<your_bot_token>/sendPhoto?chat_id=<your_chat_id>',
                files=files
            )
            print("📤 Telegram sent:", response.status_code)
    except Exception as e:
        print("❌ Telegram error:", e)

# Sound alert
def sound():
    winsound.PlaySound('security cam imp files_alert.wav', winsound.SND_FILENAME)

# Save frame
def save_frame(frame):
    cv2.imwrite(IMAGE_PATH, frame)
    print("📸 Intruder capture saved.")
    return IMAGE_PATH

# Load Haar cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Start webcam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    print("❌ Webcam not accessible.")
    exit()

last_alert_time = 0
alert_cooldown = 15  # seconds
alert_active = False
owner_last_seen = False  # Flag to avoid printing "Owner detected" repeatedly

print("🔒 Security system running...")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)

    current_time = time.time()

    if len(faces) > 0:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        if len(encodings) > 0:
            owner_found = False
            for encoding in encodings:
                match = face_recognition.compare_faces([owner_encoding], encoding, tolerance=0.5)
                if match[0]:
                    owner_found = True
                    break

            if not owner_found:
                if not alert_active or (current_time - last_alert_time > alert_cooldown):
                    print("🚨 Unknown face detected!")
                    img_path = save_frame(frame)
                    send_alert(img_path)
                    sound()
                    last_alert_time = current_time
                    alert_active = True
                    owner_last_seen = False
                else:
                    print("⏳ Alert already sent. Cooling down.")
            else:
                if not owner_last_seen:
                    print("✅ Owner detected. No alert.")
                    owner_last_seen = True
                alert_active = False
        else:
            print("⚠️ Face detected but encoding failed.")
            alert_active = False
            owner_last_seen = False
    else:
        alert_active = False
        owner_last_seen = False  # Reset flag when no face is in view

    cv2.imshow("Security Camera", frame)
    if cv2.waitKey(10) == 27:  # ESC
        print("🛑 System stopped.")
        break

cap.release()
cv2.destroyAllWindows()
