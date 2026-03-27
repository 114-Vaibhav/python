import redis

# Connect to Redis (adjust host/port if different)
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Clear all keys in the current database
redis_client.flushdb()  # clears only the selected DB
# or use flushall() to clear all databases
# redis_client.flushall()

print("Cache cleared successfully!")

