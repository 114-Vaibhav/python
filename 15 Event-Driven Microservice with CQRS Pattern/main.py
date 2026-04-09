import uuid 
from datetime import datetime
from read_model import GetOrderSummary
from projections import handleReadDB, notification_handler, analytics_handler
import json
import asyncio
import inspect

class Event:
    def __init__(self, event_id, aggregate_id, event_type, payload, timestamp, version):
        self.event_id = event_id
        self.aggregate_id = aggregate_id
        self.event_type = event_type
        self.payload = payload
        self.timestamp = timestamp
        self.version = version

class EventStore:
    def __init__(self):
        self.events = []
    
    def append(self, event):
        # assign version automatically
        existing_events = self.getEvents(event.aggregate_id)
        event.version = len(existing_events) + 1
        self.events.append(event)
        print(f"[EVENT STORE] Appended {event.event_type} v{event.version}")

    def getEvents(self, aggregate_id):
        return [event for event in self.events if event.aggregate_id == aggregate_id]

class Order:
    def __init__(self):
        self.order_id = None
        self.customer_id = None
        self.items = None
        self.order_status = None
        self.total = None

    def applyEvent(self, event):
        if event.event_type == "OrderPlaced":
            self.order_id = event.aggregate_id
            self.customer_id = event.payload["customer_id"]
            self.items = event.payload["items"]
            self.total = event.payload["total"]
            self.order_status = "PLACED"

        elif event.event_type == "PaymentProcessed":
            self.order_status = "PAID"

        elif event.event_type == "OrderShipped":
            self.order_status = "SHIPPED"

        elif event.event_type == "OrderDelivered":
            self.order_status = "DELIVERED"

        elif event.event_type == "OrderCancelled":
            self.order_status = "CANCELLED"

    def replay(self, events):
        events = sorted(events, key=lambda e: e.version)
        for event in events:
            self.applyEvent(event)

    def place_order(self, order_id, customer_id, items, total):
        if self.order_status is not None:
            raise Exception("Order already exists")

        if not items:
            raise Exception("Order must have at least one item")

        if total <= 0:
            raise Exception("Total must be positive")

        events = []

        events.append(Event(
            event_id=uuid.uuid4(),
            aggregate_id=order_id,
            event_type="OrderPlaced",
            payload={
                "customer_id": customer_id,
                "items": items,
                "total": total
            },
            timestamp = datetime.now().isoformat(),
            version=None
        ))

        for item in items:
            events.append(Event(
                event_id=uuid.uuid4(),
                aggregate_id=order_id,
                event_type="InventoryReserved",
                payload={
                    "sku": item["sku"],
                    "qty": item["qty"]
                },
                timestamp = datetime.now().isoformat(),
                version=None
            ))

        return events

class PlaceOrderCommand:
    def __init__(self, order_id, customer_id, items, total):
        self.aggregate_id = order_id
        self.customer_id = customer_id
        self.items = items
        self.total = total

class EventBus:
    def __init__(self):
        self.handlers = []

    def subscribe(self, handler):
        self.handlers.append(handler)

    async def publish(self, event):
        print(f"[BUS] Published {event.event_type}")
        
        tasks = []

        for handler in self.handlers:
            if inspect.iscoroutinefunction(handler):
                tasks.append(handler(event))   # ✅ coroutine
            else:
                handler(event)                # ✅ run sync directly

        if tasks:
            await asyncio.gather(*tasks)      # ✅ only async handlers

def log_handler(event):
    print(f"[HANDLER] Received {event.event_type}")

class CommandHandler:
    def __init__(self, event_store, event_bus):
        self.event_store = event_store
        self.event_bus = event_bus
        
    async def handle(self, command):   # ✅ make async
        print("[WRITE] Command Received", command)

        if not hasattr(command, "aggregate_id"):
            raise Exception("Invalid command")
        
        events = self.event_store.getEvents(command.aggregate_id)
        print(f"[LOAD] Loaded {len(events)} events")

        order = Order()
        order.replay(events)

        if isinstance(command, PlaceOrderCommand):
            new_events = order.place_order(
                command.aggregate_id,
                command.customer_id,
                command.items,
                command.total
            )
        else:
            raise Exception("Unknown command")

        # apply new events
        for event in new_events:
            order.applyEvent(event)

        # store
        for event in new_events:
            self.event_store.append(event)

        # publish (async properly)
        for event in new_events:
            await self.event_bus.publish(event)   # ✅ correct

