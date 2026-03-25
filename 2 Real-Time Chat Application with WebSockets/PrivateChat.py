from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

print("------------Private Chat--------------")
app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/")
def get():
    return HTMLResponse(open("templates/index.html").read())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    username = await websocket.receive_text()

    print(f'[INFO] User "{username}" connected')

    try:
        while True:
            data = await websocket.receive_text()
            message = f"{username}: {data}"
            print(message)
            await manager.broadcast(message)

    except:
        manager.disconnect(websocket)
        print(f'[INFO] {username} disconnected')