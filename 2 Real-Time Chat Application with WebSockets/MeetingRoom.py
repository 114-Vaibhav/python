from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import sqlite3
import logging
logging.basicConfig(level=logging.INFO)
app = FastAPI()

def init_db():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY,
        username TEXT,
        room TEXT,
        message TEXT
    )
    """)

    conn.commit()
    conn.close()

def save_message(username, room, message):
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    c.execute(
        "INSERT INTO messages (username, room, message) VALUES (?, ?, ?)",
        (username, room, message)
    )

    conn.commit()
    conn.close()

init_db()

rooms = {}         
user_map = {}       


async def send_room(room, message):
    for conn in rooms.get(room, []):
        print(conn)
        await conn.send_text(message)


class ConnectionManager:
    def __init__(self):
        self.active_connections = []
        self.room_users = {}   # room -> set(users)

    async def connect(self, websocket: WebSocket, username, room):
        # await websocket.accept()
        self.active_connections.append(websocket)

        if room not in self.room_users:
            self.room_users[room] = set()

        self.room_users[room].add(username)

        await self.broadcast_room_users(room)

    def disconnect(self, websocket: WebSocket, username, room):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

        if room in self.room_users:
            self.room_users[room].discard(username)

    async def broadcast_room_users(self, room):
        users = ", ".join(self.room_users.get(room, []))
        message = f"Online: {users}"
        print(f"Online: {users}")

        for conn in rooms.get(room, []):
            await conn.send_text(message)

manager = ConnectionManager()

# ================= ROUTES =================

@app.get("/")
def get():
    return HTMLResponse(open("templates/index.html").read())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Receive username & room
    await websocket.accept()
    username = await websocket.receive_text()
    room = await websocket.receive_text()

    # Connect user
    await manager.connect(websocket, username, room)

    user_map[username] = websocket

    if room not in rooms:
        rooms[room] = []

    rooms[room].append(websocket)

    print(f'[INFO] {username} joined room #{room}')

    try:
        while True:
            data = await websocket.receive_text()

            # Typing indicator
            if data == "TYPING":
                await send_room(room, f"{username} is typing...")
                print(f"{username} is typing...")
                continue

            # Save message
            save_message(username, room, data)

            # Private message
            if data.startswith("@"):
                target, msg = data.split(" ", 1)
                target = target[1:]

                if target in user_map:
                    await user_map[target].send_text(f"[DM] {username}: {msg}")
                    print(f"[DM] {username}: {msg}")

                    # logging.info(f"[DM] {username}: {msg}")
            else:
                await send_room(room, f"{username}: {data}")
                print(f"{username}: {data}")



    except:
        manager.disconnect(websocket, username, room)

        if room in rooms:
            rooms[room].remove(websocket)

        if username in user_map:
            del user_map[username]

        print(f"[INFO] {username} disconnected")