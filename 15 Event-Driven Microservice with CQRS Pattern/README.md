# Event-Driven Microservice with CQRS Pattern

This project is a simple Python demo of:

- CQRS (Command Query Responsibility Segregation)
- Event Sourcing basics
- Event-driven processing with async handlers
- Read model projection for fast queries

It uses an order workflow to show how commands create events, how those events are stored, and how a separate read model is updated for query operations.

## Project Flow

### Write Side

The write side receives a `PlaceOrderCommand`.

1. The command is handled by `CommandHandler`
2. Past events for that order are loaded from `EventStore`
3. The `Order` aggregate is rebuilt by replaying events
4. New domain events are created:
   - `OrderPlaced`
   - `InventoryReserved`
5. Events are appended to the in-memory event store
6. Events are published through the event bus

### Event Handlers

Subscribed handlers react to published events:

- `log_handler` prints received events
- `handleReadDB` updates the JSON read model
- `notification_handler` simulates sending email
- `analytics_handler` updates total revenue

### Read Side

The read side is separated from the write side.

- `readDB.json` stores a denormalized read model
- `GetOrderSummary()` fetches order data directly from the read model
- Queries do not rebuild aggregate state from events

### Event Replay

The project also demonstrates replaying stored events to reconstruct the `Order` aggregate state. This is the core Event Sourcing idea.

## Project Structure

- [main.py](./main.py) - event store, aggregate, command handler, event bus, and demo execution
- [projections.py](./projections.py) - read model projection and async event handlers
- [read_model.py](./read_model.py) - query helper for the read side
- [readDB.json](./readDB.json) - JSON-based read database
- [Output.txt](./Output.txt) - sample output from running the project

## How to Run

Make sure Python 3 is installed, then run:

```bash
python main.py
```

The script will:

- reset `readDB.json`
- create sample orders
- publish events to handlers
- build/update the read model
- query the read side
- replay events for audit/state reconstruction
- run a few validation tests

## Example Concepts Demonstrated

- Separate write and read models
- Event versioning per aggregate
- Aggregate reconstruction from event history
- Async event publishing with multiple subscribers
- Read model projection into query-friendly storage
- Basic validation on the command side

## Example Events

This demo currently uses:

- `OrderPlaced`
- `InventoryReserved`
- `PaymentProcessed`
- `OrderShipped`
- `OrderDelivered`
- `OrderCancelled`

Note: the current demo execution mainly creates `OrderPlaced` and `InventoryReserved` events, while the projection code is already prepared for additional order lifecycle events.

## Learning Sources

Here are the CQRS and Event Sourcing learning resources referenced for this project:

- https://youtu.be/JTmgi0vO5Ug
- https://youtu.be/vNplj9LwQSw

## Notes

- `EventStore` is in-memory, so events are lost when the program stops
- `readDB.json` acts as a lightweight read database for demonstration
- This is an educational project meant to explain architecture concepts, not a production-ready microservice
