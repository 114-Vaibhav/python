# Real-Time Chat Application with WebSockets

This project is the second application in the repository PYTHON. It is a real-time chat system built with **FastAPI**, **WebSockets**, **HTML**, and **Tailwind CSS**.

The project includes two chat modes:

1. `PrivateChat.py`
   A simple real-time chat for two individual users.
2. `MeetingRoom.py`
   A room-based chat application where multiple users can join the same room, view online members, send messages, and use private messaging with `@username`.

## Project Folder

`2 Real-Time Chat Application with WebSockets`

## Files

- `PrivateChat.py`  
  Runs a basic chat server for direct conversation between two users.

- `MeetingRoom.py`  
  Runs a meeting-room style chat server with:
  - room joining
  - online user list
  - typing indicator
  - message storage using SQLite
  - private messages using `@username`

- `templates/index.html`  
  Frontend interface for entering username, room name, and sending messages.

- `chat.db`  
  SQLite database used by `MeetingRoom.py` to store chat messages.

- `Output.txt`  
  Contains terminal output showing server logs, user joins, typing activity, messages, and disconnect events.

- `Output.pdf`  
  Contains UI screenshots/output of the chat application.

- `Learning/`  
  Contains practice code, experiments, and article shortcuts used while learning FastAPI and WebSockets for this project.

## Features

### Private Chat

- Real-time communication using WebSockets
- Two users can chat instantly in the browser
- Server logs user connection and disconnection events
- Messages are broadcast live to connected users

### Meeting Room Chat

- Users can join a room with a username
- Online users are displayed in the chat UI
- Typing notifications are shown in real time
- Messages are saved in SQLite database
- Multiple users can chat in the same room
- Private messages can be sent using:

```text
@username your message
```

## Technologies Used

- Python
- FastAPI
- Uvicorn
- WebSockets
- SQLite
- HTML
- Tailwind CSS

## How to Run

Open a terminal inside:

```powershell
cd "2 Real-Time Chat Application with WebSockets"
```

### Run Private Chat

```powershell
uvicorn PrivateChat:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

Open the page in two browser tabs or two browser windows and chat using different usernames.

### Run Meeting Room Chat

```powershell
uvicorn MeetingRoom:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

Enter:

- your username
- room name such as `meetingRoom`

Then join and start chatting.

## Example Workflow

### Private Chat

- User 1 opens the app and enters a username
- User 2 opens the app in another tab/window
- Both users send messages in real time

### Meeting Room

- Ram joins `meetingRoom`
- Isha joins the same room
- Vaibhav joins later
- Users can see online members
- Users exchange messages and typing updates
- Users can also send direct messages with `@username`

## Output Reference

- Terminal execution logs are available in `2 Real-Time Chat Application with WebSockets/Output.txt`
- UI screenshots/output are available in `2 Real-Time Chat Application with WebSockets/Output.pdf`

## Learning References

The `Learning` folder contains the material used while building and understanding this project. It includes sample code, templates, and article shortcuts for reference.

Articles used:

- Better Stack: FastAPI WebSockets  
  `https://betterstack.com/community/guides/scaling-python/fastapi-websockets/`

- GeeksforGeeks: Simple Chat Application Using WebSockets with FastAPI  
  `https://www.geeksforgeeks.org/python/simple-chat-application-using-websockets-with-fastapi/`

- GeeksforGeeks: How to Use WebSocket with FastAPI  
  `https://www.geeksforgeeks.org/python/how-to-use-websocket-with-fastapi/`

## Learning Outcome

This project demonstrates:

- how WebSockets enable full-duplex real-time communication
- how FastAPI handles WebSocket routes
- how to manage multiple users and rooms
- how to store chat messages in SQLite
- how to build a simple browser-based chat interface
