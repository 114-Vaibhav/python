import json

def fread(filename, order_id):
    with open(filename) as json_file:
        data = json.load(json_file)
        for order in data:
            if order["order_id"] == order_id:
                return order
    return None

def GetOrderSummary(order_id):
    order = fread("readDB.json", order_id)
    if order is None:
        return None
    return order