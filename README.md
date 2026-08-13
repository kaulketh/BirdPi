# BirdPi

A Raspberry Pi-based bird house observation system that automatically captures images at configurable intervals and serves them through a lightweight web interface.

## Features

- **Automatic observation** — captures images on a configurable timer (default: every 5 minutes)
- **Manual capture** — trigger a shot on demand via the web UI
- **Image gallery** — browse all captures with previous/next navigation
- **System info** — displays hostname, uptime, and CPU temperature
- **Camera detection** — identifies the attached Raspberry Pi camera model

## Hardware Requirements

- Raspberry Pi (any model with camera connector)
- Raspberry Pi Camera Module (compatible with `rpicam-still`)
- Network connection for web access

## Software Requirements

| Requirement | Version |
|---|---|
| Python | >= 3.13 |
| Flask | >= 3.1 |
| rpicam-still | (part of libcamera / Picamera2 stack) |

## Installation

```bash
git clone <repo-url>
cd BirdPi
pip install -e .
```

## Configuration

Edit `src/birdpi/config.py` to adjust defaults:

| Setting | Default | Description |
|---|---|---|
| `data_path` | `/home/kaulketh/birdpi-data` | Directory where images are saved |
| `width` / `height` | `3280` / `2464` | Capture resolution |
| `interval` | `300` | Seconds between automatic captures |

Images are saved as `image_YYYYMMDD_HHMMSS.jpg`.

## Running

**Web server** (recommended):
```bash
python -m birdpi
```
The Flask server starts on `http://0.0.0.0:5000`.

**Single capture** (console mode):
```bash
python src/birdpi/main.py
```

**systemd service** — a service unit template is provided at `systemd/birdpi.service`. Configure it for your user and path, then enable with:
```bash
sudo systemctl enable birdpi
sudo systemctl start birdpi
```

## Web Interface

| Route | Method | Description |
|---|---|---|
| `/` | GET | Home page — latest captured image |
| `/gallery` | GET | Full image gallery, newest first |
| `/gallery/<filename>` | GET | Single image view with prev/next |
| `/capture` | POST | Trigger a manual capture |
| `/observation/start` | POST | Start automatic observation loop |
| `/observation/stop` | POST | Stop automatic observation loop |
| `/images/<filename>` | GET | Serve image files |

## Project Structure

```
BirdPi/
├── src/birdpi/
│   ├── main.py           # Entry point
│   ├── application.py    # Core BirdPi orchestrator
│   ├── config.py         # Configuration dataclass
│   ├── models.py         # CapturedImage data model
│   ├── storage.py        # Image file management
│   ├── observer.py       # Automatic capture loop (daemon thread)
│   ├── server.py         # Flask app initialisation
│   ├── system.py         # CPU temperature, uptime
│   ├── camera/
│   │   └── capture.py    # rpicam-still wrapper
│   ├── web/
│   │   ├── api.py        # Flask app factory
│   │   └── routes.py     # Route handlers
│   ├── templates/        # Jinja2 HTML templates
│   └── static/           # CSS
├── systemd/
│   └── birdpi.service    # systemd unit template
└── pyproject.toml
```

## Architecture Notes

- **Storage** is filesystem-only — no database. Images are listed by filename sort order.
- **Observer** runs in a daemon thread; capture failures are logged and retried on the next interval without stopping the loop.
- **System metrics** are read from Linux proc/sys files (`/proc/uptime`, `/sys/class/thermal/`), so the web server must run on Linux.
- The web UI assumes a private network — there is no authentication.