async def main():
    
    with open("readDB.json", "w") as f:
        f.write("[]")

    event_store = EventStore()
    event_bus = EventBus()

   
    event_bus.subscribe(log_handler)
    event_bus.subscribe(handleReadDB)
    event_bus.subscribe(notification_handler)
    event_bus.subscribe(analytics_handler)

    command_handler = CommandHandler(event_store, event_bus)

    print("\n================ COMMAND SIDE (WRITE) ================\n")

    print(">>> Dispatching PlaceOrderCommand...\n")

    await command_handler.handle(
        PlaceOrderCommand(
            "ORD-1001",
            "vsg",
            [
                {"sku": "WID-01", "qty": 3},
                {"sku": "GAD-05", "qty": 4}
            ],
            239.96
        )
    )

    print("\n[WRITE] Order created successfully")
    print("[BUS] Events published to subscribers")

    print("\n================ EVENT HANDLERS (ASYNC) ================\n")
    print("Processing projections, notifications, analytics...\n")

    
    await asyncio.sleep(2)

    print("\n================ QUERY SIDE (READ) ================\n")

    print('>>> GetOrderSummary("ORD-1001")\n')

    result = GetOrderSummary("ORD-1001")

    if result:
        print(result)
    else:
        print("Order not found")

    print("\nResponse time: ~1-5 ms (denormalized read model)")

    print("\n================ EVENT REPLAY (AUDIT) ================\n")

    events = event_store.getEvents("ORD-1001")

    for i, e in enumerate(events, start=1):
        print(f"[Event #{i}] {e.event_type} @ {e.timestamp}")

    print("\nReplaying events to reconstruct state...\n")

    order = Order()
    order.replay(events)

    total_items = sum(item["qty"] for item in order.items)

    print("Reconstructed State:")
    print(f"Order(id={order.order_id}, status={order.order_status}, total={order.total}, items={total_items})")

    print("\n================ EXTENDED TESTS ================\n")

    print("\n--- TEST 1: Place Order Successfully ---")
    await command_handler.handle(
        PlaceOrderCommand(
            "order-1",
            "customer-1",
            [
                {"sku": "item-1", "qty": 2},
                {"sku": "item-2", "qty": 1}
            ],
            100
        )
    )

    print("\n--- TEST 2: Replay Order State ---")
    events = event_store.getEvents("order-1")
    order = Order()
    order.replay(events)
    print("Order Status after replay:", order.order_status)

    print("\n--- TEST 3: Duplicate Order (Should Fail) ---")
    try:
        await command_handler.handle(
            PlaceOrderCommand(
                "order-1",
                "customer-1",
                [{"sku": "item-3", "qty": 1}],
                50
            )
        )
    except Exception as e:
        print("Expected Error:", e)

    print("\n--- TEST 4: Invalid Order (No Items) ---")
    try:
        await command_handler.handle(
            PlaceOrderCommand(
                "order-3",
                "customer-1",
                [],
                50
            )
        )
    except Exception as e:
        print("Expected Error:", e)

    print("\n--- TEST 5: Invalid Order (Negative Total) ---")
    try:
        await command_handler.handle(
            PlaceOrderCommand(
                "order-4",
                "customer-1",
                [{"sku": "item-1", "qty": 1}],
                -10
            )
        )
    except Exception as e:
        print("Expected Error:", e)

    print("\n--- TEST 6: Multiple Orders ---")
    await command_handler.handle(
        PlaceOrderCommand(
            "order-2",
            "customer-1",
            [
                {"sku": "item-12", "qty": 2},
                {"sku": "item-2", "qty": 1}
            ],
            100
        )
    )

    print("\n--- TEST 7: Check Event Versions ---")
    events = event_store.getEvents("order-2")
    for e in events:
        print(f"{e.event_type} -> version {e.version}")

    print("\n--- TEST 8: Full Event Store Dump ---")
    for e in event_store.events:
        print(e.aggregate_id, e.event_type, e.version)

    print("\n--- TEST 9: Check Read DB ---")
    with open("readDB.json", "r") as json_file:
        data = json.load(json_file)
    print(data)

    print("\n--- TEST 10: Check Order Summary ---")
    order_summary = GetOrderSummary("order-2")
    print(order_summary)

    print("\n--- TEST 11: Check Order Summary for Order 1 ---")
    order_summary = GetOrderSummary("order-1")
    if order_summary is None:
        print("Order not found")
    else:
        print(order_summary)



if __name__ == "__main__":
    asyncio.run(main())
