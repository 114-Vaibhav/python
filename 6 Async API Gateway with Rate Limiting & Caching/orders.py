from fastapi import FastAPI

app = FastAPI()

# @app.get("/orders/{id}")
# def get_order(id: int):
#     return {"id": id, "item": "Book"}
@app.get("/orders/{id}")
def get_order(id):
    raise Exception("Forced failure")   # 🔥 ADD THIS