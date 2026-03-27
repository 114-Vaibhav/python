from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse  # 🔥 ADDED
import aiohttp
import time
import redis
import json

# ================================
# REDIS SETUP
# ================================
redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

app = FastAPI()

# ================================
# ROUTES
# ================================
ROUTES = {
    "/api/users": "http://localhost:3001/users",
    "/api/orders": "http://localhost:3002/orders",
    "/api/products": "http://localhost:3003/products"
}

def match_route(path: str):
    for route_prefix in ROUTES:
        if path.startswith(route_prefix):
            return route_prefix, ROUTES[route_prefix]
    return None, None

# ================================
# GLOBAL CONFIG
# ================================
RATE_LIMIT = 5
WINDOW = 60

CACHE_TTL = 60
cache_hits = 0
cache_misses = 0

MAX_FAILURES = 5
OPEN_TIMEOUT = 30

# 🔥 ADDED: SERVICE STATS FOR DASHBOARD
service_stats = {
    "/api/users": {"status": "UP", "latency": "-", "circuit": "CLOSED", "cache_hits": 0},
    "/api/orders": {"status": "UP", "latency": "-", "circuit": "CLOSED", "cache_hits": 0},
    "/api/products": {"status": "UP", "latency": "-", "circuit": "CLOSED", "cache_hits": 0}
}

# ================================
# CIRCUIT BREAKER
# ================================
class CircuitBreaker:
    def __init__(self, service_name):
        self.key = f"circuit:{service_name}"

    def _get_state(self):
        data = redis_client.get(self.key)
        if not data:
            return {"failures": 0, "state": "CLOSED", "last_failure": 0}
        return json.loads(data)

    def _save_state(self, state):
        redis_client.set(self.key, json.dumps(state))

    def before_request(self):
        state = self._get_state()
        now = int(time.time())

        if state["state"] == "OPEN":
            if now - state["last_failure"] < OPEN_TIMEOUT:
                return False, "OPEN"
            else:
                state["state"] = "HALF_OPEN"
                self._save_state(state)
                return True, "HALF_OPEN"

        return True, state["state"]

    def after_request(self, success):
        state = self._get_state()
        now = int(time.time())

        if success:
            state["failures"] = 0
            state["state"] = "CLOSED"
            self._save_state(state)
            return

        state["failures"] += 1
        state["last_failure"] = now

        if state["failures"] >= MAX_FAILURES:
            state["state"] = "OPEN"

        self._save_state(state)

# ================================
# RATE LIMITER
# ================================
def rate_limiter(request: Request):
    client_ip = request.client.host
    key = f"rate_limit:{client_ip}"

    current_count = redis_client.incr(key)

    if current_count == 1:
        redis_client.expire(key, WINDOW)

    if current_count > RATE_LIMIT:
        print(f"[REQ] {request.method} {request.url.path} client={client_ip} → RATE LIMITED ({current_count}/{RATE_LIMIT})")  # 🔥 ADDED
        raise HTTPException(status_code=429, detail="Too many requests")

# ================================
# CACHE
# ================================
def get_cache_key(request: Request):
    return f"cache:{request.method}:{request.url.path}"

def get_from_cache(key: str):
    return redis_client.get(key)

def set_cache(key: str, value: str):
    redis_client.set(key, value, ex=CACHE_TTL)


@app.get("/health")
def health_dashboard():

    print("\n=== Health Dashboard ===")
    print("+------------------+--------+---------+----------+-------------+")
    print("| Service          | Status | Latency | Circuit  | Cache Hits  |")
    print("+------------------+--------+---------+----------+-------------+")

    for service, stats in service_stats.items():
        print(f"| {service:<16} | {stats['status']:<6} | {stats['latency']:<7} | {stats['circuit']:<8} | {stats['cache_hits']:<11} |")

    print("+------------------+--------+---------+----------+-------------+")

    return service_stats



# ================================
# MAIN GATEWAY
# ================================
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway(request: Request, path: str):
    global cache_hits, cache_misses

    # 🔧 FIXED: route match before cache
    route_prefix, base_url = match_route("/" + path)
    if not base_url:
        return {"error": "Route not found"}

    # 1. RATE LIMIT
    rate_limiter(request)

    # 2. CACHE
    cache_key = get_cache_key(request)

    if request.method == "GET":
        cached = get_from_cache(cache_key)

        if cached:
            cache_hits += 1
            service_stats[route_prefix]["cache_hits"] += 1  # 🔥 ADDED

            ttl = redis_client.ttl(cache_key)

            print(f"[REQ] {request.method} {request.url.path} → CACHE HIT (TTL: {ttl}s) — 200 OK")

            return JSONResponse(content={"source": "cache", "data": cached}, status_code=200)

        else:
            cache_misses += 1
            print(f"[REQ] {request.method} {request.url.path} → CACHE MISS")  # 🔥 ADD THIS

    # ================================
    # PROXY LOGIC
    # ================================
    start = time.time()

    remaining_path = request.url.path[len(route_prefix):]
    target_url = base_url + remaining_path

    headers = dict(request.headers)
    body = await request.body()

    cb = CircuitBreaker(route_prefix)
    allowed, state = cb.before_request()

    service_stats[route_prefix]["circuit"] = state  # 🔥 ADDED

    if not allowed:
        print(f"[REQ] {request.method} {request.url.path} → CIRCUIT OPEN ({route_prefix}) — 503")

        return JSONResponse(
            content={"error": "Service temporarily unavailable", "retry_after": 30},
            status_code=503
        )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=request.method,
                url=target_url,
                headers=headers,
                data=body
            ) as response:

                resp_data = await response.text()
                latency = int((time.time() - start) * 1000)

                # 🔥 ADDED: update stats
                service_stats[route_prefix]["latency"] = f"{latency}ms"
                service_stats[route_prefix]["status"] = "UP" if response.status < 500 else "DOWN"

                if response.status >= 500:
                    cb.after_request(False)
                else:
                    cb.after_request(True)

                if request.method == "GET" and response.status == 200:
                    set_cache(cache_key, resp_data)

                print(f"[REQ] {request.method} {request.url.path} → PROXY to {route_prefix} — {response.status} OK in {latency}ms")

                return JSONResponse(
                    content={"status": response.status, "data": resp_data},
                    status_code=response.status
                )

    except Exception as e:
        cb.after_request(False)

        service_stats[route_prefix]["status"] = "DOWN"  # 🔥 ADDED

        print(f"[REQ] {request.method} {request.url.path} → DOWNSTREAM ERROR — 503")

        return JSONResponse(
            content={"error": "Service temporarily unavailable", "retry_after": 30},
            status_code=503
        )

# ================================
# HEALTH DASHBOARD
# ================================
