import json
import asyncio

def insertReadDB(order_id, customer_id, items, total,status,placed_at):
    with open("readDB.json", "r") as json_file:
        data = json.load(json_file)
    itm_count =0
    for item in items:
        itm_count += item["qty"]
    data.append({"order_id":order_id,"customer_id":customer_id,"items":items,"item_count":itm_count, "total":total,"status":status,"placed_at":placed_at})
    with open("readDB.json", "w") as json_file:
        json.dump(data, json_file)

def updateReadDB(order_id, customer_id, items, total,status,placed_at):
    with open("readDB.json", "r") as json_file:
        data = json.load(json_file)

        for order in data:
            if order["order_id"] == order_id:
                itm_count =0
                for item in items:
                    itm_count += item["qty"]
                order["customer_id"] = customer_id
                order["items"] = items
                order["item_count"] = itm_count
                order["total"] = total
                order["status"] = status
                order["placed_at"] = placed_at
    with open("readDB.json", "w") as json_file:
        json.dump(data, json_file)

async def handleReadDB(event):
    await asyncio.sleep(1)
    if event.event_type == "OrderPlaced":
        insertReadDB(event.aggregate_id,event.payload["customer_id"],event.payload["items"],event.payload["total"],"PLACED",event.timestamp)
    elif event.event_type == "PaymentProcessed":
        updateReadDB(event.aggregate_id,event.payload["customer_id"],event.payload["items"],event.payload["total"],"PAID",event.timestamp)
    elif event.event_type == "OrderShipped":
        updateReadDB(event.aggregate_id,event.payload["customer_id"],event.payload["items"],event.payload["total"],"SHIPPED",event.timestamp)
    elif event.event_type == "OrderDelivered":
        updateReadDB(event.aggregate_id,event.payload["customer_id"],event.payload["items"],event.payload["total"],"DELIVERED",event.timestamp)
    elif event.event_type == "OrderCancelled":
        updateReadDB(event.aggregate_id,event.payload["customer_id"],event.payload["items"],event.payload["total"],"CANCELLED",event.timestamp)
    elif event.event_type == "InventoryReserved":
        print("InventoryReserved")
    else:
        print("Unknown event type: ", event.event_type)
        raise Exception("Unknown event type")
    

async def notification_handler(event):
    await asyncio.sleep(1)
    if event.event_type == "OrderPlaced":
        print(f"[HANDLER: Notification] Email sent to {event.payload['customer_id']}")


total_revenue = 0
async def analytics_handler(event):
    global total_revenue
    await asyncio.sleep(1)
    if event.event_type == "OrderPlaced":
        total_revenue += event.payload["total"]
        print(f"[HANDLER: Analytics] Revenue updated: {total_revenue}")