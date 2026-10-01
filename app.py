import os
import threading
import time
import sqlite3
from datetime import datetime
from pathlib import Path

import cv2
import requests
from flask import Flask, jsonify, render_template
from dotenv import load_dotenv

from config import (
    CAMERA_INDEX,
    MOTION_AREA_THRESHOLD,
    ALERT_COOLDOWN_SECONDS,
    DATABASE_PATH,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
)

load_dotenv()

app = Flask(__name__)
stop_event = threading.Event()
camera_thread = None
camera_state = {"running": False, "motion": False, "last_event": None, "error": None}
state_lock = threading.Lock()


def init_db():
    Path(DATABASE_PATH).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS motion_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                area INTEGER NOT NULL
            )
        """)


def record_event(area):
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute(
            "INSERT INTO motion_events(timestamp, area) VALUES (?, ?)",
            (timestamp, int(area)),
        )
    with state_lock:
        camera_state["last_event"] = timestamp
    return timestamp


def send_telegram_alert(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(
            url,
            json={"chat_id": TELEGRAM_CHAT_ID, "text": message},
            timeout=8,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        app.logger.warning("Telegram alert failed: %s", exc)


def camera_worker():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        with state_lock:
            camera_state.update(running=False, error=f"Could not open camera index {CAMERA_INDEX}")
        return

    previous_gray = None
    last_alert_at = 0.0
    with state_lock:
        camera_state.update(running=True, error=None)

    try:
        while not stop_event.is_set():
            ok, frame = cap.read()
            if not ok:
                time.sleep(0.1)
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            motion = False
            largest_area = 0

            if previous_gray is not None:
                delta = cv2.absdiff(previous_gray, gray)
                thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
                thresh = cv2.dilate(thresh, None, iterations=2)
                contours, _ = cv2.findContours(
                    thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                )
                largest_area = max(
                    (int(cv2.contourArea(c)) for c in contours),
                    default=0,
                )
                motion = largest_area >= MOTION_AREA_THRESHOLD

            previous_gray = gray
            with state_lock:
                camera_state["motion"] = motion

            now = time.monotonic()
            if motion and now - last_alert_at >= ALERT_COOLDOWN_SECONDS:
                timestamp = record_event(largest_area)
                send_telegram_alert(
                    f"Motion detected at {timestamp}. Changed area: {largest_area} pixels."
                )
                last_alert_at = now

            time.sleep(0.03)
    finally:
        cap.release()
        with state_lock:
            camera_state["running"] = False
            camera_state["motion"] = False


@app.route("/")
def index():
    with state_lock:
        state = dict(camera_state)
    return render_template("index.html", state=state)


@app.route("/api/status")
def api_status():
    with state_lock:
        return jsonify(dict(camera_state))


@app.route("/api/events")
def api_events():
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT id, timestamp, area FROM motion_events ORDER BY id DESC LIMIT 50"
        ).fetchall()
    return jsonify([dict(row) for row in rows])


def start_camera_thread():
    global camera_thread
    if camera_thread is None or not camera_thread.is_alive():
        stop_event.clear()
        camera_thread = threading.Thread(target=camera_worker, daemon=True)
        camera_thread.start()


if __name__ == "__main__":
    init_db()
    start_camera_thread()
    try:
        app.run(host="127.0.0.1", port=5000, debug=False)
    finally:
        stop_event.set()
