# Smart Security Camera with Motion Detection and Alerts

A Raspberry Pi-based smart security camera prototype that uses OpenCV to detect motion from a camera feed and can send notifications through Telegram. A Flask dashboard provides a simple interface for viewing camera status and recent motion events.

## Project background

If accurate for your project, use this wording:

"I developed this project during my second year of B.Tech as part of my learning in IoT, computer vision, and automation. I am uploading it to GitHub now to document my earlier work and showcase my practical experience."

Update this statement if your actual project timeline differs.

## Features

- Motion detection using OpenCV frame differencing
- Flask web dashboard for camera and event status
- Event timestamps stored in a local SQLite database
- Optional Telegram alert integration
- Configurable motion sensitivity and cooldown interval
- Option to use a USB webcam for local testing or a Raspberry Pi camera
- Basic API endpoints for status and event history

## Technology stack

- Python
- OpenCV
- Flask
- SQLite
- Telegram Bot API (optional)
- Raspberry Pi Camera Module or USB webcam

## Project structure

```text
Smart-Security-Camera/
├── app.py
├── camera.py
├── config.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── templates/
│   └── index.html
├── static/
│   └── style.css
└── docs/
    └── README.md
```

## Requirements

- Python 3.10+
- Raspberry Pi with camera enabled, or a USB webcam for testing
- Telegram bot token and chat ID only if Telegram alerts are enabled

## Setup

1. Clone the repository and open the project folder.
2. Create and activate a virtual environment.

   Windows:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

   Raspberry Pi / Linux / macOS:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and configure values if needed. Never commit your real bot token.

5. Start the application:

   ```bash
   python app.py
   ```

6. Open `http://127.0.0.1:5000` in your browser.

For a Raspberry Pi accessed from another device on the same network, use the Pi's local IP address instead of `127.0.0.1`, and only expose the dashboard on a trusted network.

## How it works

1. The camera captures frames.
2. OpenCV compares consecutive grayscale, blurred frames to identify significant changes.
3. If the changed area exceeds the configured threshold, a motion event is recorded.
4. The dashboard displays recent events and the current camera status.
5. If Telegram credentials are configured, the app sends an alert subject to the cooldown setting.

This is basic frame-difference motion detection. Changes in lighting, shadows, or moving objects may trigger events; it is not a guaranteed human detector.

## Results and screenshots

When the app is running, the dashboard displays camera status, motion detection status, and recent event timestamps. Capture screenshots of your actual running application and save them in `docs/`.

You can then add images like this:

```markdown
![Security camera dashboard](docs/dashboard.png)
![Motion detection event](docs/motion-alert.png)
```

No output screenshots are included because they should represent your actual run and hardware.

## Configuration

The main settings are in `.env` or `config.py`:

- `CAMERA_INDEX`: webcam index (usually `0` for the first USB camera)
- `MOTION_AREA_THRESHOLD`: minimum changed-pixel contour area to count as motion
- `ALERT_COOLDOWN_SECONDS`: minimum interval between repeated alerts
- `TELEGRAM_BOT_TOKEN`: optional Telegram bot token
- `TELEGRAM_CHAT_ID`: optional destination chat ID

## Privacy and security

- Use the camera only in places where you have permission.
- Inform people where required by local rules.
- Keep Telegram credentials in `.env` and never commit secrets.
- Do not expose the Flask development server directly to the public Internet.
- This prototype is for learning and should not be treated as a certified security system.

## Future improvements

- Person detection using a lightweight object-detection model
- Save snapshots for motion events with appropriate privacy controls
- Add user authentication and role-based access
- Add secure remote access and event retention settings
- Support multiple cameras and configurable zones

## GitHub upload

Create a repository named `Smart-Security-Camera` with **Add README turned off**. Then, from the extracted project folder, run:

```bash
git init
git add .
git commit -m "Add smart security camera project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/Smart-Security-Camera.git
git push -u origin main
```
