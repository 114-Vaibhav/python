from fastapi import FastAPI

app = FastAPI()

@app.get("/products/{id}")
def get_product(id: int):
    return {"id": id, "name": "Laptop"}