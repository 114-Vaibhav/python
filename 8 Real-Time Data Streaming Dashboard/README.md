# Real-Time Data Streaming Dashboard

A simple real-time monitoring dashboard built with FastAPI, WebSockets, and Chart.js. The project simulates live sensor readings and streams them to a browser interface, where temperature and vibration data are displayed as live charts with alert notifications.

## Features

- Streams live sensor data over a WebSocket connection
- Displays current temperature and vibration readings
- Plots temperature and vibration values in real time
- Shows alert notifications when thresholds are exceeded
- Uses a lightweight frontend with CDN-based libraries

## Tech Stack

- Backend: Python, FastAPI, WebSockets
- Frontend: HTML, JavaScript
- Charts: Chart.js
- Styling: Tailwind CSS
- Notifications: Notyf

## Project Structure

```text
.
|-- index.html
|-- script.js
|-- main.py
|-- Output.webm
```

## How It Works

The backend in `main.py` starts a FastAPI application with a WebSocket endpoint at `/ws`.

Every second, the server sends a JSON payload containing:

- `sensor_id`
- `temp`
- `vibration`
- `timestamp`

The frontend in `script.js` connects to `ws://localhost:8000/ws`, receives incoming readings, updates the live text display, redraws both charts, and triggers notifications when:

- Temperature is greater than `100 F`
- Vibration is greater than `0.5`

## Setup

### 1. Install Python dependencies

Install the required backend packages:

```bash
pip install fastapi uvicorn
```

### 2. Start the backend server

Run the FastAPI app with Uvicorn:

```bash
uvicorn main:app --reload
```

The WebSocket server will be available at:

```text
ws://localhost:8000/ws
```

### 3. Open the frontend

Open `index.html` in your browser.

If your browser blocks local file behavior, serve the folder with a simple static server instead, for example:

```bash
python -m http.server 5500
```

Then open:

```text
http://localhost:5500
```

## Sample Data Format

```json
{
  "sensor_id": "T1",
  "temp": 97.42,
  "vibration": 0.31,
  "timestamp": "14:25:09"
}
```

## Notes

- Sensor values are randomly generated for demonstration purposes.
- Frontend libraries are loaded through CDNs, so an internet connection is needed for the UI assets unless they are downloaded locally.
- The project currently focuses on simulated streaming rather than persistent storage or historical analytics.

## Possible Improvements

- Add a requirements file
- Add multiple sensor streams
- Persist readings to a database
- Support configurable alert thresholds
- Deploy the frontend and backend together
- Add reconnect handling for WebSocket failures

## Demo Asset

- `Output.webm` appears to be a screen recording/demo of the project

## Author

Built as a real-time data streaming dashboard project for learning and demonstration.
