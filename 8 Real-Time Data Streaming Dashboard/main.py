import asyncio
import random
from fastapi import FastAPI
from fastapi import WebSocket
from datetime import datetime

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = {
            "sensor_id": "T1",
            "temp": round(random.uniform(60, 110), 2),
            "vibration": round(random.uniform(0.1, 0.6), 2),
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        await websocket.send_json(data)
        await asyncio.sleep(1)
