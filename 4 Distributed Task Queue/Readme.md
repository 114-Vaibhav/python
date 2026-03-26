# 🧵 Distributed Task Queue (Python + Redis)

A lightweight distributed task queue system built using Python and Redis, implementing core concepts like **producer-consumer pattern**, **retry with exponential backoff**, **dead-letter queues**, and **result backend tracking**.

---

## 🚀 Features

- 📥 Producer enqueues tasks with arguments
- ⚙️ Multiple worker processes execute tasks concurrently
- 🔁 Automatic retry mechanism with exponential backoff
- ❌ Dead Letter Queue (DLQ) for permanently failed tasks
- 📊 Result backend using Redis
- 🧾 Simple CLI dashboard to view task results
- 🧠 Function registry for dynamic task execution

---

## 🏗️ Architecture

```
Producer → Redis Queue → Workers → Result Backend
                      ↘ Dead Letter Queue
```

---

## 🛠️ Tech Stack

- Python
- Redis (Message Broker + Result Backend)
- multiprocessing
- JSON serialization

---

## 📂 Project Structure

```
.
├── main.py          # Complete implementation (single file)
├── output.txt       # Sample terminal output
├── README.md
```

---

## ⚙️ Prerequisites

Make sure you have:

- Python 3.x installed
- Redis installed and running

Start Redis server:

```bash
redis-server
```

---

## ▶️ How to Run

```bash
python main.py
```

---

## 🧪 Example Tasks

### 1. Generate Thumbnail

```python
generate_thumbnail(image_id=1504, size=(256,256))
```

### 2. Send Email (with simulated failure)

```python
send_email(to="vg@presidio.com")
```

---

## 🔁 Retry Mechanism

- Uses **exponential backoff**
- Formula:

```
delay = 2 ^ retries
```

Example:

- Retry 1 → 2 sec
- Retry 2 → 4 sec
- Retry 3 → 8 sec

---

## ❌ Dead Letter Queue (DLQ)

- Tasks exceeding max retries are moved to:

```
dead_letter_queue
```

- Helps in debugging and reprocessing failed jobs

---

## 📊 Dashboard Output

Displays:

- Task ID
- Status (SUCCESS / FAILED)
- Retries
- Execution Duration
- Result

---

## 📄 Sample Output

👉 Check `output.txt` for full terminal execution logs.

Example:

```
[WORKER-2] Task FAILED (SMTP Error) — retry 1/3 in 2s
[WORKER-2] Task completed in 6.82s — result: email_sent
```

---

## 🧠 Key Concepts Used

- Producer-Consumer Pattern
- Distributed Systems Basics
- Multiprocessing in Python
- Message Queues
- Exponential Backoff Strategy
- Fault Tolerance using DLQ

---

## ⚠️ Limitations

- Single-file implementation (not modular)
- No task acknowledgment system
- No visibility timeout
- Basic CLI dashboard only

---

## 👨‍💻 Author

**Vaibhav Gupta**

---

## ⭐ If you like this project

Give it a ⭐ on GitHub and feel free to improve it!
