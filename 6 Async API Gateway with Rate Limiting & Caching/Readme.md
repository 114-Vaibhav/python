# 🚀 Distributed API Gateway (Python + FastAPI + Redis)

A production-style **Reverse Proxy API Gateway** built using Python that routes requests to multiple microservices while implementing advanced backend concepts like:

- ⚡ Token Bucket Rate Limiting
- 🧠 Redis-based Response Caching (TTL)
- 🔁 Circuit Breaker Pattern
- 📊 Health Monitoring Dashboard

---

## 🏗️ Architecture

```text
Client → API Gateway → Microservices
                 ↘ Redis (Cache + Rate Limit + Circuit State)
                 ↘ Health Dashboard
```

---

## 🚀 Features

### 🔹 Reverse Proxy Routing

- Single entry point for all APIs
- Routes requests dynamically:

  ```
  /api/users/**    → user-service
  /api/orders/**   → order-service
  /api/products/** → product-service
  ```

---

### 🔹 Rate Limiting (Token Bucket)

- Per-client request limiting
- Example: **50 requests/minute**
- Prevents abuse and overload

---

### 🔹 Redis Caching (TTL)

- Caches **GET responses**
- Reduces latency significantly
- TTL-based expiration

Example:

```
CACHE HIT (TTL: 45s)
CACHE MISS → PROXY
```

---

### 🔹 Circuit Breaker

- Detects failing services
- Opens circuit after **5 failures**
- Returns fallback response

States:

- `CLOSED` → normal
- `OPEN` → blocked
- `HALF_OPEN` → recovery testing

---

### 🔹 Health Dashboard

- Real-time system monitoring
- Displays:
  - Service status
  - Latency
  - Circuit state
  - Cache hits

---

## 🛠️ Tech Stack

- Python
- FastAPI
- Redis
- aiohttp
- Async Programming (`async/await`)

---

## 📂 Project Structure

```bash
.
├── main.py               # API Gateway (core logic)
├── users.py      # User microservice
├── orders.py     # Order microservice
├── products.py   # Product microservice
├── output.txt           # Sample terminal output
├── clearCache.py        # Clear Redis cache
├── README.md

```

---

## ⚙️ Setup Instructions

### 1️⃣ Install Dependencies

```bash
pip install fastapi uvicorn aiohttp redis
```

---

### 2️⃣ Start Redis

```bash
redis-server
```

---

### 3️⃣ Run Microservices

```bash
uvicorn user_service:app --port 3001
uvicorn order_service:app --port 3002
uvicorn product_service:app --port 3003
```

---

### 4️⃣ Run API Gateway

```bash
uvicorn main:app --reload
```

---

## ▶️ Usage

### 🔹 Access Gateway

```
http://localhost:8000/api/products/1
http://localhost:8000/api/users/55
http://localhost:8000/api/orders/43

Refresh pages to get Cache Hit, Rate Limit, and Circuit Breaker responses
```

---

### 🔹 Health Dashboard

```
http://localhost:8000/health
```

---

## 🧪 Example Logs

```
[REQ] GET /api/products/42 → CACHE HIT (TTL: 45s) — 200 OK

[REQ] GET /api/orders/latest → PROXY to /api/orders — 200 OK in 134ms

[REQ] POST /api/users/signup client=127.0.0.1
→ RATE LIMITED (52/50 req/min) — 429

[REQ] GET /api/orders/7891
→ CIRCUIT OPEN (/api/orders) — 503
```

---

## 📊 Health Dashboard Output

```
+------------------+--------+---------+----------+-------------+
| Service          | Status | Latency | Circuit  | Cache Hits  |
+------------------+--------+---------+----------+-------------+
| /api/users       | UP     | 89ms    | CLOSED   | 12          |
| /api/orders      | DOWN   | timeout | OPEN     | 3           |
| /api/products    | UP     | 45ms    | CLOSED   | 25          |
+------------------+--------+---------+----------+-------------+
```

---

## ⚠️ Important Notes

- Cache applies only to **GET requests**
- Rate limiting is based on **client IP**
- Circuit breaker prevents repeated failures
- Redis must be running before starting

---

## 🔮 Future Improvements

- 🌐 Web-based dashboard (React + Charts)
- 🔐 API Key authentication system
- 📌 Priority routing / load balancing
- ⏱️ Request timeout handling
- 📈 Prometheus + Grafana monitoring

---

## 🧠 Concepts Used

- Reverse Proxy
- Token Bucket Algorithm
- Circuit Breaker Pattern
- Middleware Design Pattern
- Async Programming
- Distributed Systems

---

## 👨‍💻 Author

**Vaibhav Gupta**

---

## ⭐ If you like this project

Give it a ⭐ on GitHub and feel free to improve it!
