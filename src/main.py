import cv2
import threading
import time
import os
import requests
import face_recognition
from flask import Flask, Response

from core.pid import PIDController
from hardware.pantilt import PanTiltMechanism
from config import settings


# --------------------------------------------------
# TELEGRAM SETTINGS
# --------------------------------------------------

# Do NOT put your real Telegram token directly in GitHub.
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

app = Flask(__name__)

current_frame = None
thread_lock = threading.Lock()


def send_alert(frame):
    """Send the captured target frame to Telegram."""

    try:
        print("[ALERT] Sending target image to Telegram...")

        _, buffer = cv2.imencode(".jpg", frame)

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"

        files = {
            "photo": (
                "alert.jpg",
                buffer.tobytes(),
                "image/jpeg"
            )
        }

        data = {
            "chat_id": CHAT_ID,
            "caption": "SENTRY ALERT: Target identified from floor level."
        }

        requests.post(
            url,
            files=files,
            data=data,
            timeout=10
        )

        print("[ALERT] Telegram message sent successfully.")

    except Exception as e:
        print(f"[ALERT ERROR] Failed to send Telegram message: {e}")


# --------------------------------------------------
# ASYNCHRONOUS VISION TRACKER
# --------------------------------------------------

class TestFaceTracker:

    def __init__(self):

        print("[TEST VISION] Initializing Target-Specific Vision...")

        self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

        self.cap.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            settings.FRAME_WIDTH
        )

        self.cap.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            settings.FRAME_HEIGHT
        )

        self.cap.set(
            cv2.CAP_PROP_BUFFERSIZE,
            1
        )

        self.raw_frame = None
        self.running = True

        # Thread-safe AI data
        self.ai_lock = threading.Lock()

        self.target_data = {
            "is_target": False,
            "center": None,
            "width": 0,
            "bbox": None,
            "frame_id": 0
        }

        self.target_encoding = None

        # Load target image if available
        if os.path.exists("target.jpeg"):

            image = face_recognition.load_image_file(
                "target.jpeg"
            )

            encodings = face_recognition.face_encodings(image)

            if encodings:

                self.target_encoding = encodings[0]

                print(
                    "[TEST VISION] Target encoding successfully loaded."
                )

            else:

                print(
                    "[ERROR] No face found in target.jpeg!"
                )

        # Start camera and AI threads
        threading.Thread(
            target=self._camera_thread,
            daemon=True
        ).start()

        threading.Thread(
            target=self._ai_thread,
            daemon=True
        ).start()

    # --------------------------------------------------
    # CAMERA THREAD
    # --------------------------------------------------

    def _camera_thread(self):

        # Grabs frames as fast as hardware allows
        while self.running:

            ret, frame = self.cap.read()

            if ret:
                self.raw_frame = frame

    # --------------------------------------------------
    # AI PROCESSING THREAD
    # --------------------------------------------------

    def _ai_thread(self):

        ai_frame_id = 0

        while self.running:

            if self.raw_frame is None:

                time.sleep(0.01)

                continue

            # Snapshot of latest frame
            frame = self.raw_frame.copy()

            ai_frame_id += 1

            # --------------------------------------------------
            # CLAHE SHADOW RECOVERY
            # --------------------------------------------------

            lab = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2LAB
            )

            l_channel, a_channel, b_channel = cv2.split(lab)

            clahe = cv2.createCLAHE(
                clipLimit=3.0,
                tileGridSize=(8, 8)
            )

            cl = clahe.apply(l_channel)

            merged = cv2.merge(
                (cl, a_channel, b_channel)
            )

            enhanced_bgr = cv2.cvtColor(
                merged,
                cv2.COLOR_LAB2BGR
            )

            rgb_frame = cv2.cvtColor(
                enhanced_bgr,
                cv2.COLOR_BGR2RGB
            )

            # --------------------------------------------------
            # FACE DETECTION
            # --------------------------------------------------

            face_locations = face_recognition.face_locations(
                rgb_frame,
                model="hog",
                number_of_times_to_upsample=1
            )

            face_encodings = face_recognition.face_encodings(
                rgb_frame,
                face_locations
            )

            target_found = False

            for (
                (top, right, bottom, left),
                encoding
            ) in zip(
                face_locations,
                face_encodings
            ):

                face_width = right - left

                # Face size filtering
                if not (15 <= face_width <= 250):
                    continue

                if self.target_encoding is not None:

                    matches = face_recognition.compare_faces(
                        [self.target_encoding],
                        encoding,
                        tolerance=0.5
                    )

                    if True in matches:

                        target_found = True

                        t_center = (
                            left + (right - left) // 2,
                            top + (bottom - top) // 2
                        )

                        # Safely update target information
                        with self.ai_lock:

                            self.target_data = {
                                "is_target": True,
                                "center": t_center,
                                "width": face_width,
                                "bbox": (
                                    left,
                                    top,
                                    right,
                                    bottom
                                ),
                                "frame_id": ai_frame_id
                            }

                        break

            # No target found
            if not target_found:

                with self.ai_lock:

                    self.target_data = {
                        "is_target": False,
                        "center": None,
                        "width": 0,
                        "bbox": None,
                        "frame_id": ai_frame_id
                    }

    # --------------------------------------------------
    # GET CURRENT STATE
    # --------------------------------------------------

    def get_current_state(self):

        if self.raw_frame is None:

            return None, None, False, 0

        frame = self.raw_frame.copy()

        with self.ai_lock:

            data = self.target_data.copy()

        if data["is_target"] and data["bbox"]:

            left, top, right, bottom = data["bbox"]

            cv2.rectangle(
                frame,
                (left, top),
                (right, bottom),
                (64, 128, 255),
                2
            )

            cv2.putText(
                frame,
                f"TARGET ({data['width']}px)",
                (left, top - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (64, 128, 255),
                2
            )

        return (
            frame,
            data["center"],
            data["is_target"],
            data["frame_id"]
        )

    # --------------------------------------------------
    # CLEANUP
    # --------------------------------------------------

    def cleanup(self):

        self.running = False

        if self.cap.isOpened():
            self.cap.release()


# --------------------------------------------------
# TRACKING TEST LOOP
# --------------------------------------------------

def tracking_test_loop():

    global current_frame

    print(
        "--- STARTING WEB-BASED TRACKING TEST ---"
    )

    vision = TestFaceTracker()

    time.sleep(1.5)

    servos = PanTiltMechanism()

    pan_pid = PIDController(
        settings.PAN_P,
        settings.PAN_I,
        settings.PAN_D
    )

    tilt_pid = PIDController(
        settings.TILT_P,
        settings.TILT_I,
        settings.TILT_D
    )

    last_alert_time = 0

    last_processed_ai_id = -1

    while True:

        frame, center, is_target, ai_frame_id = (
            vision.get_current_state()
        )

        if frame is None:
            continue

        if is_target and center:

            # Send alert once per 60 seconds
            if time.time() - last_alert_time > 60:

                threading.Thread(
                    target=send_alert,
                    args=(frame.copy(),),
                    daemon=True
                ).start()

                last_alert_time = time.time()

            # Only process a new AI coordinate
            if ai_frame_id != last_processed_ai_id:

                error_x = (
                    center[0]
                    - (settings.FRAME_WIDTH // 2)
                )

                error_y = (
                    center[1]
                    - (settings.FRAME_HEIGHT // 2)
                )

                pan_adjust = pan_pid.update(error_x)

                tilt_adjust = tilt_pid.update(error_y)

                servos.move(
                    pan_adjust,
                    tilt_adjust
                )

                last_processed_ai_id = ai_frame_id

            # Debug drawing
            cx = settings.FRAME_WIDTH // 2
            cy = settings.FRAME_HEIGHT // 2

            cv2.drawMarker(
                frame,
                (cx, cy),
                (0, 255, 0),
                cv2.MARKER_CROSS,
                20,
                2
            )

            cv2.putText(
                frame,
                f"AI Frame: {ai_frame_id}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2
            )

        else:

            # Target lost
            pan_pid.reset()
            tilt_pid.reset()

            cv2.putText(
                frame,
                "NO TARGET",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )

        with thread_lock:
            current_frame = frame.copy()

        time.sleep(0.01)


# --------------------------------------------------
# VIDEO STREAM GENERATOR
# --------------------------------------------------

def gen():

    while True:

        with thread_lock:

            if current_frame is None:
                continue

            _, buffer = cv2.imencode(
                ".jpg",
                current_frame,
                [
                    cv2.IMWRITE_JPEG_QUALITY,
                    60
                ]
            )

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + buffer.tobytes()
            + b"\r\n"
        )


# --------------------------------------------------
# FLASK ROUTE
# --------------------------------------------------

@app.route("/")
def video_feed():

    return Response(
        gen(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

if __name__ == "__main__":

    threading.Thread(
        target=tracking_test_loop,
        daemon=True
    ).start()

    app.run(
        host="0.0.0.0",
        port=5000,
        threaded=True,
        use_reloader=False
    )